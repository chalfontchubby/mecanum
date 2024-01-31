

import inspect
def DBG(msg):
    stack = inspect.stack()
    the_class = stack[1][0].f_locals["self"].__class__.__name__
    the_method = stack[1][0].f_code.co_name
    print(f"{the_class}:{the_method} {msg}")

class MenuItem:
    def __init__(self, name):
        self._name = name

    def click(self, menu_stack):
        DBG(f"{self._name}")
        pass

    def inc(self):
        DBG(f"{self._name}")

        new_idx = self.items.index(self._value) + 1
        if self._wrap:
            new_idx = new_idx % len(self.items)
        self._value = self.items[() % len(self.items)]

    def dec(self):
        DBG(f"{self._name}")

        self._value = self.items[
            (self.items.index(self._value) + len(self.items) - 1) % len(self.items)
        ]

    def current(self):
        return self._value
class Menu(MenuItem):

    def __init__(self, name, items=None, wrap=True):
        super().__init__(name)
        self._items = items
        if items:
            self._current = items[0]

    def name(self):
        return self._name

    def click(self, menu_stack):
        DBG("")

        menu_stack.push(self._current)

    def inc(self):
        DBG("")

        new_idx = self._items.index(self._current) + 1
        if new_idx >= len(self._items) :
            if self._wrap:
                new_idx = 0
            else:
                new_idx = len(self._items)-1

        self._current = self._items[new_idx]

    def dec(self):
        DBG("")

        new_idx = self._items.index(self._current) - 1
        if new_idx < 0:
            if self._wrap :
                new_idx = 0
            else:
                new_idx = len(self.items)-1
        self._current = self._items[new_idx]

    # Print full menu stack
    def dump(self, prefix=""):
        print(f"{prefix}{self}")
        if (self._items is not None):
            for item in self._items:
                if isinstance(item, Menu):
                    item.dump(prefix + "....")
    def __repr__(self):
        return f"{self._current.name()}"


class Option(Menu):
    _options = {}

    def __init__(self, name, items, default=None, wrap=True):
        super().__init__(name, items)
        self._wrap = wrap
        self._value = self._items[0] if default is None else default
        assert self._value is not None
        assert name not in Option._options
        Option._options[name] = self

    def click(self, menu_stack):

        assert self is menu_stack.active_item()
        DBG(f"Set value = {self._current}")

        self._value = self._current
        menu_stack.pop()

    def name(self):
        return self._name

    def __repr__(self):
        return f"{self._name} = {self._value}"

    @classmethod
    def get(cls, name):
        return cls._options[name]

    @classmethod
    def print_all(cls):
        for option in cls._options.values():
            print(f"\t{option}")

class MenuStack:
    def __init__(self, base_menu):
        self._stack = [base_menu]

    def active_item(self):
        return self._stack[-1]


    def click(self):
        DBG("")

        self.active_item().click(self)
    def inc(self):
        DBG("")

        self.active_item().inc()
    def dec(self):
        DBG("")

        self.active_item().dec()

    def push(self, menu):
        DBG("")

        self._stack.append(menu)

    def pop(self):
        DBG("")

        assert len(self._stack) > 1
        self._stack = self._stack[0:-1]

    def dump(self):
        print(f"Stack is {self._stack}")
        self._stack[0].dump()
    def __repr__(self):
        return "->".join([item._name for item in self._stack])+f"({self.active_item()})"


class Func(Menu):
    _options = {}

    def __init__(self, name, fn, auto_pop=True):
        super().__init__(name)
        self._auto_pop = auto_pop
        self._fn = fn

    def click(self, menu_stack):
        self._fn()
        if self._auto_pop:
            menu_stack.pop()

    def __repr__(self):
        return f"function {self._name}"

def func_211():
    print("func 211")


def func_212():
    print("func 212")


menu = Menu(
    "top",
    [
        Menu(
            "1",
            [
                Option("1_1", [0, 1, 2, 3, 4]),
                Option("1_2", [0, 1, 2, 3, 4, 5, 6], default=5),
                Option("Task", ["maze", "line", "lava"]),
            ],
        ),
        Menu("2", [Menu("2.1", [Func("foo", func_211), Func("bar", func_212)])]),
    ],
)
print(f"Menu is {menu}")
menu_stack = MenuStack(menu)
menu_stack.dump()

print(menu_stack)
menu_stack.click()
print(menu_stack)
menu_stack.click()
print(menu_stack)
print(f"Active {menu_stack}")
menu_stack.inc()
print(menu_stack)
menu_stack.click()
print(menu_stack)

# import sys, tty, termios
#
# def getch(char_width=1):
#     '''get a fixed number of typed characters from the terminal.
#     Linux / Mac only'''
#     fd = sys.stdin.fileno()
#     old_settings = termios.tcgetattr(fd)
#     try:
#         tty.setraw(fd)
#         ch = sys.stdin.read(char_width)
#     finally:
#         termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
#     return ch
#
# for i in range (10):
#     c = getch()
#     if c == "\r":
#         print("nl")
#     print(f"Key is {ord(c)}" )

for i in range(3):
    Option.print_all()
    Option.get("Task").inc()
    Option.get("1_2").dec()
