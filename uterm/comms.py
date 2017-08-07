from __future__ import unicode_literals
import io
import json
import time

import pyte


class Comms(object):

    def __init__(self, terminal, silent=False):
        self.terminal = terminal
        self.terminal.tx(b'\x03')
        self.imports = []
        self.silent = silent

    def import_module(self, name, silent=None):
        if name in self.imports:
            return
        self.send('import %s' % name, silent=silent)
        self.imports.append(name)

    def json(self, command, silent=None):
        self.import_module('json', silent=silent)
        output = ('print(json.dumps(%s))' % command.strip()).encode()
        response = self.send(output, silent=silent)[len(output):]
        try:
            return json.loads(response)
        except ValueError:
            pass

    def send(self, text, silent=None):
        if hasattr(text, 'encode'):
            text = text.encode()
        text += b'\r'
        self.terminal.tx(text)
        # Wait for ok
        stream = pyte.ByteStream()
        width = 1000
        screen = pyte.Screen(width, 10)
        stream.attach(screen)
        incoming = io.BytesIO()
        if silent is None:
            silent = self.silent
        timeout = time.time() + 3
        while True:
            if time.time() > timeout:
                raise ValueError('Timeout')
            data = self.terminal.rx(silent=silent)
            if not data:
                continue
            stream.feed(data)
            incoming.write(data)
            incoming.seek(-4, io.SEEK_END)
            if incoming.read() == b'>>> ':
                output = io.StringIO()
                for line in screen.display:
                    line = line.strip()
                    output.write(line)
                    if len(line) < width:
                        output.write(u'\n')
                return output.getvalue().rstrip()[:-3]
