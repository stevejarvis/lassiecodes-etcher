#!/usr/bin/env python3

import logging
import ndef
import RPi.GPIO as GPIO
from ntag_tlv import MessageTlv, TerminatorTlv, LockCtrlTlv

import pn532.pn532 as nfc
from pn532 import *

logging.basicConfig(level=logging.INFO)

pn532 = PN532_I2C(debug=False, reset=20, req=16)

# Configure PN532 to communicate with NTAG215 cards
pn532.SAM_configuration()

def _wait_for_card():
    print('Waiting for RFID/NFC card to write to!')
    while True:
        # Check if a card is available to read
        uid = pn532.read_passive_target(timeout=0.5)
        print('.', end="")
        # Try again if no card is available.
        if uid is not None:
            break
    print('Found card with UID:', [hex(i) for i in uid])

def _write_chunked(b):
    '''
    Write a byte string to the card page by page.
    '''
    # Pad with nulls to length
    while len(b) % 4 != 0:
        b += b'\x00'

    # Block 4 is first user-writable block.
    block_number = 4
    for i in range(0, len(b), 4):
        data = b[i:i+4]  # [)

        try:
            pn532.ntag2xx_write_block(block_number, data)
            rdata = pn532.ntag2xx_read_block(block_number)
            if rdata == data:
                logging.info(f'SUCCESS wrote block {block_number} successfully: {data}')
            else:
                logging.error(f'ERROR wrote block {block_number} badly: {data} != {rdata}')
        except nfc.PN532Error as e:
            logging.error(e.errmsg)
            break
        block_number += 1

def write_tag(phone):
    '''
    Write the tag with the info we want.
    '''
    _wait_for_card()

    lock_record = LockCtrlTlv()
    tel_record = MessageTlv([ndef.UriRecord(f'tel:{phone}')])
    term_record = TerminatorTlv()
    raw_msg = b''.join([record.to_bytes() for record in [lock_record, tel_record, term_record]])
    logging.info(f'Raw: {raw_msg}')
    _write_chunked(raw_msg)


if __name__ == '__main__':
    import sys
    try:
        number = sys.argv[1]
    except:
        number = '8675309'
    print(f'Writing {number}')
    write_tag(number)

    GPIO.cleanup()

