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
import traceback

#Clean the shell
import os
os.system(['clear','cls'][os.name == 'nt'])

# get new object
p = ISO8583()
#some string describing the transation type
transation = "200"
print ('Setting transation type to %s' % transation)
p.setTransationType(transation)
# Is the same that:
#p.setMTI(transation)

#Some tests and 
print ('Setting bits')

p.setBit(3,"100000")
p.setBit(4,1200)
p.setBit(7,"1207231505")
p.setBit(11,12)
p.setBit(12,"231505")
p.setBit(13,1207)
p.setBit(32,"01020000000")
p.setBit(40,"002")
p.setBit(41,"98765432")
p.setBit(42,"303500098765432")
p.setBit(49,986)
p.setBit(62,"PP16814995840013560000")
p.setBit(63,"00000105")
try:
	p.setBit(126,"00000000000000105")
except ValueToLarge:
	print ('\t\tSomething happening!!!! The Exception! So, bit 126 is not set!!!!')
	#if want more information ...
	#traceback.print_exc()

#show hex bitmap
print ('Bitmap in HEX')
p.showBitmap()

#Show bits
print ('Bits with values')
p.showIsoBits()

# Show raw ASCII ISO
print ('The package is -> ')
p.showRawIso()

# Getting bits...
print ('\n\n\n------------------------------------------\n')

print ('Getting bits')
try:
	print ('Bit 7 is there? %s' % p.getBit(7))
	print ('Bit 32 is there? %s' % p.getBit(32))
except:
	print ('Something is bad...')
	
# Testing exceptions...	
try:
	print ('Bit 45 is there? %s' % p.getBit(45))
except:
	print ("No, this bit is not there :)")	

try:
	print ('Bit 27 is there? %s' % p.getBit(27))
except BitNotSet as bns:
	print(bns)
	

#More exceptions...	
print ('\n\n\n------------------------------------------\n')
print ('Exceptions....')

iso = ISO8583()
try:
	iso.setMTI('0800')
	iso.setBit(2,2)
	iso.setBit(4,4)
	iso.setBit(12,12)
	iso.setBit(21,21)
	iso.setBit(17,17)
	iso.setBit(49,9861) # this bit is wrong ...
	iso.setBit(99,99)
except ValueToLarge as e:
		print ('Value too large :( %s' % e)
except InvalidMTI as i:
		print ('This MTI is wrong :( %s' % i)




