try:
    from utilities import is_available, URScriptHelper
except:
    from .utilities import is_available, URScriptHelper

def send_script(proxy_ip, proxy_port, ur_ip):
    ur = URScriptHelper(proxy_ip, proxy_port)

    script = "movel(p[0.407143, 0, 0.29, 2.221, -2.221, 0.000], v=0.01, r=0.001)\n"
    script += "socket_send_int(%i)\n" % 1
    script = ur.wrap_script(script)
    print(script)

    ur_available = is_available(ur_ip)

    if ur_available:
        ur.execute(ur_ip, script)


if __name__ == "__main__":
    proxy_port = 9111
    proxy_ip = "10.0.0.106"
    ur_ip = "10.0.0.10"

    send_script(proxy_ip, proxy_port, ur_ip)
