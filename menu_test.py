
from menu import Menu, MenuStack, Option, Func
def func_211():
    print("func 211")

def func_212():
    print("func 212")



# Create the menu stack that will hold everything together
ms = MenuStack()
# And populate it with a set of menus
menu = Menu(ms,
    "top",
    [
        Menu(ms,
            "1",
            [
                Option(ms,"1_1", [0, 1, 2, 3, 4]),
                Option(ms,"1_2", [0, 1, 2, 3, 4, 5, 6], default=5),
                Option(ms,"Task", ["maze", "line", "lava"]),
            ],
        ),
        Menu(ms,"2",
             [Menu(ms,"2.1",
                   [
                       Func(ms,"foo", func_211),
                       Func(ms,"bar", func_212)]
                   )]
             ),
    ],
)


# Smoke tests
print(f"Menu is {menu}")

ms.set_base(menu)
ms.dump()
assert(ms.active_item().name() == "top")
assert(ms.active_item().current().name() == "1")

ms.click()
assert(ms.active_item().name() == "1")
assert(ms.active_item().current().name() == "1_1")
tmp0 = ms.active_item()

ms.click()
tmp = ms.active_item()
assert(ms.active_item().name() == "1_1")
assert(ms.active_item().current() == 0)

ms.inc()
assert(ms.active_item().current() == 1)
# Clink on "1" should set it as the value of the "1_1" option
ms.click()
assert(ms.active_item().name() == "1")



tmp = ms.active_item().current()
assert(ms.active_item().current().name() == "1_1")

print(ms)
ms.click()
print(ms)

