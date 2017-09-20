"""
A micropython-friendly terminal

Usage:
    uterm [--log FILE]
          [-p <port> | --port=<port>]
          [-b <rate> | --baudrate=<rate>]
          [<command>] [<args>...]

Options:
    --log FILE            Log all incoming data to a file
    -p --port <port>      Port to connect to [default: /dev/ttyUSB0]
    -b --baudrate <rate>  Baud rate to connect with [default: 115200]

If no command is given, an interactive terminal is launched.
Otherwise, the following commands are valid:
    get <file>   Display the contents of a file
    exec <cmd>   Execute any python command(s)
    ls [<path>]  List files
    cd <path>    Change directory
    pwd          Show the current working directory

For command help, run:
    uterm <command> --help
"""
import json
import sys

import serial
import uterm
from docopt import docopt
from uterm.terminal import Terminal


def run_uterm(terminal):
    try:
        terminal.run()
    except IOError as e:
        if e.errno != 5:
            raise
        print('Lost connection.')


def _exec(terminal, command):
    terminal.send_command(command)
    while True:
        data = terminal.rx(silent=True, readline=True)
        if not data or data == '>>> ':
            break
        sys.stdout.write(data)


def uterm_ls(terminal, args):
    """
    List remote files and directories.

    usage: uterm ls [<path>]
    """
    path = args['<path>'] or ''
    terminal.send_command(
        'import json;import os;d=os.listdir({!r});'
        'd.sort(key=lambda p: (os.stat(p)[0] != 0o040000, p));'
        'print(json.dumps(d))'.format(path))
    data = terminal.rx(silent=True, readline=True)
    for path in json.loads(data):
        print(path)


def uterm_pwd(terminal, args):
    """
    Print the current remote working directory.

    usage: uterm pwd
    """
    _exec(terminal, 'import os;print(os.getcwd())')


def uterm_cd(terminal, args):
    """
    Change the remote working directory.

    usage: uterm cd <path>
    """
    _exec(terminal, 'import os;os.chdir({!r})'.format(args['<path>']))


def uterm_get(terminal, args):
    """
    Print the contents of a remote file.

    usage: uterm get [--] <file>
    """
    command = (
        'with open("{}") as f:\n'
        '  print(f.read())').format(args['<file>'])
    _exec(terminal, command)


def uterm_exec(terminal, args):
    """
    Remotely execute any python command (or commands).

    usage: uterm exec <command>
    """
    _exec(terminal, args['<command>'])


def main():
    args = docopt(__doc__, version=uterm.__version__, options_first=True)
    port = serial.Serial(args['--port'], int(args['--baudrate']))
    log = open(args['--log'], 'wb') if args['--log'] else None
    terminal = Terminal(port, log=log)

    try:
        command = args['<command>']
        if command:
            func = globals().get('uterm_{}'.format(command))
            if not func:
                exit('{!r} is not a uterm command.'.format(command))
            argv = [command] + args['<args>']
            args = docopt(func.__doc__, argv=argv)
            func(terminal, args)
        else:
            run_uterm(terminal)
    finally:
        if log:
            log.close()


if __name__ == '__main__':
    main()
