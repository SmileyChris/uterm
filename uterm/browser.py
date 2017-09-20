from __future__ import unicode_literals
import os
import curses
from fnmatch import fnmatch

ESC = 27


def pad(data, width):
    return data + ' ' * (width - len(data))


class File(object):
    """
    A file / directory node in the filesystem.

    Attributes:
        container (bool): whether the filesystem node can contain other things.
        name (str): The path of the file / directory
        factory (BrowserBase): The instance which created this object
    """
    container = False

    def __init__(self, name, factory, nice_name=None):
        self.name = name
        self.factory = factory
        self._nice_name = nice_name

    def render(self, depth, width):
        return pad('%s%s %s' % (' ' * 2 * depth, self.icon(),
                                self.nice_name), width)

    @property
    def nice_name(self):
        """
        The basename of the file / directory node.
        """

        if self._nice_name is not None:
            return self._nice_name
        return os.path.basename(self.name)

    def children(self):
        return []

    def icon(self):
        return '   '

    def traverse(self):
        yield self, 0


class Dir(File):
    """
    A directory node in the filesystem.

    Attributes:
        kids (:obj:`list` of :obj:`File`): child filesystem items
        expanded (bool): Whether the item is expanded in the UI
    """

    container = True

    def __init__(self, *args, **kwargs):
        super(Dir, self).__init__(*args, **kwargs)
        self.kids = None
        self._expanded = False

    @property
    def kidnames(self):
        if not hasattr(self, '_kidnames'):
            self._kidnames = self.factory.child_names(self.name)
        return self._kidnames

    def children(self):
        """
        Populate and return the kids attribute.
        """

        if self.kidnames is None:
            return []
        if self.kids is None:
            self.kids = self.factory.children(self.name, self.kidnames)
        return self.kids

    def icon(self):
        if self.expanded:
            return '[-]'
        elif self.kidnames is None:
            return '[?]'
        elif self.children():
            return '[+]'
        else:
            return '[ ]'

    @property
    def expanded(self):
        return self._expanded

    @expanded.setter
    def expanded(self, value):
        self._expanded = value and self.children()

    def collapse(self):
        self.expanded = False

    def traverse(self):
        """
        Traverses expanded child filesystem nodes

        Yields:
            Tuple (File, Int): child File object and and depth
        """
        yield self, 0
        if not self.expanded:
            return
        for child in self.children():
            for kid, depth in child.traverse():
                yield kid, depth + 1


class BrowserBase(object):
    """
    Abstracts a file browser UI.

    Attributes:
        dir_class (type): Type of directories
        file_class (type): Type of files
        initial_index (int):
    """
    dir_class = Dir
    file_class = File
    initial_index = 0
    return_container = True
    base_name = '.'

    def __init__(self, name=None, root_name=None):
        self.root_name = root_name
        self.reset(name)

    def reset(self, name=None):
        if name is None:
            name = self.base.name if hasattr(self, 'base') else self.base_name
        self.base = self.item(name, nice_name=self.root_name)
        self.base.expanded = True

    def item(self, name, *args, **kwargs):
        """
        Instantiate a File / Dir object from its name.

        Arguments:
            name (str):
        """
        if self.is_container(name):
            obj_class = self.dir_class
        else:
            obj_class = self.file_class
        return obj_class(name, factory=self, *args, **kwargs)

    def run(self, stdscr):
        """
        Draws the browser UI on the screen
        """
        curidx = self.initial_index
        while True:
            stdscr.clear()
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
            offset = max(0, curidx - curses.LINES + 3)
            current_obj = self.base
            for line, (data, depth) in enumerate(self.base.traverse()):
                if line == curidx:
                    stdscr.attrset(curses.color_pair(1) | curses.A_BOLD)
                    current_obj = data
                else:
                    stdscr.attrset(curses.color_pair(0))
                if 0 <= line - offset < curses.LINES - 1:
                    stdscr.addstr(
                        line - offset, 0, data.render(depth, curses.COLS))
            stdscr.refresh()
            ch = stdscr.getch()
            if ch == curses.KEY_UP:
                curidx -= 1
            elif ch == curses.KEY_DOWN:
                curidx += 1
            elif ch == curses.KEY_PPAGE:
                curidx -= max(0, curses.LINES)
            elif ch == curses.KEY_NPAGE:
                curidx += min(line - 1, curses.LINES)
            elif ch == curses.KEY_RIGHT:
                current_obj.expanded = True
            elif ch == curses.KEY_LEFT:
                current_obj.expanded = False
            elif ch == ESC:
                return ('CANCEL', current_obj)
            elif ch == curses.KEY_DC:  # Del
                return ('DELETE', current_obj)
            elif ch == ord('\n'):
                if self.return_container or not current_obj.container:
                    return ('SELECT', current_obj)
                current_obj.expanded = not current_obj.expanded
            curidx %= line + 1

    def child_names(self, name):
        paths = self.list_container(name)
        if paths is None:
            return
        paths = sorted(paths)
        files, folders = [], []
        for path in paths:
            path = os.path.join(name, path)
            if self.is_container(path):
                folders.append(path)
            elif self.file_match(path):
                files.append(path)
        return folders + files

    def file_match(self, name):
        return True

    def children(self, name, child_names):
        return [self.item(child) for child in child_names]


class OSBrowser(BrowserBase):

    def is_container(self, name):
        return os.path.isdir(name)

    def list_container(self, name):
        try:
            return os.listdir(name)
        except Exception:
            return  # probably permission denied

    @property
    def initial_index(self):
        index = 0
        latest = 0
        for i, child in enumerate(self.base.children()):
            mtime = os.path.getmtime(child.name)
            if mtime > latest:
                latest = mtime
                index = i + 1
        return index


class PyBrowser(OSBrowser):

    return_container = False

    def file_match(self, name):
        return fnmatch(name, '*.py') or fnmatch(name, '*.mpy')


class uPyBrowser(BrowserBase):

    base_name = '/'

    def __init__(self, comms, *args, **kwargs):
        self.comms = comms
        super(uPyBrowser, self).__init__(*args, **kwargs)

    def reset(self, *args, **kwargs):
        self.listdir_cache = {}
        super(uPyBrowser, self).reset(*args, **kwargs)

    def list_container(self, path):
        self.comms.import_module('os')
        return self.listdir_cache.setdefault(
            path, self.comms.json('os.listdir(%s)' % repr(path)))

    def is_container(self, name):
        if name.endswith('.py'):
            return False
        return isinstance(self.list_container(name), list)
