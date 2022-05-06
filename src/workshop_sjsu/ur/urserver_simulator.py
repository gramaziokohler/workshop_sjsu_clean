import argparse
import asyncio
import functools
import re
import socket
import struct

BYTE_ORDER = '!'
PAYLOAD_FORMAT = 'I'


def get_current_ip_address():
    """This retrieves the IP address of the default route."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(('10.255.255.255', 1))
        ip = sock.getsockname()[0]
    finally:
        sock.close()
    return ip


async def handle_tcp_request(callback, reader, writer):
    try:
        while True:
            data = await reader.readline()
            addr, port = writer.get_extra_info('peername')

            if len(data) == 0:
                return

            print(f' [ ] Received {len(data)} bytes from {addr}:{port}', end='', flush=True)
            callback(data, writer)
            print(f' [✓]')

    finally:
        if writer:
            writer.close()


async def start_server(callback, port=30002):
    print(' [ ] Starting TCP server...\r', end='', flush=True)
    server = await asyncio.start_server(functools.partial(handle_tcp_request, callback), '0.0.0.0', port)
    addr, port = server.sockets[0].getsockname()
    print(f' [✓] Started TCP server on {addr}:{port}')

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UR Server simulator')

    args = parser.parse_args()

    print()
    print('UR Server Simulator')
    print()

    ip_address = get_current_ip_address()
    print(' [✓] Local IP address: {}'.format(ip_address))

    regex = re.compile(r"(textmsg)\(\"(.+)\"\)|(socket_send_int)\((\d+)\)")

    def urserver_callback(data, writer):
        data = data.decode('ascii').strip()
        match = regex.match(data)

        if match:
            for group in range(1, len(match.groups()))[::2]:
                if match.group(group) is not None:
                    cmd = match.group(group)
                    params = match.group(group + 1)
                    if cmd == 'textmsg':
                        print(f'| {params}', end='', flush=True)
                    if cmd == 'socket_send_int':
                        response = struct.pack(BYTE_ORDER + PAYLOAD_FORMAT, int(params))
                        writer.write(response)
        
        print('\r', end='', flush=True)

    asyncio.run(start_server(urserver_callback))
