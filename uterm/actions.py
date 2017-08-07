from __future__ import unicode_literals
import os

import curses

from .comms import Comms
from . import browser


class Uploader(object):

    def __init__(self, name, update_func=None):
        self.path = os.path.normpath(name)
        self.name = os.path.basename(name)
        self.update_func = update_func

    def update(self, amount):
        if self.update_func:
            self.update_func(amount)

    def __call__(self, terminal):
        temp_name = '_{}'.format(self.name)
        comms = Comms(terminal, silent=True)
        comms.send('_fh = open(%r, "wb")' % temp_name)
        comms.send('_fhw = lambda text: _fh.write(text) and None')
        with open(self.path, 'rb') as fh:
            fh.seek(0, 2)
            total = float(fh.tell())
            fh.seek(0)
            self.update(0)
            while True:
                data = fh.read(60)
                if not data:
                    self.update(1)
                    break
                self.update(fh.tell() / total)
                comms.send(b'_fhw(' + repr(data).encode() + b')')
            comms.send('_fh.close()')
            comms.import_module('os')
            comms.send(
                # Note the explicit second \r to ensure the statement is
                # executed.
                b'if %r in os.listdir(): os.remove(%r)\r' % (
                    self.name, self.name))
            comms.send('os.rename(%r, %r)' % (temp_name, self.name))
            module, ext = os.path.splitext(self.name)
            if ext in ('.py', '.mpy'):
                comms.import_module('sys')
                # Note the explicit second \r to ensure the statement is
                # executed.
                comms.send('if %r in sys.modules: del sys.modules[%r]\r' % (
                    module, module))

        return True


def browse(terminal):
    window = curses.newwin(*terminal.window.getmaxyx())
    window.keypad(1)
    curses.panel.new_panel(window)
    py_browser = browser.PyBrowser()
    action, obj = py_browser.run(window)
    if action == 'SELECT':
        width = terminal.window.getmaxyx()[1] - 8
        dialog = curses.newwin(4, width, 3, 4)
        dialog.border()
        width -= 4
        dialog.addstr(1, 3, 'Uploading {}...'.format(obj.name))

        def progress(amount):
            dialog.addstr(2, 3, '#' * int(width * amount))
            dialog.refresh()

        panel = curses.panel.new_panel(dialog)
        panel.top()
        dialog.refresh()
        upload = Uploader(obj.name, progress)
        upload(terminal)
        if os.path.basename(obj.name) in ('main.py', 'boot.py'):
            terminal.tx(b'\x03\x04')
        return True


def reset(terminal, hard=True):
    if hard:
        comms = Comms(terminal)
        comms.import_module('machine')
        comms.send('machine.reset()')
    else:
        terminal.tx(b'\x03\x04')
    return True


def remote(terminal):
    comms = Comms(terminal, silent=True)
    window = curses.newwin(*terminal.window.getmaxyx())
    window.keypad(1)
    curses.panel.new_panel(window)
    comms.import_module('os')
    cwd = comms.json('os.getcwd()')
    upy_browser = browser.uPyBrowser(comms=comms)
    while True:
        upy_browser.root_name = '/'
        if cwd and cwd != '/':
            upy_browser.root_name += ' (working directory: %s)' % cwd
        upy_browser.reset()
        action, obj = upy_browser.run(window)
        if action == 'DELETE':
            if obj.name in ('/', '/boot.py'):
                continue
            if not obj.children():
                if (
                        obj.container and cwd and (
                            cwd == obj.name or
                            cwd.startswith('%s/' % obj.name))):
                    comms.send('os.chdir("/")')
                    cwd = '/'
                comms.send('os.remove(%r)' % obj.name)
            continue
        elif action == 'SELECT':
            if obj.container:
                comms.send('os.chdir(%r)' % obj.name)
                cwd = obj.name
                continue
        break
