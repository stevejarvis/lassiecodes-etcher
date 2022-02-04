'''
TLV classes to help with the data writing.
https://developer.nordicsemi.com/nRF_Connect_SDK_dev/doc/PR-4304/nrfxlib/nfc/doc/type_2_tag.html#data
'''
import ndef


class NtagTlv(object):

    def to_bytes(self):
        raise NotImplementedError


class MessageTlv(NtagTlv):

    def __init__(self, records):
        '''
        Records is some iterable of ndeflib records.
        '''
        self.tag = b'\x03'
        self.records = records

    def to_bytes(self):
        '''
        Return a byte array.
        '''
        # First the T for the TLV
        b = self.tag
        # Then the length. We're assuming short records here, so length is just 1 byte.
        # Serialize the records so we know how long. 
        record_bytes = b''.join(ndef.message_encoder(self.records))
        # Then the L is that long plus one more for the type and flags.
        b += bytes([len(record_bytes)])
        # Next the V is the records themselves.
        b += record_bytes
        return b


class LockCtrlTlv(NtagTlv):

    def __init__(self):
        self.tag = b'\x01'
    
    def to_bytes(self):
        '''
        Targeted specifically at ntag213. Actually right as they come out of the
        box and at the moment I don't plan on locking records, so this is more a 
        learning experience than actually necessary to set.

        Out of box memory: https://www.nxp.com/docs/en/data-sheet/NTAG213_215_216.pdf
        '''
        b = self.tag 
        # L
        b += b'\x03'
        # And V. For deciphering these nibbles, check section 2.3.2 here is the best description I've found.
        # http://apps4android.org/nfc-specifications/NFCForum-TS-Type-2-Tag_1.1.pdf
        b += b'\xa0\x0c\x34'
        return b


class TerminatorTlv(NtagTlv):

    def __init__(self):
        self.tag = b'\xFE'

    def to_bytes(self):
        '''
        Terminator is special, it's not really TLV, but docs call it one.
        '''
        return self.tag
