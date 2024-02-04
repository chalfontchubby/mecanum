

import inspect
def DBG(msg):
    stack = inspect.stack()
    the_class = stack[1][0].f_locals["self"].__class__.__name__
    the_method = stack[1][0].f_code.co_name
    print(f"{the_class}:{the_method} {msg}")

class MenuItem:
    def __init__(self, ms, name):
        self._stack = ms
        self._name = name

    def click(self):
        DBG(f"{self._name}")

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

    def activate(self):
        pass

    def deactivate(self):
        pass

    def name(self):
        return self._name

    def current(self):
        return self._current

class Menu(MenuItem):
    def __init__(self, ms, name, items=None, wrap=True):
        super().__init__(ms, name)
        self._items = items
        self._current = None

    def name(self):
        return self._name

    def click(self):
        DBG("")
        self._stack.push(self._current)

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

    def activate(self):
        self._current=self._items[0]

    def deactivate(self):
        self._current = None

    # Print full menu stack
    def dump(self, prefix=""):
        print(f"{prefix}{self}")
        if (self._items is not None):
            for item in self._items:
                if isinstance(item, Menu):
                    item.dump(prefix + "....")
    def __repr__(self):
        return self.name() + (f" = {self._current.name()}" if self._current is not None else " <inactive>")


class Option(Menu):

    def __init__(self, ms, name, items, default=None, wrap=True):
        super().__init__(ms, name, items)
        self._wrap = wrap
        self._value = self._items[0] if default is None else default
        assert self._value is not None
        assert name not in self._stack._options
        self._stack._options[name] = self

    def click(self):
        assert self is self._stack.active_item()
        DBG(f"Set value = {self._current}")

        self._value = self._current
        self._stack.pop()

    def name(self):
        return self._name

    def __repr__(self):
        return f"{self._name} = {self._value}"


class MenuStack:
    def __init__(self) :
        self._stack = []
        self._options = {}

    def set_base(self, base_menu):
        self._stack = [base_menu]
        base_menu.activate()

    def active_item(self):
        return self._stack[-1]

    def click(self):
        DBG("")
        self.active_item().click()

    def inc(self):
        DBG("")
        self.active_item().inc()

    def dec(self):
        DBG("")
        self.active_item().dec()

    def push(self, menu):
        DBG("")
        menu.activate()
        self._stack.append(menu)

    def pop(self):
        DBG("")
        assert len(self._stack) > 1
        self.active_item().deactivate()
        self._stack = self._stack[0:-1]

    @classmethod
    def get_opt(cls, name):
        return cls._options[name]

    def dump(self):
        print(f"Stack is {self._stack}")
        self._stack[0].dump()
        for option in self._options.items():
            print(f"option {option.__repr__()}")

    def __repr__(self):
        return "->".join([item._name for item in self._stack])+f"({self.active_item()})"


class Func(Menu):
    _options = {}

    def __init__(self, ms, name, fn, auto_pop=True):
        super().__init__(ms, name)
        self._auto_pop = auto_pop
        self._fn = fn

    def click(self, ms):
        self._fn()
        if self._auto_pop:
            ms.pop()

    def __repr__(self):
        return f"function {self._name}"



