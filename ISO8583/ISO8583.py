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

__author__ = 'Igor Vitorio Custodio <igorvc@vulcanno.com.br>'
__version__ = '1.4'
__licence__ = 'GPL V3'

import sys
if sys.version_info >= (3,):
    from ISO8583.ISOErrors import *
else:
    from ISOErrors import *
import struct
import binascii
import ebcdic
import time

class ISO8583:
    """Main Class to work with ISO8583 packages.
    Used to create, change, send, receive, parse or work with ISO8593 Package version 1987.
    It's 100% Python :)
    Enjoy it!
    Thanks to: Vulcanno IT Solutions <http://www.vulcanno.com.br>
    Licence: GPL Version 3
    More information: http://code.google.com/p/iso8583py/

    Example:
        from ISO8583.ISO8583 import ISO8583
        from ISO8583.ISOErrors import *

        iso = ISO8583()
        try:
            iso.setMTI('0800')
            iso.setBit(2,2)
            iso.setBit(4,4)
            iso.setBit(12,12)
            iso.setBit(21,21)
            iso.setBit(17,17)
            iso.setBit(49,986)
            iso.setBit(99,99)
        except ValueTooLarge, e:
                print ('Value too large :( %s' % e)
        except InvalidMTI, i:
                print ('This MTI is wrong :( %s' % i)

        print ('The Message Type Indication is = %s' %iso.getMTI())

        print ('The Bitmap is = %s' %iso.getBitmap())
        iso.showIsoBits();
        print ('This is the ISO8583 complete package %s' % iso.getRawIso())
        print ('This is the ISO8583 complete package to sent over the TCPIP network %s' % iso.getNetworkISO())

"""
    # Attributes
    # Bits to be set 00000000 -> _BIT_POSITION_1 ... _BIT_POSITION_8
    _BIT_POSITION_1 = 128  # 10 00 00 00
    _BIT_POSITION_2 = 64  # 01 00 00 00
    _BIT_POSITION_3 = 32  # 00 10 00 00
    _BIT_POSITION_4 = 16  # 00 01 00 00
    _BIT_POSITION_5 = 8  # 00 00 10 00
    _BIT_POSITION_6 = 4  # 00 00 01 00
    _BIT_POSITION_7 = 2  # 00 00 00 10
    _BIT_POSITION_8 = 1  # 00 00 00 01

    # Array to translate bit to position
    _TMP = [0, _BIT_POSITION_8, _BIT_POSITION_1, _BIT_POSITION_2, _BIT_POSITION_3, _BIT_POSITION_4, _BIT_POSITION_5,
            _BIT_POSITION_6, _BIT_POSITION_7]
    _BIT_DEFAULT_VALUE = 0

    # ISO8583 constants
    _BITS_VALUE_TYPE = {}
    # Every _BITS_VALUE_TYPE has:
    # _BITS_VALUE_TYPE[N] = [ X, Y, Z, W, K, L ]
    # N = bitnumber
    # X = smallStr representation of the bit meaning
    # Y = large str representation
    # Z = type of the bit (B, N, A, AN, ANS, LL, LLL, LLLLLL)
    # V = format of indicator length indicator LL, LLL, etc (-, A[scii], B[CD])
    # W = size of the information that N need to has
    # K = type of values a, an, n, ans, b
    # L = format of the data (A[scii], E[bcdic], P[acked])
    _BITS_VALUE_TYPE[1] = ['BME', 'Bit Map Extended', 'B', '-', 16, 'b', 'A']
    _BITS_VALUE_TYPE[2] = ['2', 'Primary account number (PAN)', 'LL', 'A', 19, 'n', 'A']
    _BITS_VALUE_TYPE[3] = ['3', 'Processing code', 'N', '-', 6, 'n', 'A']
    _BITS_VALUE_TYPE[4] = ['4', 'Amount transaction', 'N', '-', 12, 'n', 'A']
    _BITS_VALUE_TYPE[5] = ['5', 'Amount reconciliation', 'N', '-', 12, 'n', 'A']
    _BITS_VALUE_TYPE[6] = ['6', 'Amount cardholder billing', 'N', '-', 12, 'n', 'A']
    _BITS_VALUE_TYPE[7] = ['7', 'Date and time transmission', 'N', '-', 10, 'n', 'A']
    _BITS_VALUE_TYPE[8] = ['8', 'Amount cardholder billing fee', 'N', '-', 8, 'n', 'A']
    _BITS_VALUE_TYPE[9] = ['9', 'Conversion rate reconciliation', 'N', '-', 8, 'n', 'A']
    _BITS_VALUE_TYPE[10] = [
        '10', 'Conversion rate cardholder billing', 'N', '-', 8, 'n', 'A']
    _BITS_VALUE_TYPE[11] = ['11', 'Systems trace audit number', 'N', '-', 6, 'n', 'A']
    _BITS_VALUE_TYPE[12] = [
        '12', 'Time local transaction', 'N', '-', 6, 'n', 'A']
    _BITS_VALUE_TYPE[13] = ['13', 'Date local transaction', 'N', '-', 4, 'n', 'A']
    _BITS_VALUE_TYPE[14] = ['14', 'Date expiration', 'N', '-', 4, 'n', 'A']
    _BITS_VALUE_TYPE[15] = ['15', 'Date settlement', 'N', '-', 4, 'n', 'A']
    _BITS_VALUE_TYPE[16] = ['16', 'Date conversion', 'N', '-', 4, 'n', 'A']
    _BITS_VALUE_TYPE[17] = ['17', 'Date capture', 'N', '-', 4, 'n', 'A']
    _BITS_VALUE_TYPE[18] = ['18', 'Merchant Type', 'N', '-', 4, 'n', 'A']
    _BITS_VALUE_TYPE[19] = [
        '19', 'Country code acquiring institution', 'N', '-', 3, 'n', 'A']
    _BITS_VALUE_TYPE[20] = [
        '20', 'Country code primary account number (PAN)', 'N', '-', 3, 'n', 'A']
    _BITS_VALUE_TYPE[21] = [
        '21', 'Forwarding Institution Country Code', 'N', '-', 3, 'n', 'A']
    _BITS_VALUE_TYPE[22] = ['22', 'POS Entry Mode', 'N', '-', 3, 'n', 'A']
    _BITS_VALUE_TYPE[23] = ['23', 'Card sequence number', 'N', '-', 3, 'n', 'A']
    _BITS_VALUE_TYPE[24] = ['24', 'Function code', 'N', '-', 3, 'n', 'A']
    _BITS_VALUE_TYPE[25] = ['25', 'POS condition code', 'N', '-', 2, 'n', 'A']
    _BITS_VALUE_TYPE[26] = ['26', 'POS PIN Capture Code', 'N', '-', 2, 'n', 'A']
    _BITS_VALUE_TYPE[27] = ['27', 'Auth ID Response Length', 'N', '-', 1, 'n', 'A']
    _BITS_VALUE_TYPE[28] = ['28', 'Amount, Txn Fee', 'N', '-', 8, 'n', 'A']
    _BITS_VALUE_TYPE[29] = ['29', 'Amount, Reconciliation Fee', 'N', '-', 8, 'n', 'A']
    _BITS_VALUE_TYPE[30] = ['30', 'Amount, Txn Processing Fee', 'N', '-', 8, 'n', 'A']
    _BITS_VALUE_TYPE[31] = ['31', 'Amount, Settlement Processing Fee', 'N', '-', 8, 'n', 'A']
    _BITS_VALUE_TYPE[32] = [
        '32', 'Acquiring institution identification code', 'LL', 'A', 11, 'n', 'A']
    _BITS_VALUE_TYPE[33] = [
        '33', 'Forwarding institution identification code', 'LL', 'A', 11, 'n', 'A']
    _BITS_VALUE_TYPE[34] = ['34', 'Primary Account Number, extended', 'LL', 'A', 28, 'n', 'A']
    _BITS_VALUE_TYPE[35] = ['35', 'Track 2 data', 'LL', 'A', 37, 'n', 'A']
    _BITS_VALUE_TYPE[36] = ['36', 'Track 3 data', 'LLL', 'A', 104, 'n', 'A']
    _BITS_VALUE_TYPE[37] = ['37', 'Retrieval reference number', 'N', '-', 12, 'an', 'A']
    _BITS_VALUE_TYPE[38] = ['38', 'Approval code', 'N', '-', 6, 'an', 'A']
    _BITS_VALUE_TYPE[39] = ['39', 'Response code', 'A', '-', 2, 'an', 'A']
    _BITS_VALUE_TYPE[40] = ['40', 'Service restriction code', 'N', '-', 3, 'an', 'A']
    _BITS_VALUE_TYPE[41] = [
        '41', 'Card acceptor terminal identification', 'N', '-', 8, 'ans', 'A']
    _BITS_VALUE_TYPE[42] = [
        '42', 'Card acceptor identification code', 'A', '-', 15, 'ans', 'A']
    _BITS_VALUE_TYPE[43] = [
        '43', 'Card acceptor name/location', 'A', '-', 40, 'ans', 'A']
    _BITS_VALUE_TYPE[44] = ['44', 'Additional response data', 'LL', 'A', 25, 'an', 'A']
    _BITS_VALUE_TYPE[45] = ['45', 'Track 1 data', 'LL', 'A', 76, 'an', 'A']
    _BITS_VALUE_TYPE[46] = ['46', 'Amounts fees', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[47] = ['47', 'Additional data national', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[48] = ['48', 'Additional data private', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[49] = ['49', 'Currency code, transaction', 'AN', '-', 3, 'an', 'A']
    _BITS_VALUE_TYPE[50] = ['50', 'Currency code, settlement', 'AN', '-', 3, 'an', 'A']
    _BITS_VALUE_TYPE[51] = [
        '51', 'Currency code, cardholder billing', 'AN', '-', 3, 'an', 'A']
    _BITS_VALUE_TYPE[52] = [
        '52', 'Personal identification number (PIN) data', 'B', '-', 16, 'b', 'A']
    _BITS_VALUE_TYPE[53] = [
        '53', 'Security related control information', 'LL', 'A', 16, 'n', 'A']
    _BITS_VALUE_TYPE[54] = ['54', 'Amounts additional', 'LLL', 'A', 120, 'an', 'A']
    _BITS_VALUE_TYPE[55] = [
        '55', 'Integrated circuit card (ICC) system related data', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[56] = ['56', 'Original data elements', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[57] = [
        '57', 'Authorisation life cycle code', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[58] = [
        '58', 'Authorising agent institution identification code', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[59] = ['59', 'Transport data', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[60] = ['60', 'Reserved for national use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[61] = [
        '61', 'Reserved for national use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[62] = [
        '62', 'Reserved for private use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[63] = [
        '63', 'Reserved for private use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[64] = [
        '64', 'Message authentication code (MAC) field', 'B', '-', 16, 'b', 'A']
    _BITS_VALUE_TYPE[65] = ['65', 'Bitmap tertiary', 'B', '-', 16, 'b', 'A']
    _BITS_VALUE_TYPE[66] = ['66', 'Settlement code', 'N', '-', 1, 'n', 'A']
    _BITS_VALUE_TYPE[67] = ['67', 'Extended payment data', 'N', '-', 2, 'n', 'A']
    _BITS_VALUE_TYPE[68] = [
        '68', 'Receiving institution country code', 'N', '-', 3, 'n', 'A']
    _BITS_VALUE_TYPE[69] = [
        '69', 'Settlement institution county code', 'N', '-', 3, 'n', 'A']
    _BITS_VALUE_TYPE[70] = [
        '70', 'Network management Information code', 'N', '-', 3, 'n', 'A']
    _BITS_VALUE_TYPE[71] = ['71', 'Message number', 'N', '-', 4, 'n', 'A']
    _BITS_VALUE_TYPE[72] = ['72', 'Data record', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[73] = ['73', 'Date action', 'N', '-', 6, 'n', 'A']
    _BITS_VALUE_TYPE[74] = ['74', 'Credits, number', 'N', '-', 10, 'n', 'A']
    _BITS_VALUE_TYPE[75] = ['75', 'Credits, reversal number', 'N', '-', 10, 'n', 'A']
    _BITS_VALUE_TYPE[76] = ['76', 'Debits, number', 'N', '-', 10, 'n', 'A']
    _BITS_VALUE_TYPE[77] = ['77', 'Debits, reversal number', 'N', '-', 10, 'n', 'A']
    _BITS_VALUE_TYPE[78] = ['78', 'Transfer number', 'N', '-', 10, 'n', 'A']
    _BITS_VALUE_TYPE[79] = ['79', 'Transfer, reversal number', 'N', '-', 10, 'n', 'A']
    _BITS_VALUE_TYPE[80] = ['80', 'Inquiries number', 'N', '-', 10, 'n', 'A']
    _BITS_VALUE_TYPE[81] = ['81', 'Authorizations, number', 'N', '-', 10, 'n', 'A']
    _BITS_VALUE_TYPE[82] = [
        '82', 'Credits, processing fee amount', 'N', '-', 12, 'n', 'A']
    _BITS_VALUE_TYPE[83] = [
        '83', 'Credits, transaction fee amount', 'N', '-', 12, 'n', 'A']
    _BITS_VALUE_TYPE[84] = [
        '84', 'Debits, processing fee amount', 'N', '-', 12, 'n', 'A']
    _BITS_VALUE_TYPE[85] = [
        '85', 'Debits, transaction fee amount', 'N', '-', 12, 'n', 'A']
    _BITS_VALUE_TYPE[86] = ['86', 'Credits, amount', 'N', '-', 16, 'n', 'A']
    _BITS_VALUE_TYPE[87] = ['87', 'Credits, reversal amount', 'N', '-', 16, 'n', 'A']
    _BITS_VALUE_TYPE[88] = ['88', 'Debits, amount', 'N', '-', 16, 'n', 'A']
    _BITS_VALUE_TYPE[89] = ['89', 'Debits, reversal amount', 'N', '-', 16, 'n', 'A']
    _BITS_VALUE_TYPE[90] = ['90', 'Original data elements', 'N', '-', 42, 'n', 'A']
    _BITS_VALUE_TYPE[91] = ['91', 'File update code', 'AN', '-', 1, 'an', 'A']
    _BITS_VALUE_TYPE[92] = ['92', 'File security code', 'N', '-', 2, 'n', 'A']
    _BITS_VALUE_TYPE[93] = ['93', 'Response indicator', 'N', '-', 5, 'n', 'A']
    _BITS_VALUE_TYPE[94] = ['94', 'Service indicator', 'AN', '-', 7, 'an', 'A']
    _BITS_VALUE_TYPE[95] = ['95', 'Replacement amounts', 'AN', '-', 42, 'an', 'A']
    _BITS_VALUE_TYPE[96] = ['96', 'Message security code', 'AN', '-', 8, 'an', 'A']
    _BITS_VALUE_TYPE[97] = ['97', 'Amount, net settlement', 'N', '-', 16, 'n', 'A']
    _BITS_VALUE_TYPE[98] = ['98', 'Payee', 'ANS', '-', 25, 'ans', 'A']
    _BITS_VALUE_TYPE[99] = [
        '99', 'Settlement institution identification code', 'LL', 'A', 11, 'n', 'A']
    _BITS_VALUE_TYPE[100] = [
        '100', 'Receiving institution identification code', 'LL', 'A', 11, 'n', 'A']
    _BITS_VALUE_TYPE[101] = ['101', 'File name', 'LL', 'ANS', 17, 'ans', 'A']
    _BITS_VALUE_TYPE[102] = [
        '102', 'Account identification 1', 'LL', 'A', 28, 'ans', 'A']
    _BITS_VALUE_TYPE[103] = [
        '103', 'Account identification 2', 'LL', 'A', 28, 'ans', 'A']
    _BITS_VALUE_TYPE[104] = [
        '104', 'Transaction description', 'LLL', 'A', 100, 'ans', 'A']
    _BITS_VALUE_TYPE[105] = ['105', 'Reserved for ISO use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[106] = ['106', 'Reserved for ISO use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[107] = ['107', 'Reserved for ISO use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[108] = ['108', 'Reserved for ISO use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[109] = ['109', 'Reserved for ISO use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[110] = ['110', 'Reserved for ISO use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[111] = [
        '111', 'Reserved for private use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[112] = [
        '112', 'Reserved for private use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[113] = ['113', 'Reserved for private use', 'LL', 'A', 11, 'n', 'A']
    _BITS_VALUE_TYPE[114] = [
        '114', 'Reserved for national use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[115] = [
        '115', 'Reserved for national use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[116] = [
        '116', 'Reserved for national use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[117] = [
        '117', 'Reserved for national use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[118] = [
        '118', 'Reserved for national use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[119] = [
        '119', 'Reserved for national use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[120] = [
        '120', 'Reserved for private use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[121] = [
        '121', 'Reserved for private use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[122] = [
        '122', 'Reserved for national use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[123] = [
        '123', 'Reserved for private use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[124] = ['124', 'Info Text', 'LLL', 'A', 255, 'ans', 'A']
    _BITS_VALUE_TYPE[125] = [
        '125', 'Network management information', 'LL', 'A', 50, 'ans', 'A']
    _BITS_VALUE_TYPE[126] = ['126', 'Issuer trace id', 'LL', 'A', 6, 'ans', 'A']
    _BITS_VALUE_TYPE[127] = ['127', 'Reserved for private use', 'LLL', 'A', 999, 'ans', 'A']
    _BITS_VALUE_TYPE[128] = ['128', 'Message authentication code (MAC) field', 'B', '-', 16, 'b', 'A']


    ################################################################################################
    # Default constructor of the ISO8583 Object
    def __init__(self, iso="", debug=False, bitmap_uppercase=False, hdrlen=0):
        """Default Constructor of ISO8583 Package.
        It initialize a "brand new" ISO8583 package
        Example: To Enable debug you can use:
            pack = ISO8583(debug=True)
        @param: iso a String that represents the ASCII of the package. The same that you need to pass to setIsoContent() method.
        @param: debug (True or False) default False -> Used to print some debug infos. Only use if want that messages!
        """
        # Bitmap internal representation
        self.BITMAP = []
        # Values
        self.BITMAP_VALUES = []
        # Bitmap ASCII representation
        self.BITMAP_HEX = b''
        self.BITMAP_format = 'A'
        # MTI
        self.MESSAGE_TYPE_INDICATION = b''
        self.MTI_format = 'A'
        # Debug ?
        self.DEBUG = debug
        # Bitmap uses uppercase ?
        self.BITMAP_UPPERCASE = bitmap_uppercase
        # Header (optional)
        self.hdrlen = hdrlen
        self.hdr = b''

        self.__initializeBitmap()
        self.__initializeBitmapValues()

        if iso != "":
            self.setIsoContent(iso)

    ################################################################################################

    ################################################################################################
    # Return small bit name
    def getSmallBitName(self, bit):
        """Method that return the small bit name
        @param: bit -> Bit that will be searched and whose name will be returned
        @return: str that represents the name of the bit
        """
        return self._BITS_VALUE_TYPE[bit][0]

    ################################################################################################

    ################################################################################################
    # Return large bit name
    def getLargeBitName(self, bit):
        """Method that return the large bit name
        @param: bit -> Bit that will be searched and whose name will be returned
        @return: str that represents the name of the bit
        """
        return self._BITS_VALUE_TYPE[bit][1]

    ################################################################################################

    ################################################################################################
    # Return bit type
    def getBitType(self, bit):
        """Method that return the bit Type
        @param: bit -> Bit that will be searched and whose type will be returned
        @return: str that represents the type of the bit
        """
        return self._BITS_VALUE_TYPE[bit][2]

    ################################################################################################

    ################################################################################################
    # Return bit type
    def getBitLenForm(self,bit):
        """Method that return the bit Length Indicator Format
        @param: bit -> Bit that will be searched and whose length indicator format will be returned
        @return: str that represents the length indicator format of the bit
        """
        return self._BITS_VALUE_TYPE[bit][3]
    ################################################################################################

    ################################################################################################
    # Return bit limit
    def getBitLimit(self, bit):
        """Method that return the bit limit (Max size)
        @param: bit -> Bit that will be searched and whose limit will be returned
        @return: int that indicate the limit of the bit
        """
        return self._BITS_VALUE_TYPE[bit][4]

    ################################################################################################

    ################################################################################################
    # Return bit value type
    def getBitValueType(self, bit):
        """Method that return the bit value type
        @param: bit -> Bit that will be searched and whose value type will be returned
        @return: str that indicate the valuye type of the bit
        """
        return self._BITS_VALUE_TYPE[bit][5]

    ################################################################################################

    ################################################################################################
    #Return bit type
    def getBitFormat(self,bit):
        """Method that return the bit Format (Ascii, Ebcdic, Packed)
        @param: bit -> Bit that will be searched and whose format will be returned
        @return: str that represents the format of the bit
        """
        return self._BITS_VALUE_TYPE[bit][6]
    ################################################################################################

    ################################################################################################
    # Set the header 
    def setHdr(self, hdr):
        """Method that sets the optional header byte string
        """


        self.hdr = hdr
        self.hdrlen = len(hdr)

    ################################################################################################

    ################################################################################################
    # Set the header length
    def setHdrlen(self, hdrlen):
        """Method that sets the optional header byte length
        """

        if hdrlen < 0: # Sanitize input
            hdrlen = 0

        self.hdrlen = hdrlen
        if hdrlen == 0: # Clear header
            self.hdr = b''
        elif len(self.hdr) > self.hdrlen: # truncate header
            self.hdr = self.hdr[0:self.hdrlen]
        elif len(self.hdr) < self.hdrlen:
            self.hdr = self.hdr.ljust(self.hdrlen)

    ################################################################################################

    ################################################################################################
    # Get the header 
    def getHdr(self):
        """Method that gets the optional header byte string
        """

        return self.hdr

    ################################################################################################

    ################################################################################################
    # Get the header length
    def getHdrlen(self):
        """Method that gets the optional header byte length
        """

        return self.hdrlen

    ################################################################################################

    ################################################################################################
    # Set the MTI format (ASCII/BCD)
    def setMTIformat(self, format='A'):
        """Method that set Transaction Type (MTI) format, 'B'CD, 'A'SCII or 'E'BCDIC
        """

        if format != 'A' and format != 'B' and format != 'E':
            raise InvalidFormat('Error: Invalid MTI format!')

        self.MTI_format = format

    ################################################################################################

    ################################################################################################
    # Set the MTI format (ASCII/EBCDIC/BCD)
    def setBITMAPformat(self, format='A'):
        """Method that set the BITMAP format, 'A'SCII, 'E'BCDIC or 'P'acked
        """

        if format != 'A' and format != 'P' and format != 'E':
            raise InvalidFormat('Error: Invalid BITMAP format!')

        self.BITMAP_format = format

    ################################################################################################

    ################################################################################################
    # Set the MTI
    def setTransactionType(self, type):
        """Method that set Transaction Type (MTI)
        @param: type -> MTI to be setted
        @raise: ValueTooLarge Exception
        """

        type = "%s" % type
        if len(type) > 4:
            type = type[0:3]
            raise ValueTooLarge('Error: value up to size! MTI limit size = 4')

        if self.MTI_format == 'A':
            self.MESSAGE_TYPE_INDICATION = type.zfill(4).encode()
        elif self.MTI_format == 'E':
            self.MESSAGE_TYPE_INDICATION = type.zfill(4).encode('cp1148')
        else:
            self.MESSAGE_TYPE_INDICATION = binascii.unhexlify(type.zfill(4))

    ################################################################################################

    ################################################################################################
    # setMTI too
    def setMTI(self, type):
        """Method that set Transaction Type (MTI)
        In fact, is an alias to "setTransactionType" method
        @param: type -> MTI to be setted
        """
        self.setTransactionType(type)

    ################################################################################################

    ################################################################################################
    # Method that put "zeros" inside bitmap
    def __initializeBitmap(self):
        """Method that initialize/reset a internal bitmap representation
        It's a internal method, so don't call!
        """

        if self.DEBUG is True:
            print('Init bitmap')

        if len(self.BITMAP) == 16:
            for cont in range(0, 16):
                self.BITMAP[cont] = self._BIT_DEFAULT_VALUE
        else:
            for cont in range(0, 16):
                self.BITMAP.append(self._BIT_DEFAULT_VALUE)

    ################################################################################################

    ################################################################################################
    # init with "0" the array of values
    def __initializeBitmapValues(self):
        """Method that initialize/reset a internal array used to save bits and values
        It's a internal method, so don't call!
        """
        if self.DEBUG is True:
            print('Init bitmap_values')

        if len(self.BITMAP_VALUES) == 128:
            for cont in range(0, 129):
                self.BITMAP_VALUES[cont] = self._BIT_DEFAULT_VALUE
        else:
            for cont in range(0, 129):
                self.BITMAP_VALUES.append(self._BIT_DEFAULT_VALUE)

    ################################################################################################

    ################################################################################################
    # Unset a bit
    def unsetBit(self, bit):
        """Method used to unset a bit.
        @param: bit -> bit number that want to be setted
        @raise: BitNonexistent Exception Exception
        """
        if self.DEBUG is True:
            print('Unsetting bit inside bitmap bit[%s]' % bit)

        if bit < 1 or bit > 128:
            raise BitNonexistent("Bit number %s dosen't exist!" % bit)

        # Clear the existing bit value (if present)
        self.BITMAP_VALUES[bit] = self._BIT_DEFAULT_VALUE

        # calculate the position inside the bitmap
        pos = 1
        if (bit % 8) == 0:
            pos = (bit // 8) - 1
        else:
            pos = (bit // 8)

        # need to check if the value can be there .. AN , N ... etc ... and the size

        self.BITMAP[pos] = self.BITMAP[pos] & ~self._TMP[(bit % 8) + 1]

        # Clear the continuation bit?
        if bit > 64 and self.BITMAP[8:15] == [0, 0, 0, 0, 0, 0, 0]:
           # need to unset bit 1 of first "bit" in bitmap
           self.BITMAP[0] = self.BITMAP[0] & ~self._TMP[2]

        return True

    ################################################################################################

    ################################################################################################
    # Set a value to a bit
    def setBit(self, bit, value):
        """Method used to set a bit with a value.
        It's one of the most important method to use when using this library
        @param: bit -> bit number that want to be setted
        @param: value -> the value of the bit
        @return: True/False default True -> To be used in the future!
        @raise: BitNonexistent Exception, ValueTooLarge Exception
        """
        if self.DEBUG is True:
            print('Setting bit inside bitmap bit[%s] = %s' % (bit, value))

        if bit < 1 or bit > 128:
            raise BitNonexistent("Bit number %s dosen't exist!" % bit)

        # calculate the position inside the bitmap
        pos = 1

        if self.getBitType(bit) == 'LL':
            self.__setBitTypeLL(bit, value)

        if self.getBitType(bit) == 'LLL':
            self.__setBitTypeLLL(bit, value)

        if self.getBitType(bit) == 'LLLLLL':
            self.__setBitTypeLLLLLL(bit, value)

        if self.getBitType(bit) == 'N':
            self.__setBitTypeN(bit, value)

        if self.getBitType(bit) == 'A':
            self.__setBitTypeA(bit, value)

        if self.getBitType(bit) == 'AN':
            self.__setBitTypeAN(bit, value)

        if self.getBitType(bit) == 'ANS':
            self.__setBitTypeANS(bit, value)

        if self.getBitType(bit) == 'B':
            self.__setBitTypeB(bit, value)

        # Continuation bit?
        if bit > 64:
            # need to set bit 1 of first "bit" in bitmap
            self.BITMAP[0] = self.BITMAP[0] | self._TMP[2]

        if (bit % 8) == 0:
            pos = (bit // 8) - 1
        else:
            pos = (bit // 8)

        # need to check if the value can be there .. AN , N ... etc ... and the size

        self.BITMAP[pos] = self.BITMAP[pos] | self._TMP[(bit % 8) + 1]

        return True

    ################################################################################################

    ################################################################################################
    # print bitmap
    def showBitmap(self):
        """Method that print the bitmap in ASCII form
        Hint: Try to use getBitmap method and format your own print :)
        """

        self.__buildBitmap()

        # printing
        print(self.BITMAP_HEX)

    ################################################################################################

    ################################################################################################
    # Build a bitmap
    def __buildBitmap(self):
        """Method that build the bitmap ASCII
        It's a internal method, so don't call!
        """

        self.BITMAP_HEX = b''

        for c in range(0, 16):
            if (self.BITMAP[0] & self._BIT_POSITION_1) != self._BIT_POSITION_1:
                # Only has the first bitmap
                if self.DEBUG is True:
                    print('%d Bitmap = %d(Decimal) = %s (hexa) ' %
                          (c, self.BITMAP[c], hex(self.BITMAP[c])))

                tm = hex(self.BITMAP[c])[2:]
                if self.BITMAP_UPPERCASE is True:
                    tm = tm.upper()
                if len(tm) != 2:
                    tm = '0' + tm
                self.BITMAP_HEX += tm.encode()
                if c == 7:
                    break
            else:  # second bitmap
                if self.DEBUG is True:
                    print('%d Bitmap = %d(Decimal) = %s (hexa) ' %
                          (c, self.BITMAP[c], hex(self.BITMAP[c])))

                tm = hex(self.BITMAP[c])[2:]
                if self.BITMAP_UPPERCASE is True:
                    tm = tm.upper()
                if len(tm) != 2:
                    tm = '0' + tm
                self.BITMAP_HEX += tm.encode()

    ################################################################################################

    ################################################################################################
    # Get a bitmap from str
    def __getBitmapFromStr(self, bitmap_raw):
        """Method that receive a bitmap str and transfor it to ISO8583 object readable.
        @param: bitmap -> bitmap str to be readable
        It's a internal method, so don't call!
        """
        # Need to check if the size is correct etc...
        cont = 0

        if self.BITMAP_HEX != b'':
            self.BITMAP_HEX = b''

        if self.BITMAP_format == 'A':
            bitmap = bitmap_raw
        elif self.BITMAP_format == 'E':
            bitmap = bitmap_raw.decode('cp1148').encode()
        else:
            bitmap = binascii.hexlify(bitmap_raw[0:8])
            if (int(bitmap[0:2], 16) & self._BIT_POSITION_1) == self._BIT_POSITION_1:  # Also 2nd bitmap
                bitmap = binascii.hexlify(bitmap_raw[0:16]) # Now we have the full double-length bitmap unpacked

        for x in range(0, 32, 2):
            if (int(bitmap[0:2], 16) & self._BIT_POSITION_1) != self._BIT_POSITION_1:  # Only 1 bitmap
                if self.DEBUG is True:
                    print('Token[%d] %s converted to int is = %s' %
                          (x, bitmap[x:x + 2], int(bitmap[x:x + 2], 16)))

                self.BITMAP_HEX += bitmap[x:x + 2]
                self.BITMAP[cont] = int(bitmap[x:x + 2], 16)
                if x == 14:
                    break
            else:  # Second bitmap
                if self.DEBUG is True:
                    print('Token[%d] %s converted to int is = %s' %
                          (x, bitmap[x:x + 2], int(bitmap[x:x + 2], 16)))

                self.BITMAP_HEX += bitmap[x:x + 2]
                self.BITMAP[cont] = int(bitmap[x:x + 2], 16)
            cont += 1

    ################################################################################################

    ################################################################################################
    # print bit array that is present in the bitmap
    def showBitsFromBitmapStr(self, bitmap):
        """Method that receive a bitmap str, process it, and print a array with bits this bitmap string represents.
        Usualy is used to debug things.
        @param: bitmap -> bitmap str to be analized and translated to "bits"
        """
        bits = self.__initializeBitsFromBitmapStr(bitmap)
        print('Bits inside %s  = %s' % (bitmap, bits))

    ################################################################################################

    ################################################################################################
    # initialize a bitmap using ASCII str
    def __initializeBitsFromBitmapStr(self, bitmap):
        """Method that receive a bitmap str, process it, and prepare ISO8583 object to understand and "see" the bits and values inside the ISO ASCII package.
        It's a internal method, so don't call!
        @param: bitmap -> bitmap str to be analized and translated to "bits"
        """
        bits = []
        for c in range(0, 16):
            for d in range(1, 9):
                if self.DEBUG is True:
                    print('Value (%d)-> %s & %s = %s' % (
                        d, self.BITMAP[c], self._TMP[d], (self.BITMAP[c] & self._TMP[d])))
                if (self.BITMAP[c] & self._TMP[d]) == self._TMP[d]:
                    if d == 1:  # e o 8 bit
                        if self.DEBUG is True:
                            print('Bit %s is present !!!' % ((c + 1) * 8))
                        bits.append((c + 1) * 8)
                        self.BITMAP_VALUES[(c + 1) * 8] = b'X'
                    else:
                        if (c == 0) & (d == 2):  # Continuation bit
                            if self.DEBUG is True:
                                print('Bit 1 is present !!!')

                            bits.append(1)

                        else:
                            if self.DEBUG is True:
                                print('Bit %s is present !!!' %
                                      (c * 8 + d - 1))

                            bits.append(c * 8 + d - 1)
                            self.BITMAP_VALUES[c * 8 + d - 1] = b'X'

        bits.sort()

        return bits

    ################################################################################################

    ################################################################################################
    # return a array of bits, when processing the bitmap
    def __getBitsFromBitmap(self):
        """Method that process the bitmap and return a array with the bits presents inside it.
        It's a internal method, so don't call!
        """
        bits = []
        for c in range(0, 16):
            for d in range(1, 9):
                if self.DEBUG is True:
                    print('Value (%d)-> %s & %s = %s' % (
                        d, self.BITMAP[c], self._TMP[d], (self.BITMAP[c] & self._TMP[d])))
                if (self.BITMAP[c] & self._TMP[d]) == self._TMP[d]:
                    if d == 1:  # e o 8 bit
                        if self.DEBUG is True:
                            print('Bit %s is present !!!' % ((c + 1) * 8))

                        bits.append((c + 1) * 8)
                    else:
                        if (c == 0) & (d == 2):  # Continuation bit
                            if self.DEBUG is True:
                                print('Bit 1 is present !!!')

                            bits.append(1)

                        else:
                            if self.DEBUG is True:
                                print('Bit %s is present !!!' %
                                      (c * 8 + d - 1))

                            bits.append(c * 8 + d - 1)

        bits.sort()

        return bits

    ################################################################################################

    ################################################################################################
    # Method that receive a ISO8583 ASCII package in the network form and parse it.
    def __formatValue(self,bit,value):
        """Method that formats a value to the appropriate data for the bit or LL or LLL bits
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: Nothing as yet
        @return: binary data that represents the format of the bit
        It's a internal method, so don't call!
        """
        size = "%s" % len(value)
        data_form = self.getBitFormat(bit)

        if data_form == "A":
            data = value.encode()
        elif data_form == "E":
            data = value.encode('cp1148')
        else: # Packed data
            # Needs to be even length, with padding on the right
            if int(size) % 2 == 0:
                data = binascii.unhexlify(value)
            else: # Pad to the right with a single '0' character
                data = binascii.unhexlify(value + '0')

        return data

    ################################################################################################

    ################################################################################################
    # Set of type LL
    def __setBitTypeLL(self, bit, value):
        """Method that set a bit with value in form LL
        It put the size in front of the value
        Example: pack.setBit(99,'123') -> Bit 99 is a LL type, so this bit, in ASCII form need to be 03123. To understand, 03 is the size of the information and 123 is the information/value
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueTooLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value

        if len(value) > 99:
            # value = value[0:99]
            raise ValueTooLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))
        if len(value) > self.getBitLimit(bit):
            raise ValueTooLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))

        size = "%s" % len(value)
        data = self.__formatValue(bit, value)
        lenform = self.getBitLenForm(bit)

        if lenform == 'A':
            self.BITMAP_VALUES[bit] = size.zfill(2).encode() + data
        elif lenform == 'E':
            self.BITMAP_VALUES[bit] = size.zfill(2).encode('cp1148') + data
        elif lenform == 'P':
            self.BITMAP_VALUES[bit] = self.__IntToLLPack(len(value)) + data
        else:
            self.BITMAP_VALUES[bit] = self.__IntToLLBCD(len(value)) + data

    ################################################################################################

    ################################################################################################
    # Set of type LLL
    def __setBitTypeLLL(self, bit, value):
        """Method that set a bit with value in form LLL
        It put the size in front of the value
        Example: pack.setBit(104,'12345ABCD67890') -> Bit 104 is a LLL type, so this bit, in ASCII form need to be 01412345ABCD67890.
            To understand, 014 is the size of the information and 12345ABCD67890 is the information/value
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueTooLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value

        if len(value) > 999:
            raise ValueTooLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))
        if len(value) > self.getBitLimit(bit):
            raise ValueTooLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))

        size = "%s" % len(value)
        data = self.__formatValue(bit, value)
        lenform = self.getBitLenForm(bit)

        if lenform == 'A':
            self.BITMAP_VALUES[bit] = size.zfill(3).encode() + data
        elif lenform == 'E':
            self.BITMAP_VALUES[bit] = size.zfill(3).encode('cp1148') + data
        elif lenform == 'P':
            self.BITMAP_VALUES[bit] = self.__IntToLLLPack(len(value)) + data
        else:
            self.BITMAP_VALUES[bit] = self.__IntToLLLBCD(len(value)) + data

    ################################################################################################

    ################################################################################################
    # Set of type LLLLLL
    def __setBitTypeLLLLLL(self, bit, value):
        """Method that set a bit with value in form LLLLLL
        It put the size in front of the value
        Example: pack.setBit(104,'12345ABCD67890') -> If Bit 104 is a LLLLLL type, so this bit, in ASCII form need to be 00001412345ABCD67890.
            To understand, 000014 is the size of the information and 12345ABCD67890 is the information/value
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueTooLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value

        if len(value) > 999999:
            raise ValueTooLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))
        if len(value) > self.getBitLimit(bit):
            raise ValueTooLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))

        size = "%s" % len(value)
        data = self.__formatValue(bit, value)
        lenform = self.getBitLenForm(bit)

        if lenform == 'A':
            self.BITMAP_VALUES[bit] = size.zfill(6).encode() + data
        elif lenform == 'E':
            self.BITMAP_VALUES[bit] = size.zfill(6).encode('cp1148') + data
        elif lenform == 'P':
            self.BITMAP_VALUES[bit] = self.__IntToLLLLLLPack(len(value)) + data
        else:
            self.BITMAP_VALUES[bit] = self.__IntToLLLLLLBCD(len(value)) + data

    ################################################################################################

    ################################################################################################
    # Set of type N,
    def __setBitTypeN(self, bit, value):
        """Method that set a bit with value in form N
        It complete the size of the bit with a default value
        Example: pack.setBit(3,'30000') -> Bit 3 is a N type, so this bit, in ASCII form need to has size = 6 (ISO specification) so the value 30000 size = 5 need to receive more "1" number.
            In this case, will be "0" in the left. In the package, the bit will be sent like '030000'
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueTooLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value

        if len(value) > self.getBitLimit(bit):
            value = value[0:self.getBitLimit(bit)]
            raise ValueTooLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))

        #self.__checkBitTypeValidity(bit, value)

        data_form = self.getBitFormat(bit)

        if data_form == "A":
            self.BITMAP_VALUES[bit] = value.zfill(self.getBitLimit(bit)).encode()
        elif data_form == "E":
            self.BITMAP_VALUES[bit] = value.zfill(self.getBitLimit(bit)).encode('cp1148')
        else: # Packed data - make sure that it's left zero-filled to the correct length- a multiple of 2
            unpacked_len = self.__getUnpackedLen(self.getBitLimit(bit))
            self.BITMAP_VALUES[bit] = binascii.unhexlify(value.zfill(unpacked_len))

    ################################################################################################

    ################################################################################################
    # Set of type A
    def __setBitTypeA(self, bit, value):
        """Method that set a bit with value in form A
        It complete the size of the bit with a default value
        Example: pack.setBit(3,'30000') -> Bit 3 is a A type, so this bit, in ASCII form need to has size = 6 (ISO specification) so the value 30000 size = 5 need to receive more "1" number.
            In this case, will be "0" in the left. In the package, the bit will be sent like '030000'
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueTooLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value

        if len(value) > self.getBitLimit(bit):
            value = value[0:self.getBitLimit(bit)]
            raise ValueTooLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))

        #self.__checkBitTypeValidity(bit, value)

        data_form = self.getBitFormat(bit)

        if data_form == "A":
            self.BITMAP_VALUES[bit] = value.zfill(self.getBitLimit(bit)).encode()
        elif data_form == "E":
            self.BITMAP_VALUES[bit] = value.zfill(self.getBitLimit(bit)).encode('cp1148')

    ################################################################################################

    ################################################################################################
    # Set of type AN
    def __setBitTypeAN(self, bit, value):
        """Method that set a bit with value in form AN
        It complete the size of the bit with a default value
        Example: pack.setBit(3,'30000') -> Bit 3 is a A type, so this bit, in ASCII form need to has size = 6 (ISO specification) so the value 30000 size = 5 need to receive more "1" number.
            In this case, will be "0" in the left. In the package, the bit will be sent like '030000'
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueTooLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value

        if len(value) > self.getBitLimit(bit):
            value = value[0:self.getBitLimit(bit)]
            raise ValueTooLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))

        #self.__checkBitTypeValidity(bit, value)

        data_form = self.getBitFormat(bit)

        if data_form == "A":
            self.BITMAP_VALUES[bit] = value.zfill(self.getBitLimit(bit)).encode()
        elif data_form == "E":
            self.BITMAP_VALUES[bit] = value.zfill(self.getBitLimit(bit)).encode('cp1148')

    ################################################################################################

    ################################################################################################
    # Set of type B
    def __setBitTypeB(self, bit, value):
        """Method that set a bit with value in form B
        It complete the size of the bit with a default value
        Example: pack.setBit(3,'30000') -> Bit 3 is a B type, so this bit, in ASCII form need to has size = 6 (ISO specification) so the value 30000 size = 5 need to receive more "1" number.
            In this case, will be "0" in the left. In the package, the bit will be sent like '030000'
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueTooLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value

        if len(value) > self.getBitLimit(bit):
            value = value[0:self.getBitLimit(bit)]
            raise ValueTooLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))

        data_form = self.getBitFormat(bit)

        if data_form == "A":
            self.BITMAP_VALUES[bit] = value.zfill(self.getBitLimit(bit)).encode()
        elif data_form == "E":
            self.BITMAP_VALUES[bit] = value.zfill(self.getBitLimit(bit)).encode('cp1148')
        else: # Packed data- ensure it is a multiple of 2. Also pad with zeros to the left if required
            unpacked_len = self.__getUnpackedLen(self.getBitLimit(bit))
            self.BITMAP_VALUES[bit] = binascii.unhexlify(value.zfill(unpacked_len))

    ################################################################################################

    ################################################################################################
    # Set of type ANS
    def __setBitTypeANS(self, bit, value):
        """Method that set a bit with value in form ANS
        It complete the size of the bit with a default value
        Example: pack.setBit(3,'30000') -> Bit 3 is a ANS type, so this bit, in ASCII form need to has size = 6 (ISO specification) so the value 30000 size = 5 need to receive more "1" number.
            In this case, will be "0" in the left. In the package, the bit will be sent like '030000'
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueTooLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value

        if len(value) > self.getBitLimit(bit):
            value = value[0:self.getBitLimit(bit)]
            raise ValueTooLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))

        #self.__checkBitTypeValidity(bit, value)

        data_form = self.getBitFormat(bit)

        if data_form == "A":
            self.BITMAP_VALUES[bit] = value.zfill(self.getBitLimit(bit)).encode()
        elif data_form == "E":
            self.BITMAP_VALUES[bit] = value.zfill(self.getBitLimit(bit)).encode('cp1148')

    ################################################################################################

    ################################################################################################
    # print os bits insede iso
    def showIsoBits(self, showall=False):
        """Method that show in detail a list of bits , values and types inside the object
        Example: output to
            (...)
            iso.setBit(2,2)
            iso.setBit(4,4)
            (...)
            iso.showIsoBits()
            (...)
            Bit[2] of type LL has limit 19 = 012
            Bit[4] of type N has limit 12 = 000000000004
            (...)
        """

        for cont in range(1, 129):
            if self.BITMAP_VALUES[cont] != self._BIT_DEFAULT_VALUE:
                print("Bit[%s] of type %s has limit %s = %s" % (
                    cont, self.getBitType(cont), self.getBitLimit(cont), self.BITMAP_VALUES[cont]))
            elif showall is True:
                print("Bit[%s] of type %s has limit %s" % (
                    cont, self.getBitType(cont), self.getBitLimit(cont)))

    ################################################################################################

    ################################################################################################
    # print Raw iso
    def showRawIso(self):
        """Method that print ISO8583 ASCII complete representation
        Example:
        iso = ISO8583()
        iso.setMTI('0800')
        iso.setBit(2,2)
        iso.setBit(4,4)
        iso.setBit(12,12)
        iso.setBit(17,17)
        iso.setBit(99,99)
        iso.showRawIso()
        output (print) -> 0800d010800000000000000000002000000001200000000000400001200170299
        Hint: Try to use getRawIso method and format your own print :)
        """

        resp = self.getRawIso()
        print(resp)

    ################################################################################################

    ################################################################################################
    # Return raw iso
    def getRawIso(self, nohdr=False):
        """Method that return ISO8583 ASCII complete representation
        Example:
        iso = ISO8583()
        iso.setMTI('0800')
        iso.setBit(2,2)
        iso.setBit(4,4)
        iso.setBit(12,12)
        iso.setBit(17,17)
        iso.setBit(99,99)
        str = iso.getRawIso()
        print ('This is the ASCII package %s' % str)
        output (print) -> This is the ASCII package 0800d010800000000000000000002000000001200000000000400001200170299

        @return: str with complete ASCII ISO8583
        @raise: InvalidMTI Exception
        """

        self.__buildBitmap()

        if self.MESSAGE_TYPE_INDICATION == b'':
            raise InvalidMTI('Check MTI! Do you set it?')

        # Start with the header, if set (or b'' if not)
        if nohdr is True:
            resp = b''
        else:
            resp = self.hdr

        resp += self.MESSAGE_TYPE_INDICATION
        if self.BITMAP_format == 'A':
            resp += self.BITMAP_HEX
        elif self.BITMAP_format == 'E':
            resp += self.BITMAP_HEX.decode().encode('cp1148')
        else:
            resp += binascii.unhexlify(self.BITMAP_HEX)

        for cont in range(0, 129):
            if self.BITMAP_VALUES[cont] != self._BIT_DEFAULT_VALUE:
                resp = resp + self.BITMAP_VALUES[cont]

        return resp

    ################################################################################################

    ################################################################################################
    # Redefine a bit
    def redefineBit(self, bit, smallStr, largeStr, bitType, LenForm, size, valueType, format):
        """Method that redefine a bit structure in global scope!
        Can be used to personalize ISO8583 structure to another specification (ISO8583 1987 for example!)
        Hint: If you have a lot of "ValueTooLarge Exception" maybe the specification that you are using is different of mine. So you will need to use this method :)
        @param: bit -> bit to be redefined
        @param: smallStr -> a small String representantion of the bit, used to build "user friendly prints", example "2" for bit 2
        @param: largeStr -> a large String representantion of the bit, used to build "user friendly prints" and to be used to inform the "main use of the bit",
            example "Primary account number (PAN)" for bit 2
        @param: bitType -> type the bit, used to build the values, example "LL" for bit 2. Need to be one of (B, N, AN, ANS, LL, LLL, LLLLLL)
        @param: LenForm -> Length indicator format for LL and LLL fields- 'A' for ASCII, 'B' for BCD, 'P' for packed hex or '-' if bitType not LL or LLL
        @param: size -> limit size the bit, used to build/complete the values, example "19" for bit 2.
        @param: valueType -> value type the bit, used to "validate" the values, example "n" for bit 2. This mean that in bit 2 we need to have only numeric values.
            Need to be one of (a, an, n, ans, b)
        @param: format -> format of the bit, encode/decode the values- 'A' for ASCII, 'E' for EBCDIC.
        @raise: BitNonexistent Exception, InvalidValueType Exception

        """

        if self.DEBUG is True:
            print('Trying to redefine the bit with (self,%s,%s,%s,%s,%s,%s,%s,%s)' % (
                bit, smallStr, largeStr, bitType, LenForm, size, valueType, format))

        # validating bit position
        if bit == 1 or bit < 0 or bit > 128:
            raise BitNonexistent(
                "Error %d cannot be changed because has a invalid number!" % bit)

        if bitType != "B" and bitType != "N" and bitType != "A" and bitType != "AN" and bitType != "ANS" and bitType != "LL" and bitType != "LLL" and bitType != "LLLLLL":
            raise InvalidBitType(
                "Error bit %d cannot be changed because %s is not a valid bitType (B, N, A, AN, ANS, LL, LLL)!" % (
                    bit, bitType))

        if LenForm != '-' and bitType != "LL" and bitType != "LLL" and bitType != "LLLLLL":
            raise InvalidLenForm("Error %d cannot be changed because has an invalid LenForm!" % bit)

        if LenForm != '-' and LenForm != 'A' and LenForm != 'E' and LenForm != 'B' and LenForm != 'P':
            raise InvalidLenForm("Error %d cannot be changed because has an invalid %s LenForm!" % (bit, LenForm))

        # need to validate if the type and size is compatible! example slimit = 100 and type = LL

        if valueType != "a" and valueType != "n" and valueType != "ans" and valueType != "b" and valueType != "an":
            raise InvalidValueType(
                "Error bit %d cannot be changed because %s is not a valid valueType (a, an, n ans, b)!" % (
                    bit, valueType))

        if format != 'A' and format != 'E' and format != 'P':
            raise InvalidFormat("Error %d cannot be changed because has an invalid %s format!" % (bit, format))

        if format == 'P' and bitType != 'B' and bitType != 'N' and bitType != 'LL' and bitType != 'LLL' and bitType != 'LLLLLL':
            raise InvalidFormat("Error %d cannot be changed because has an invalid %s format (cannot be packed)!" % (bit, format))
        self._BITS_VALUE_TYPE[bit] = [smallStr, largeStr, bitType, LenForm, size, valueType, format]

        if self.DEBUG is True:
            print('Bit %d redefined!' % bit)

    ################################################################################################

    ################################################################################################
    # a partir de um trem de string, pega o MTI
    def __setMTIFromStr(self, iso):
        """Method that get the first 4 characters to be the MTI.
        It's a internal method, so don't call!
        """

        if self.MTI_format == 'A' or self.MTI_format == 'E':
            self.MESSAGE_TYPE_INDICATION = iso[0:4]
        else:
            self.MESSAGE_TYPE_INDICATION = iso[0:2]

        if self.DEBUG is True:
            print('MTI found was %s' % self.MESSAGE_TYPE_INDICATION)

    ################################################################################################

    ################################################################################################
    # return the MTI
    def getMTI(self):
        """Method that return the MTI of the package
        @return: str -> with the MTI
        """

        # Need to validate if the MTI was setted ...etc ...
        if self.MTI_format == 'A':
            return self.MESSAGE_TYPE_INDICATION.decode()
        elif self.MTI_format == 'E':
            return self.MESSAGE_TYPE_INDICATION.decode('cp1148')
        else:
            return binascii.hexlify(self.MESSAGE_TYPE_INDICATION).decode()

    ################################################################################################

    ################################################################################################
    # Return the bitmap
    def getBitmap(self):
        """Method that return the ASCII Bitmap of the package
        @return: str -> with the ASCII Bitmap
        """
        self.__buildBitmap()

        return self.BITMAP_HEX

    ################################################################################################

    ################################################################################################
    # return the Varray of values
    def getValuesArray(self):
        """Method that return an internal array of the package
        @return: array -> with all bits, presents or not in the bitmap
        """
        return self.BITMAP_VALUES

    ################################################################################################

    ################################################################################################

    def __raiseValueTypeError(self, bit):
        """ Raise a type error exception
            @param: bit -> bit that caused the error
            @raises: InvalidValueType -> exception with message according to
                     type error
        """
        raise InvalidValueType(
            'Error: value of type %s has invalid type' % (self.getBitType(bit))
        )

    ################################################################################################

    ################################################################################################

    def __checkBitTypeValidity(self, bit, value):
        """ Verify that a bit's value has the correct type
            @param: bit -> bit to be validated
            @param: value -> bit's value as a string
            @raises: InvalidValueType -> exception with message according to
                     type error
        """

        bitType = self.getBitValueType(bit)

        if bitType == 'a':
            if not all(x.isspace() or x.isalpha() for x in value):
                self.__raiseValueTypeError(bit)
        elif bitType == 'n':
            if not value.isdecimal():
                self.__raiseValueTypeError(bit)
        elif bitType == 'an':
            if not all(x.isspace() or x.isalnum() for x in value):
                self.__raiseValueTypeError(bit)

        # No exceptions raised, return
        return True

    ################################################################################################

    ################################################################################################
    # Receive a str and interpret it to bits and values
    def __getBitFromStr(self, strWithoutMtiBitmap):
        """Method that receive a string (ASCII) without MTI and Bitmaps (first and second), understand it and remove the bits values
        @param: str -> with all bits presents whithout MTI and bitmap
        It's a internal method, so don't call!
        """

        if self.DEBUG is True:
            print('This is the input string <%s>' % strWithoutMtiBitmap)

        offset = 0
        # jump bit 1 because it was alread defined in the "__initializeBitsFromBitmapStr"
        for cont in range(2, 129):
            if self.BITMAP_VALUES[cont] != self._BIT_DEFAULT_VALUE:
                if self.DEBUG is True:
                    print('String = %s offset = %s bit = %s' %
                          (strWithoutMtiBitmap[offset:], offset, cont))

                bitType = self.getBitType(cont)
                lenform = self.getBitLenForm(cont)

                if bitType == 'LL':
                    if lenform == 'A':
                        lenoffset = 2
                        valueSize = int(strWithoutMtiBitmap[offset:offset + lenoffset])
                    elif lenform == 'E':
                        lenoffset = 2
                        valueSize = int(strWithoutMtiBitmap[offset:offset + lenoffset].decode('cp1148'))
                    elif lenform == 'P':
                        lenoffset = 1
                        valueSize = self.__LLPackToInt(strWithoutMtiBitmap[offset:offset + lenoffset])
                    else: # 'B'(CD)
                        lenoffset = 1
                        valueSize = self.__LLBCDToInt(strWithoutMtiBitmap[offset:offset + lenoffset])

                    if self.DEBUG is True:
                        print('Size of the message in LL = %s' % valueSize)

                    if valueSize > self.getBitLimit(cont):
                        print('This bit is larger than the specification.')
                        # raise ValueTooLarge("This bit is larger than the specification!")

                    if self.getBitFormat(cont) == 'P':
                        modvalueSize = self.__getPackedLen(valueSize)
                    else: # ASCII and EBCDIC have the same length
                        modvalueSize = valueSize

                    self.BITMAP_VALUES[cont] = strWithoutMtiBitmap[offset:offset+lenoffset] + strWithoutMtiBitmap[
                        offset+lenoffset:offset+lenoffset+ modvalueSize]

                    if self.DEBUG is True:
                        print('\tSetting bit %s value %s' %
                              (cont, self.BITMAP_VALUES[cont]))

                    offset += modvalueSize + lenoffset 

                elif bitType == 'LLL':
                    if lenform == 'A':
                        lenoffset = 3
                        valueSize = int(strWithoutMtiBitmap[offset:offset + lenoffset])
                    elif lenform == 'E':
                        lenoffset = 3
                        valueSize = int(strWithoutMtiBitmap[offset:offset + lenoffset].decode('cp1148'))
                    elif lenform == 'P':
                        lenoffset = 2
                        valueSize = self.__LLLPackToInt(strWithoutMtiBitmap[offset:offset + lenoffset])
                    else: # 'B'(CD)
                        lenoffset = 2
                        valueSize = self.__LLLBCDToInt(strWithoutMtiBitmap[offset:offset + lenoffset])

                    if self.DEBUG is True:
                        print('Size of the message in LLL = %s' % valueSize)

                    if valueSize > self.getBitLimit(cont):
                        raise ValueTooLarge(
                            "This bit is larger than the specification!")

                    if self.getBitFormat(cont) == 'P':
                        modvalueSize = self.__getPackedLen(valueSize)
                    else:
                        modvalueSize = valueSize

                    self.BITMAP_VALUES[cont] = strWithoutMtiBitmap[offset:offset+lenoffset] + strWithoutMtiBitmap[
                        offset+lenoffset:offset+lenoffset+modvalueSize]

                    if self.DEBUG is True:
                        print('\tSetting bit %s value %s' %
                              (cont, self.BITMAP_VALUES[cont]))

                    offset += modvalueSize + lenoffset

                elif bitType == 'LLLLLL':
                    if lenform == 'A':
                        lenoffset = 6
                        valueSize = int(strWithoutMtiBitmap[offset:offset + lenoffset])
                    elif lenform == 'E':
                        lenoffset = 6
                        valueSize = int(strWithoutMtiBitmap[offset:offset + lenoffset].decode('cp1148'))
                    elif lenform == 'P':
                        lenoffset = 3
                        valueSize = self.__LLLLLLPackToInt(strWithoutMtiBitmap[offset:offset + lenoffset])
                    else: # 'B'(CD)
                        lenoffset = 3
                        valueSize = self.__LLLLLLBCDToInt(strWithoutMtiBitmap[offset:offset + lenoffset])

                    if self.DEBUG is True:
                        print('Size of the message in LLLLLL = %s' % valueSize)

                    if valueSize > self.getBitLimit(cont):
                        raise ValueTooLarge(
                            "This bit is larger than the specification!")

                    if self.getBitFormat(cont) == 'P':
                        modvalueSize = self.__getPackedLen(valueSize)
                    else:
                        modvalueSize = valueSize

                    self.BITMAP_VALUES[cont] = strWithoutMtiBitmap[offset:offset+lenoffset] + strWithoutMtiBitmap[
                        offset+lenoffset:offset+lenoffset+modvalueSize]

                    if self.DEBUG is True:
                        print('\tSetting bit %s value %s' %
                              (cont, self.BITMAP_VALUES[cont]))

                    offset += modvalueSize + lenoffset

                # if self.getBitType(cont) == 'LLLL':
                # valueSize = int(strWithoutMtiBitmap[offset:offset +4])
                # if valueSize > self.getBitLimit(cont):
                # raise ValueTooLarge("This bit is larger than the specification!")
                # self.BITMAP_VALUES[cont] = '(' + strWithoutMtiBitmap[offset:offset+4] + ')' + strWithoutMtiBitmap[offset+4:offset+4+valueSize]
                # offset += valueSize + 4

                elif bitType == 'N' or bitType == 'A' or bitType == 'ANS' or \
                   bitType == 'B' or bitType == 'AN':

                    origvalueSize = self.getBitLimit(cont)

                    if self.getBitFormat(cont) == 'P':
                        modvalueSize = self.__getPackedLen(origvalueSize)
                    else:
                        modvalueSize = origvalueSize

                    value = strWithoutMtiBitmap[offset:modvalueSize + offset]

                    #self.__checkBitTypeValidity(cont, value)
                    self.BITMAP_VALUES[cont] = value

                    if self.DEBUG is True:
                        print('\tSetting bit %s value %s' %
                              (cont, self.BITMAP_VALUES[cont]))

                    offset += modvalueSize

    ################################################################################################

    ################################################################################################
    #Parse a Int to LLBCD length
    def __IntToLLBCD(self,LLlen_int):
       return binascii.unhexlify('{0:02d}'.format(int(LLlen_int)))
    ################################################################################################

    ################################################################################################
    #Parse a LLBCD length to Int
    def __LLBCDToInt(self,LLlen_bcd):
       return LLlen_bcd[0]//16 * 10 + LLlen_bcd[0]%16
    ################################################################################################

    ################################################################################################
    #Parse a Int to LLLBCD length
    def __IntToLLLBCD(self,LLLlen_int):
       return binascii.unhexlify('{0:04d}'.format(int(LLLlen_int)))
    ################################################################################################

    ################################################################################################
    #Parse a LLLBCD length to Int
    def __LLLBCDToInt(self,LLLlen_bcd):
       return LLLlen_bcd[0]%16*100 + LLLlen_bcd[1]//16*10 + LLLlen_bcd[1]%16
    ################################################################################################

    ################################################################################################
    #Parse a Int to LLLLLLBCD length
    def __IntToLLLLLLBCD(self,LLLLLLlen_int):
       return binascii.unhexlify('{0:06d}'.format(int(LLLLLLlen_int)))
    ################################################################################################

    ################################################################################################
    #Parse a LLLLLLBCD length to Int
    def __LLLLLLBCDToInt(self,LLLLLLlen_bcd):
       return LLLLLLlen_bcd[0]//16*100000 + LLLLLLlen_bcd[0]%16*10000 + LLLLLLlen_bcd[1]//16*1000 + LLLLLLlen_bcd[1]%16*100 + LLLLLLlen_bcd[2]//16*10 + LLLLLLlen_bcd[2]%16
    ################################################################################################

    ################################################################################################
    #Parse a Int to LLPack length
    def __IntToLLPack(self,LLlen_int):
        return binascii.unhexlify('{0:02x}'.format(int(LLlen_int)))
    ################################################################################################

    ################################################################################################
    #Parse a Int to LLLPack length
    def __IntToLLLPack(self,LLLlen_int):
        return binascii.unhexlify('{0:04x}'.format(int(LLLlen_int)))
    ################################################################################################

    ################################################################################################
    #Parse a Int to LLLLLLPack length
    def __IntToLLLLLLPack(self,LLLLLLlen_int):
        return binascii.unhexlify('{0:06x}'.format(int(LLLLLLlen_int)))
    ################################################################################################

    ################################################################################################
    #Parse a LLPack length to Int
    def __LLPackToInt(self,LLlen_pack):
        return LLlen_pack[0]
    ################################################################################################

    ################################################################################################
    #Parse a LLLPack length to Int
    def __LLLPackToInt(self,LLLlen_pack):
        return LLLlen_pack[0]%16*256 + LLLlen_pack[1]
    ################################################################################################

    ################################################################################################
    #Parse a LLLLLLPack length to Int
    def __LLLLLLPackToInt(self,LLLLLLlen_pack):
        return LLLLLLlen_pack[0]*256*256 + LLLLLLlen_pack[1]*256 + LLLLLLlen_pack[2]
    ################################################################################################

    ################################################################################################
    #Get packed equivalent size
    def __getPackedLen(self,origlen):
       if origlen % 2 == 0:
           packed_len = int(origlen/2)
       else:
           packed_len = int((origlen+1)/2)
       return packed_len
    ################################################################################################

    ################################################################################################
    #Get packed equivalent size
    def __getUnpackedLen(self,origlen):
       return self.__getPackedLen(origlen)*2
    ################################################################################################

    ################################################################################################
    # Parse a ASCII iso to object
    def setIsoContent(self, iso):
        """Method that receive a complete ISO8583 string (ASCII) understand it and remove the bits values
        Example:
            iso = '0210B238000102C080040000000000000002100000000000001700010814465469421614465701081100301000000N399915444303500019991544986020   Value not allowed009000095492'
            i2 = ISO8583()
            # in this case, we need to redefine a bit because default bit 42 is LL and in this specification is "N"
            # the rest remain, so we use "get" :)
            i2.redefineBit(42, i2.getSmallBitName(42), i2.getLargeBitName(42), 'N', i2.getBitLenForm(42), i2.getBitLimit(42), i2.getBitValueType(42), i2.getBitFormat(42) )
            i2.setIsoContent(iso2)
            print ('Bitmap = %s' %i2.getBitmap())
            print ('MTI = %s' %i2.getMTI() )

            print ('This ISO has bits:')
            v3 = i2.getBitsAndValues()
            for v in v3:
                print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))

        @param: str -> complete ISO8583 string
        @raise: InvalidIso8583 Exception
        """

        if self.MTI_format == 'A' or self.MTI_format == 'E':
            mti_len = 4
        else:
            mti_len = 2

        if self.BITMAP_format == 'A' or self.BITMAP_format == 'E':
            bitmap_min_size = 16
        else:
            bitmap_min_size = 8

        if len(iso) < (mti_len + bitmap_min_size + self.hdrlen):
            raise InvalidIso8583('This is not a valid iso!!')
        if self.DEBUG is True:
            print('ASCII to process <%s>' % iso)

        if self.hdrlen > 0:
            self.hdr = iso[0:self.hdrlen]
        if self.DEBUG is True:
            print('Header found was %s' % self.hdr)

        self.__setMTIFromStr(iso[self.hdrlen:])
        if self.MTI_format == 'A' or self.MTI_format == 'E':
            isoT = iso[self.hdrlen + 4:]
        else:
            isoT = iso[self.hdrlen + 2:]
        self.__getBitmapFromStr(isoT)
        self.__initializeBitsFromBitmapStr(self.BITMAP_HEX)
        if self.DEBUG is True:
            print('This is the array of bits (before) %s ' %
                  self.BITMAP_VALUES)

        if self.BITMAP_format == 'A' or self.BITMAP_format == 'E':
            bitmap_size = len(self.BITMAP_HEX)
        else:
            bitmap_size = int(len(self.BITMAP_HEX)/2)

        self.__getBitFromStr(iso[self.hdrlen + mti_len + bitmap_size:])
        if self.DEBUG is True:
            print('This is the array of bits (after) %s ' % self.BITMAP_VALUES)

    ################################################################################################

    ################################################################################################
    # Method that compare 2 isos
    def __cmp__(self, obj2):
        """Method that compare two objects in "==", "!=" and other things
        Example:
            p1 = ISO8583()
            p1.setMTI('0800')
            p1.setBit(2,2)
            p1.setBit(4,4)
            p1.setBit(12,12)
            p1.setBit(17,17)
            p1.setBit(99,99)

            #get the rawIso and save in the iso variable
            iso = p1.getRawIso()

            p2 = ISO8583()
            p2.setIsoContent(iso)

            print ('Is equivalent?')
            if p1 == p1:
                print ('Yes :)')
            else:
                print ('Noooooooooo :(')

        @param: obj2 -> object that will be compared
        @return: <0 if is not equal, 0 if is equal
        """
        ret = -1  # By default is different
        if (self.getMTI() == obj2.getMTI()) and (self.getBitmap() == obj2.getBitmap()) and (
                self.getValuesArray() == obj2.getValuesArray()):
            ret = 0

        return ret

    ################################################################################################

    ################################################################################################
    # Method that return a array with bits and values inside the iso package
    def getBitsAndValues(self):
        """Method that return an array of bits, values, types etc.
            Each array value is a dictionary with: {'bit':X ,'type': Y, 'value': Z} Where:
                bit: is the bit number
                type: is the bit type
                value: is the bit value inside this object
            so the Generic array returned is:  [ (...),{'bit':X,'type': Y, 'value': Z}, (...)]

        Example:
            p1 = ISO8583()
            p1.setMTI('0800')
            p1.setBit(2,2)
            p1.setBit(4,4)
            p1.setBit(12,12)
            p1.setBit(17,17)
            p1.setBit(99,99)

            v1 = p1.getBitsAndValues()
            for v in v1:
                print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))

        @return: array of values.
        """
        ret = []
        for cont in range(2, 129):
            if self.BITMAP_VALUES[cont] != self._BIT_DEFAULT_VALUE:
                _TMP = {}
                _TMP['bit'] = "%d" % cont
                _TMP['type'] = self.getBitType(cont)
                _TMP['value(raw)'] = self.BITMAP_VALUES[cont]
                _TMP['value(decoded)'] = self.getBit(cont)
                ret.append(_TMP)
        return ret

    ################################################################################################

    ################################################################################################
    # Method that return a array with bits and values inside the iso package
    def getBit(self, bit):
        """Return the value of the bit
        @param: bit -> the number of the bit that you want the value
        @raise: BitNonexistent Exception, BitNotSet Exception
        """

        if bit < 1 or bit > 128:
            raise BitNonexistent("Bit number %s dosen't exist!" % bit)

        # Is that bit set?
        isThere = False
        arr = self.__getBitsFromBitmap()

        if self.DEBUG is True:
            print('This is the array of bits inside the bitmap %s' % arr)

        for v in arr:
            if v == bit:
                bitType = self.getBitType(bit)
                value = self.BITMAP_VALUES[bit]
                lenform = self.getBitLenForm(bit)
                if bitType == 'LL':
                    if lenform == 'A':
                        offset = 2
                        valueSize = int(value[0:0+offset])
                    elif lenform == 'E':
                        offset = 2
                        valueSize = int(value[0:0+offset].decode('cp1148'))
                    elif lenform == 'P':
                        offset = 1
                        valueSize = self.__LLPackToInt(value[0:0+offset])
                    else: # B(CD)
                        offset = 1
                        valueSize = self.__LLBCDToInt(value[0:0+offset])
                elif bitType == 'LLL':
                    if lenform == 'A':
                        offset = 3
                        valueSize = int(value[0:0+offset])
                    elif lenform == 'E':
                        offset = 3
                        valueSize = int(value[0:0+offset].decode('cp1148'))
                    elif lenform == 'P':
                        offset = 2
                        valueSize = self.__LLLPackToInt(value[0:0+offset])
                    else: # B(CD)
                        offset = 2
                        valueSize = self.__LLLBCDToInt(value[0:0+offset])
                else: # Fixed length field
                    offset = 0

                isThere = True
                break

        if isThere:
            data_form = self.getBitFormat(bit)
            if data_form == "A":
                return value[offset:].decode()
            elif data_form == "E":
                return value[offset:].decode('cp1148')
            else: # Must be packed, so has possible padding to be stripped
                unpacked_data = binascii.hexlify(value[offset:])
                if bitType == 'LL' or bitType == 'LLL':
                   return unpacked_data[0:valueSize].decode()
                else: # Must be bitType 'N' or 'B'- possibly left-padded with a zero
                   if self.getBitLimit(bit) % 2 == 0:
                       return unpacked_data[0:].decode()
                   else: # Skip the leading padding '0'
                       return unpacked_data[1:].decode()
        else:
            raise BitNotSet("Bit number %s was not set!" % bit)

    ################################################################################################

    ################################################################################################
    # Method that returns a timestamp in YYMMDDhhmmss format
    def getYYMMDDhhmmss(self):
        """Return the current date/time in YYMMDDhhmmss format
        """
        return time.strftime('%y%m%d%H%M%S')
    ################################################################################################

    ################################################################################################
    # Method that return a timestamp in MMDDhhmmss format
    def getMMDDhhmmss(self):
        """Return the current date/time in MMDDhhmmss format
        """
        return time.strftime('%m%d%H%M%S')
    ################################################################################################

    ################################################################################################
    # Method that return a timestamp in YYMMDD format
    def getYYMMDD(self):
        """Return the current date in YYMMDD format
        """
        return time.strftime('%y%m%d')
    ################################################################################################

    ################################################################################################
    # Method that return a timestamp in MMDD format
    def getMMDD(self):
        """Return the current date in MMDD format
        """
        return time.strftime('%m%d')
    ################################################################################################

    ################################################################################################
    # Method that return a timestamp in hhmmss format
    def gethhmmss(self):
        """Return the current date in hhmmss format
        """
        return time.strftime('%H%M%S')
    ################################################################################################

    ################################################################################################
    # Method that return ISO8583 to TCPIP network form, with the size in the beginning.
    def getNetworkISO(self, bigEndian=True):
        """Method that return ISO8583 ASCII package with the size in the beginning
        By default, it return the package with size represented with big-endian.
        Is the same that:
            import struct
            (...)
            iso = ISO8583()
            iso.setBit(3,'300000')
            (...)
            ascii = iso.getRawIso()
            # Example: big-endian
            # To little-endian, replace '!h' with '<h'
            netIso = struct.pack('!h',len(iso))
            netIso += ascii
            # Example: big-endian
            # To little-endian, replace 'iso.getNetworkISO()' with 'iso.getNetworkISO(False)'
            print ('This <%s> the same that <%s>' % (iso.getNetworkISO(),netIso))

        @param: bigEndian (True|False) -> if you want that the size be represented in this way.
        @return: size + ASCII ISO8583 package ready to go to the network!
        @raise: InvalidMTI Exception
        """

        netIso = "".encode()
        asciiIso = self.getRawIso()

        if bigEndian:
            netIso = struct.pack('!h', len(asciiIso))
            if self.DEBUG is True:
                print('Pack Big-endian')
        else:
            netIso = struct.pack('<h', len(asciiIso))
            if self.DEBUG is True:
                print('Pack Little-endian')

        netIso += asciiIso

        return netIso

    ################################################################################################

    ################################################################################################
    # Method that recieve a ISO8583 ASCII package in the network form and parse it.
    def setNetworkISO(self, iso, bigEndian=True):
        """Method that receive sie + ASCII ISO8583 package and transfor it in the ISO8583 object.
            By default, it recieve the package with size represented with big-endian.
            Is the same that:
            import struct
            (...)
            iso = ISO8583()
            iso.setBit(3,'300000')
            (...)
            # Example: big-endian
            # To little-endian, replace 'iso.getNetworkISO()' with 'iso.getNetworkISO(False)'
            netIso = iso.getNetworkISO()
            newIso = ISO8583()
            # Example: big-endian
            # To little-endian, replace 'newIso.setNetworkISO()' with 'newIso.setNetworkISO(False)'
            newIso.setNetworkISO(netIso)
            #Is the same that:
            #size = netIso[0:2]
            ## To little-endian, replace '!h' with '<h'
            #size = struct.unpack('!h',size )
            #newIso.setIsoContent(netIso[2:size])
            arr = newIso.getBitsAndValues()
            for v in arr:
                print ('Bit %s Type %s Value = %s' % (v['bit'],v['type'],v['value']))

            @param: iso -> str that represents size + ASCII ISO8583 package
            @param: bigEndian (True|False) -> Codification of the size.
            @raise: InvalidIso8583 Exception
        """

        if self.MTI_format == 'A' or self.MTI_format == 'E':
            mti_len = 4
        else:
            mti_len = 2

        if self.BITMAP_format == 'A' or self.BITMAP_format == 'E':
            bitmap_min_size = 16
        else:
            bitmap_min_size = 8

        if len(iso) < (mti_len + bitmap_min_size + 4):
            raise InvalidIso8583('This is not a valid iso!! Invalid Size')

        size = iso[0:2]
        if bigEndian:
            size = struct.unpack('!h', size)
            if self.DEBUG is True:
                print('Unpack Big-endian')
        else:
            size = struct.unpack('<h', size)
            if self.DEBUG is True:
                print('Unpack Little-endian')

        if len(iso) != (size[0] + 2):
            raise InvalidIso8583(
                'This is not a valid iso!! The ISO8583 ASCII(%s) is less than the size %s!' % (len(iso[2:]), size[0]))

        self.setIsoContent(iso[2:])

    ################################################################################################
