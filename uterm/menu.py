import curses


class Menu(object):

    def __init__(self, title, items=None):
        self.width = 60
        self.selected_item = 0
        self.window = curses.newwin(4, self.width)
        self.title = title
        self.items = items
        self.panel = curses.panel.new_panel(self.window)
        self.panel.hide()
        self.window.keypad(1)
        self.window.nodelay(0)

    def __call__(self, terminal):
        self.terminal = terminal
        curses.curs_set(0)  # Hide cursor.
        self.panel.top()
        self.draw_items()

        try:
            exit = None
            while not exit:
                ch = self.window.getch()
                if ch == 27:
                    break
                exit = self.nav(ch)
        finally:
            self.panel.hide()
            curses.curs_set(1)  # Show cursor again.
        return exit

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items):
        self._items = items or []
        self.window.resize(4 + len(self._items), self.width)
        self.window.erase()
        self.window.addstr(1, 2, self.title)
        self.window.border()

    def draw_items(self):
        for i, item in enumerate(self.items):
            selected = self.selected_item == i
            self.window.addstr(
                3 + i, 3, item[0], curses.A_BOLD if selected else 0)
        self.window.refresh()

    def nav(self, key):
        if key == curses.KEY_DOWN:
            self.selected_item += 1
        elif key == curses.KEY_UP:
            self.selected_item -= 1
        elif key == 10:
            return self.execute()
        else:
            return
        self.selected_item %= len(self.items)
        self.draw_items()

    def execute(self):
        func = self.items[self.selected_item][1]
        if callable(func):
            return func(self.terminal)
