from __future__ import unicode_literals
import argparse
import os
import time

import serial
import curses
import curses.panel
import pyte

from . import actions
from .menu import Menu


class Terminal(object):
    escape_key = b'\x01'
    menu_key = b'\x1b'

    def __init__(self, port, accept_input=True, log=None):
        self.port = port
        self.accept_input = accept_input
        self.escape_mode = None
        self.log = log

    @property
    def running(self):
        return self.port.is_open

    @running.setter
    def running(self, value):
        if not value and self.running:
            self.port.close()

    def close(self):
        self.running = False
        return True

    def menu(self):
        menu = Menu(
            'Micropython terminal',
            [
                ('Upload', actions.browse),
                ('Remote Browse', actions.remote),
                ('Reset uPy', actions.reset),
                ('Exit uterm', lambda terminal: terminal.close()),
            ])
        menu(self)

    def tx(self, data):
        if self.escape_mode:
            self.escape_mode = None
            # Exit on: ctrl-q, ctrl-x, q, x.
            if data in (b'\x11', b'\x18', b'q', b'x', b'Q', b'X'):
                self.running = False
                return
        elif data == self.escape_key:
            self.escape_mode = True
            return
        elif data == self.menu_key:
            self.menu()
            return
        if data == b'\n':
            data = b'\r'
        self.port.write(data)

    def rx(self, silent=False, readline=False):
        if not self.running:
            return ''
        if readline:
            self.port.timeout = 0.1
            incoming = self.port.readline()
        else:
            waiting = self.port.inWaiting()
            if not waiting:
                return ''
            incoming = self.port.read(waiting)
        if self.log:
            self.log.write(incoming)
        if not silent:
            self.screen_stream.feed(incoming)
            display = self.screen.display
            for i in self.screen.dirty:
                line = display[i].encode('ascii', 'replace')
                self.window.addstr(i, 0, line)
            self.screen.dirty.clear()
            c = self.screen.cursor
            self.window.move(c.y, c.x)
        return incoming

    def send_command(self, command):
        command = command.strip().replace('\n', '\r')
        self.tx(b'\x03\x05')
        self.port.flush()
        line = ''
        while not line.endswith(b'=== '):
            line += self.rx(silent=True)
        if '\r' in command:
            command += '\r\r\r'
        command += '\x04'
        self.tx(b'{}'.format(command))
        self.port.flush()
        # Read lines
        for i in range(command.count('\r')+1):
            self.rx(silent=True, readline=True)

    def loop(self):
        while self.running:
            key = ''
            t = 0
            while True:
                try:
                    key += self.window.getkey()
                    t = time.time()
                except curses.error:
                    if time.time() - t > 0.0025:
                        break
            if key:
                self.tx(key.encode())
            self.rx()

    def __call__(self, window):
        # Don't wait for input when calling getch.
        window.nodelay(1)
        # Don't interpret escape sequences, we want to send them on.
        window.keypad(0)
        self.window = window

        # Set up terminal
        y, x = window.getmaxyx()
        self.screen = pyte.DiffScreen(x-1, y)
        self.screen_stream = pyte.ByteStream()
        self.screen_stream.attach(self.screen)
        window.addstr(
            0, 0, "Welcome to uterm. If a program is running you'll "
            "want to hit ctrl-c.")
        window.move(1, 0)

        while self.running:
            try:
                self.loop()
            except KeyboardInterrupt:
                if not self.accept_input:
                    raise
                self.tx(b'\x03')

    def run(self):
        # Set shorter escape delay.
        os.environ.setdefault('ESCDELAY', '25')
        curses.wrapper(self)


def main():
    parser = argparse.ArgumentParser(
        description='Run a micropython-friendly terminal')
    parser.add_argument('--log', help="log all incoming data to a file")
    parser.add_argument(
        '-p', '--port', default='/dev/ttyUSB0',
        help="port to connect to (defaults to /dev/ttyUSB0)")
    parser.add_argument(
        '-b', '--baudrate', default='115200',
        help="baud rate to connect with (defaults to 115200)")
    args = parser.parse_args()
    port = serial.Serial(args.port, int(args.baudrate))

    log = open(args.log, 'wb') if args.log else None
    try:
        try:
            Terminal(port, log=log).run()
        finally:
            if log:
                log.close()
    except IOError as e:
        if e.errno != 5:
            raise
        print('Lost connection.')


if __name__ == '__main__':
    main()
