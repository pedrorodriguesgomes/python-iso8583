"""

(C) Copyright 2009 Igor V. Custodio

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

from ISO8583.ISO8583 import ISO8583
from ISO8583.ISOErrors import *
import socket
import sys
import time

# Configure the client
serverIP = "127.0.0.1"
serverPort = 7777
numberEcho = 5
timeBetweenEcho = 5  # in seconds

bigEndian = True
# bigEndian = False

s = None
for res in socket.getaddrinfo(serverIP, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        s = None
        continue
    try:
        s.connect(sa)
    except socket.error as msg:
        s.close()
        s = None
        continue
    break
if s is None:
    print('Could not connect :(')
    sys.exit(1)

for req in range(0, numberEcho):
    iso = ISO8583()
    iso.setMTI('0800')
    iso.setBit(3, '300000')
    iso.setBit(24, '045')
    iso.setBit(41, '11111111')
    iso.setBit(42, '222222222222222')
    iso.setBit(63, 'This is a Test Message')
    if bigEndian:
        try:
            message = iso.getNetworkISO()
            s.send(message)
            print('Sending ... %s' % message)
            ans = s.recv(2048).decode()
            print("\nInput ASCII |%s|" % ans)
            isoAns = ISO8583()
            isoAns.setNetworkISO(ans)
            v1 = isoAns.getBitsAndValues()
            for v in v1:
                print('Bit %s of type %s with value = %s' % (v['bit'], v['type'], v['value']))

            if isoAns.getMTI() == '0810':
                print("\tThat's great !!! The server understand my message !!!")
            else:
                print("The server dosen't understand my message!")

        except InvalidIso8583 as ii:
            print(ii)
            break

        time.sleep(timeBetweenEcho)

    else:
        try:
            message = iso.getNetworkISO(False)
            s.send(message)
            print('Sending ... %s' % message)
            ans = s.recv(2048)
            print("\nInput ASCII |%s|" % ans)
            isoAns = ISO8583()
            isoAns.setNetworkISO(ans, False)
            v1 = isoAns.getBitsAndValues()
            for v in v1:
                print('Bit %s of type %s with value = %s' % (v['bit'], v['type'], v['value']))

            if isoAns.getMTI() == '0810':
                print("\tThat's great !!! The server understand my message !!!")
            else:
                print("The server dosen't understand my message!")

        except InvalidIso8583 as ii:
            print(ii)
            break

        time.sleep(timeBetweenEcho)

print('Closing...')
s.close()
