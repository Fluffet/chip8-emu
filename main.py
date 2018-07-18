import curses
import sys
from chip8 import Chip8
from time import sleep

screen = curses.initscr()
curses.noecho()
curses.cbreak()
curses.curs_set(False)
screen.keypad(True)
screen.nodelay(True)

keypad = {
    "1" : 0x1, "2" : 0x2, "3" : 0x3, "4" : 0xC,
    "q" : 0x4, "w" : 0x5, "e" : 0x6, "r" : 0xD,
    "a" : 0x7, "s" : 0x8, "d" : 0x9, "f" : 0xE,
    "z" : 0xA, "x" : 0x0, "c" : 0xB, "v" : 0xF }

emu = Chip8(screen, keypad) # Have to pass screen and keypad for 0xFx0A in an easy way =)
emu.load_game(sys.argv[1])


def draw():
    screen.clear()
    s = ""

    for y in range(32):
        row = emu.mem.gfx[y*64 : y*64 + 64]

        for x in row:
            if x == 1:
                s += "█"#"#"
            else:
                s += " "
        s += "\n"

    try:
        pass
    except ERR as e:
        raise
    else:
        pass
    finally:
        pass
    screen.addstr(0,0,s)
    screen.refresh()
    emu.draw_flag = False

def update_keys():
    c = screen.getch()

    if c != -1:
        c = chr(c)
        for k,v in keypad.items(): # reset all to 0
            keypad[k] = 0
            if k == c:
                emu.keypad[c] = 1

try:
    while True:
        emu.tick()
        if emu.draw_flag:
            draw()

        update_keys()
        sleep(0.16)

except KeyboardInterrupt:
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()
    sys.exit()
    pass
