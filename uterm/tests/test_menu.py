try:
    from unittest import mock
except ImportError:
    import mock
import pytest
from uterm.menu import Menu


@mock.patch('uterm.menu.curses')
def test_menu_init(curses):
    Menu('Test')


@pytest.mark.timeout(0.1)
@mock.patch('uterm.menu.curses')
def test_menu_call(curses):
    menu = Menu('Test')
    menu.window.getch.return_value = 27

    menu(terminal=None)
