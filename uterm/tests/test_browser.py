try:
    from unittest import mock
except ImportError:
    import mock
from uterm.browser import OSBrowser


def fake_isdir(name):
    """
    Return true if first character is 'A'
    """
    return name.startswith('A')


# OSBrowser

@mock.patch('os.path')
def test_osbrowser_is_container(os_path):
    os_path.isdir.side_effect = fake_isdir
    browser = OSBrowser()
    assert browser.is_container('Apple')
    assert not browser.is_container('Banana')


@mock.patch('os.listdir')
def test_osbrowser_list_container(os_listdir):
    files = ['a.py', 'b.py']
    os_listdir.return_value = files
    browser = OSBrowser()
    assert browser.list_container('') == files


@mock.patch('os.listdir')
def test_osbrowser_list_container_failed(os_listdir):
    os_listdir.side_effect = OSError
    browser = OSBrowser()
    assert browser.list_container('') is None
