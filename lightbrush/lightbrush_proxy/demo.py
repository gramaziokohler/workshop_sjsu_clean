import time
import requests

if __name__ == '__main__':
    ip_address = '192.168.1.67'
    session = requests.Session()

    url = 'http://' + ip_address + '/brightness?value={}'
    session.get(url.format(255))

    url = 'http://' + ip_address + '/leds?rgb=[{},{},{}]'
    r, g, b = 0, 0, 0

    while True:
        g += 1
        rc = r % 255
        gc = g % 255
        bc = b % 255
        response = session.get(url.format(rc, gc, bc))
        print('RGB: {} {} {}\r'.format(rc, gc, bc), end='', flush=True)
        time.sleep(.1)