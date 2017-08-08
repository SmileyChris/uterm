from __future__ import unicode_literals
from unittest import TestCase
try:
    from unittest import mock
except ImportError:
    import mock

from .. import actions


class UploaderTest(TestCase):

    def test_init(self):
        uploader = actions.Uploader('some/path')
        self.assertEqual(uploader.name, 'path')


class BrowseTest(TestCase):

    @mock.patch('uterm.actions.curses')
    @mock.patch('uterm.actions.browser')
    def test_call(self, mock_browser, *args):
        mock_terminal = mock.Mock()
        mock_browser.PyBrowser().run.return_value = ('NOOP', None)
        mock_terminal.window.getmaxyx.return_value = (80, 24)
        actions.browse(mock_terminal)


class ResetTest(TestCase):

    def test_call(self):
        mock_terminal = mock.Mock()
        mock_terminal.rx.return_value = b'>>> '
        actions.reset(mock_terminal)
        mock_terminal.tx.assert_called_with(b'machine.reset()\r')

    def test_call_soft(self):
        mock_terminal = mock.Mock()
        actions.reset(mock_terminal, hard=False)
        mock_terminal.tx.assert_called_with(b'\x03\x04')


class RemoteTest(TestCase):

    @mock.patch('uterm.actions.curses')
    @mock.patch('uterm.actions.browser')
    def test_call(self, mock_browser, *args):
        mock_terminal = mock.Mock()
        mock_terminal.rx.return_value = b'>>> '
        mock_browser.uPyBrowser().run.return_value = ('NOOP', None)
        mock_terminal.window.getmaxyx.return_value = (80, 24)
        actions.remote(mock_terminal)
