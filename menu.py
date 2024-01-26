
class Option:
    _options = {}
    def __init__(self, name, choices, default=None):
        self._name = name
        self._choices = choices
        self._value = self._choices[0] if default is None else default
        assert self._value is not None
        assert name not in Option._options
        Option._options[name] = self

    def inc(self):
        self._value = self._choices[(self._choices.index(self._value) + 1) % len(self._choices)]

    def dec(self):
        self._value = self._choices[(self._choices.index(self._value) + len(self._choices) - 1) % len(self._choices)]


    def __repr__(self):
        return f"{self._name} = {self._value}"
    @classmethod
    def get(cls, name):
        return cls._options[name]

    @classmethod
    def print_all(cls):
        for option in cls._options.values():
            print(f"\t{option}")

def func_211():
    print("func 211")

def func_212():
    print("func 212")



class Menu:

    _menu_stack = []
    def __init__(self, name, items):
        self._name = name
        self._items = items;
        self._current = items[0]
        Menu._menu_stack = [self]



menu = Menu("top", [
    "1" , [
        Option("1_1",[0,1,2,3,4]),
        Option("1_2", [0, 1, 2, 3, 4,5,6], default = 5),
        Option("Task", ["maze", "line", "lava"]),
    ],
    Menu ("2" ,
          [
              Menu("2.1",
                   [
                   func_211,
            func_212
        ])
    ])
    ])

for i in range (3):
    Option.print_all()
    Option.get("Task").inc()
    Option.get("1_2").dec()