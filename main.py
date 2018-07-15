import curses
import sys
from chip8 import Chip8

#screen = curses.initscr()
#curses.noecho()
#curses.cbreak()
#curses.curs_set(False)
#screen.keypad(True)

emu = Chip8()
emu.load_game(sys.argv[1])

def draw():
    screen.clear()
    s = ""

    for y in range(32):
        row = emu.gfx_mem[y*32 : y*32+64]
        for x in row:
            if x == 1:
                s += "#"
            else:
                s += " "
        s += "\n"

    screen.addstr(0,0,s)
    screen.refresh()

def update_keys():
    pass

try:
    while True:

        emu.tick()
        if emu.draw_flag:
            #draw()
            emu.draw_flag = False
            pass

        update_keys()

except KeyboardInterrupt:
    #curses.nocbreak()
    #screen.keypad(False)
    #curses.echo()
    #curses.endwin()
    sys.exit()
    pass
