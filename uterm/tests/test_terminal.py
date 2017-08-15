from __future__ import unicode_literals
from unittest import TestCase
try:
    from unittest import mock
except ImportError:
    import mock

from ..terminal import Terminal


class TerminalTest(TestCase):

    def test_init(self):
        mock_port = mock.Mock()
        Terminal(mock_port)

    def test_running(self):
        mock_port = mock.Mock()
        terminal = Terminal(mock_port)
        mock_port.is_open = True
        self.assertTrue(terminal.running)
        mock_port.is_open = False
        self.assertFalse(terminal.running)


class TXTest(TestCase):
    CTRL_A = b'\x01'
    ESC = b'\x1b'
    CTRL_Q = b'\x11'
    CTRL_X = b'\x18'

    def test_basic(self):
        mock_port = mock.Mock()
        terminal = Terminal(mock_port)
        terminal.tx(b'test')
        mock_port.write.assert_called_with(b'test')

    def test_rewrite_newline(self):
        mock_port = mock.Mock()
        terminal = Terminal(mock_port)
        terminal.tx(b'\n')
        mock_port.write.assert_called_with(b'\r')

    def test_menu_key(self):
        mock_port = mock.Mock()
        terminal = Terminal(mock_port)
        terminal.menu = mock.Mock()
        terminal.tx(self.ESC)
        mock_port.write.assert_not_called()
        terminal.menu.assert_any_call()

    def test_escape_key(self):
        mock_port = mock.Mock()
        terminal = Terminal(mock_port)
        terminal.tx(self.CTRL_A)
        mock_port.write.assert_not_called()
        # Second call will pass any character, such as ctrl-a...
        terminal.tx(self.CTRL_A)
        mock_port.write.assert_called_with(self.CTRL_A)
        # or the escape key...
        terminal.tx(self.CTRL_A)
        terminal.tx(self.ESC)
        mock_port.write.assert_called_with(self.ESC)
        # or any other normal key.
        terminal.tx(self.CTRL_A)
        terminal.tx(b' ')
        mock_port.write.assert_called_with(b' ')

    def test_escape_quit(self):
        mock_port = mock.Mock()
        terminal = Terminal(mock_port)
        # Non "quit" keys don't quit.
        terminal.tx(self.CTRL_A)
        terminal.tx(b' ')
        mock_port.close.assert_not_called()
        for code in (self.CTRL_Q, self.CTRL_X, b'q', b'x'):
            mock_port = mock.Mock()
            terminal = Terminal(mock_port)
            terminal.tx(self.CTRL_A)
            terminal.tx(code)
            mock_port.close.assert_any_call()


class RXTest(TestCase):

    def test_not_running(self):
        mock_port = mock.Mock()
        terminal = Terminal(mock_port)
        mock_port.is_open = False
        self.assertFalse(terminal.running)
        self.assertEqual(terminal.rx(), '')

    def test_not_waiting(self):
        mock_port = mock.Mock()
        terminal = Terminal(mock_port)
        mock_port.inWaiting.return_value = False
        self.assertEqual(terminal.rx(), '')

    def test_read(self):
        mock_port = mock.Mock()
        terminal = Terminal(mock_port, log=mock.Mock())
        expected = b'test'
        mock_port.read.return_value = expected
        mock_port.inWaiting.return_value = len(expected)

        # Set up some things created in __call__
        terminal.window = mock.Mock()
        terminal.screen_stream = mock.Mock()
        terminal.screen = mock.MagicMock()
        terminal.screen.display = ['']
        terminal.screen.dirty.__iter__.return_value = range(1)

        range(1)

        self.assertEqual(terminal.rx(), expected)
