import asyncio
import random
import struct
import time

BYTE_ORDER = '<'
PAYLOAD_FORMAT = 'Ic'

async def start_lightbrush_client(port=9111):
    try:
        _reader, writer = await asyncio.open_connection('127.0.0.1', port)

        value = random.randint(0, 200)
        message = struct.pack(BYTE_ORDER + PAYLOAD_FORMAT, value, b'\n' )
        writer.write(message)

        print(f'  Sent: {value:<5}\r', end='', flush=True)
    finally:
        if writer:
            writer.close()

if __name__ == '__main__':

    print('Starting simulator...')
    print('Sending random integers every 2 seconds...')

    while True:
        asyncio.run(start_lightbrush_client())
        time.sleep(2)
    
