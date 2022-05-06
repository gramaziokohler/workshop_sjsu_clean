import math
import os
import socket


def is_available(ur_ip):
    syscall = "ping -r 1 -n 1 %s"
    response = os.system(syscall % ur_ip)
    if response == 0:
        return True
    else:
        return False

INDENT = "\t"
UR_SERVER_PORT = 30002
URSCRIPT_TEMPLATE_PRE = "def program():\n"

URSCRIPT_TEMPLATE_PRE += "\ttextmsg(\">> Entering program.\")\n"
URSCRIPT_TEMPLATE_PRE += "\tPROXY_ADDRESS = \"{proxy_ip}\"\n"
URSCRIPT_TEMPLATE_PRE += "\tPROXY_PORT = {proxy_port}\n"
URSCRIPT_TEMPLATE_PRE += "\ttextmsg(PROXY_ADDRESS)\n"
URSCRIPT_TEMPLATE_PRE += "\ttextmsg(PROXY_PORT)\n"
URSCRIPT_TEMPLATE_PRE += "\tset_tcp(p{tcp})\n"
URSCRIPT_TEMPLATE_PRE += "\tsocket_open(PROXY_ADDRESS, PROXY_PORT)\n"


URSCRIPT_TEMPLATE_POST = "socket_close()\n"
URSCRIPT_TEMPLATE_POST += "\ttextmsg(\"<< Exiting program.\")\n"
URSCRIPT_TEMPLATE_POST += "end\n"
URSCRIPT_TEMPLATE_POST += "program()\n\n\n"


class URScriptHelper(object):
    def __init__(self, proxy_ip, proxy_port, tcp=[0, 0, 0, 0, 0, 0]):
        self.template_pre = URSCRIPT_TEMPLATE_PRE.format(proxy_ip=proxy_ip, proxy_port=proxy_port, tcp=tcp, indent=INDENT)

    def wrap_script(self, script):
        indented_script = '\n'.join([INDENT + line for line in script.split('\n')])
        script = self.template_pre + indented_script + URSCRIPT_TEMPLATE_POST.format(indent=INDENT)
        return script

    def send_configurations(self, configurations, velocity, radius, acceleration, startends=None):
        script = ""
        for i, config in enumerate(configurations):
            config = config.copy()

            start_or_end = startends[i]
        
            if i == 0:
                script += 'movej([%.6f, %.6f, %.6f, %.6f, %.6f, %.6f], v=%.4f, r=%.4f)\n' % tuple(config.joint_values + [velocity, radius])
            else:
                #script += 'movel([%.6f, %.6f, %.6f, %.6f, %.6f, %.6f], v=%.4f, r=%.4f)\n' % tuple(config.joint_values + [velocity, radius])
                if not start_or_end:
                    script += 'movel([%.6f, %.6f, %.6f, %.6f, %.6f, %.6f], v=%.4f, r=%.4f)\n' % tuple(config.joint_values + [velocity, radius])
                else:
                    script += 'movel([%.6f, %.6f, %.6f, %.6f, %.6f, %.6f], a=%.4f, v=%.4f)\n' % tuple(config.joint_values + [acceleration, velocity])

            script += 'socket_send_int(%i)\n' % i
            script += 'textmsg("%i")\n' % i

        return self.wrap_script(script)

    def execute(self, ur_ip, script, sock=None):
        try:
            if not sock:
                sock = socket.create_connection((ur_ip, UR_SERVER_PORT), timeout=2)

            sock.send(script.encode('ascii'))
            print("Script sent to {} on port {}".format(ur_ip, UR_SERVER_PORT))

            return sock
        except socket.timeout:
            print("UR with ip {} not available on port {}".format(ur_ip, UR_SERVER_PORT))
            raise


if __name__ == '__main__':
    from compas.robots import Configuration

    proxy_ip, proxy_port = '10.0.0.99', 9111
    ur_ip = '10.0.0.10'
    ur = URScriptHelper(proxy_ip, proxy_port)
    configs = [
        Configuration.from_revolute_values([-0.336346, -1.81684, 1.79533, -1.53407, -1.56666, 1.22421]),
    ]
    script = ur.send_configurations(configs, velocity=0.01, radius=0.01)
    print(script)

    """
    script = ""
    script += "def program():\n"
    script += "\ttextmsg(\">> Entering program.\")\n"
    script += "\ttextmsg(\"<< Exiting program.\")\n"
    script += "end\n"
    script += "program()\n\n\n"
    print(script)
    """
    sock = ur.execute(ur_ip, script)
    sock.close()