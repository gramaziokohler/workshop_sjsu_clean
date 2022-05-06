import argparse
import io
import os
import sys
import struct

import compas

try:
    from utilities import is_available, URScriptHelper
except:
    from .utilities import is_available, URScriptHelper


BYTE_ORDER = '!'
PAYLOAD_FORMAT = 'I'

def execute(proxy_ip, proxy_port, ur_ip, configurations, tool_angle_axis):
    ur = URScriptHelper(proxy_ip, proxy_port, tool_angle_axis)
    script = ur.send_configurations(configurations, velocity=0.01, radius=0.01)

    ur_available = is_available(ur_ip)

    if ur_available:
        print('UR connected, sending script...')
        try:
            sock = ur.execute(ur_ip, script)

            while True:
                data = sock.recv(4)
                if not data:
                    break

                value = struct.unpack(BYTE_ORDER + PAYLOAD_FORMAT, data)[0]
                if (value + 1) == len(configurations):
                    print('Done!')
                    return
        finally:
            if sock:
                sock.close()
    else:
        print('UR not connected!')


def load_command_file(file):
    if not os.path.exists(file):
        print(f' [!] Cannot find file={file}')
        print('     Verify the file exists and is a valid JSON file.')
        sys.exit(1)

    
    with io.open(file, 'r') as fp:
        commands = compas.json_load(fp)
        configurations = commands['configurations']

    return configurations



if __name__ == "__main__":
    proxy_port = 9111
    proxy_ip = "10.0.0.106"
    tool_angle_axis = [0,0,0,0,0,0]

    parser = argparse.ArgumentParser(description='Lightpainting controller')
    parser.add_argument(
        'file', type=str, help='light painting file containing robot points and colors')
    parser.add_argument(
        '--ur', type=str, help='IP address of the UR robot.', default='10.0.0.10')

    args = parser.parse_args()

    print()
    print('Lightpainting Controller')
    print()

    print(' [ ] Loading commands file...\r', end='', flush=True)
    configurations = load_command_file(args.file)
    print(' [✓] Loaded {} configurations'.format(len(configurations)))

    ur_ip = args.ur

    execute(proxy_ip, proxy_port, ur_ip, configurations, tool_angle_axis)
