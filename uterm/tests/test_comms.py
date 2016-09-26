from __future__ import unicode_literals
from unittest import TestCase
try:
    from unittest import mock
except ImportError:
    import mock

from ..comms import Comms


class CommsTest(TestCase):

    def test_init(self):
        mock_terminal = mock.Mock()
        Comms(mock_terminal)
        # Transmits ctrl-c when initializing.
        mock_terminal.tx.assert_called_with(b'\x03')

    def test_reimport_module(self):
        mock_terminal = mock.Mock()
        comms = Comms(mock_terminal)
        comms.send = mock.Mock()
        comms.import_module('test')
        comms.import_module('test')
        self.assertEqual(comms.send.call_count, 1)

    def test_send_waits_for_data(self):
        mock_terminal = mock.Mock()
        mock_terminal.rx.side_effect = (None, None, b'>>> ')
        comms = Comms(mock_terminal)
        comms.send('test')
