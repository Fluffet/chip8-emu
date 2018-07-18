import chip8
from random import random
import math
import sys
import curses

def log(s):
    with open("log", "a") as f:
        f.write(s + "\n")

class OpcodeHandler(object):
    def __init__(self, chip8):
        self.c8 = chip8

    def run_instruction(self, opcode):
        # I guess this is where most of the fun stuff happens
        # Everything was learned here
        # http://devernay.free.fr/hacks/chip8/C8TECH10.HTM

        nnn = opcode & 0x0FFF
        n   = opcode & 0x000F
        x   = (opcode & 0x0F00) >> 8
        y   = (opcode & 0x00F0) >> 4
        kk  = opcode & 0x00FF

        if opcode == 0x00EE: # 00EE: Return from subroutine
            self.c8.reg.pc = self.c8.reg.stack.pop()

        elif opcode == 0x00E0: # 00E0: Clear screen
            self.c8.mem.gfx = [0]*32*64
            self.c8.draw_flag = True

        elif opcode & 0xF000 == 0x1000: # 1NNN: Jump to NNN
            self.c8.reg.pc = nnn

        elif opcode & 0xF000 == 0x2000: # 0x2NNN: Calls subroutine at address NNN
            self.c8.reg.stack.append(self.c8.reg.pc)
            self.c8.reg.pc = nnn

        elif opcode & 0xF000 == 0x3000: # 3xkk Skip next instruction if Vx = kk
            if self.c8.reg.v[x] == kk:
                self.c8.reg.pc += 2

        elif opcode & 0xF000 == 0x4000: # 4xkk - SNE Vx, byte
            if self.c8.reg.v[x] != kk:
                self.c8.reg.pc += 2

        elif opcode & 0xF000 == 0x5000: # 5xy0 - SE Vx, Vy
            if self.c8.reg.v[x] == self.c8.reg.v[y]:
                self.c8.reg.pc += 2

        elif opcode & 0xF000 == 0x6000: # 6xkk - LD Vx, byte
            log("load v" + str(x) + " with " + str(kk))
            self.c8.reg.v[x] = kk

        elif opcode & 0xF000 == 0x7000: # 7xkk - ADD Vx, byte
            r = self.c8.reg.v[x] + kk
            self.c8.reg.v[0xF] = 1 if r > 255 else 0
            self.c8.reg.v[x] = r % 256

        elif opcode & 0xF00F == 0x8000: # 8xy0 - LD Vx, Vy
            self.c8.reg.v[x] = self.c8.reg.v[y]

        elif opcode & 0xF00F == 0x8001: # 8xy1 - OR Vx, Vy (bitwise)
            self.c8.reg.v[x] = self.c8.reg.v[x] | self.c8.reg.v[y]

        elif opcode & 0xF00F == 0x8002: # 8xy2 - AND Vx, Vy (bitwise)
            self.c8.reg.v[x] = self.c8.reg.v[x] & self.c8.reg.v[y]

        elif opcode & 0xF00F == 0x8003: # 8xy3 - XOR Vx, Vy (bitwise)
            self.c8.reg.v[x] = self.c8.reg.v[x] ^ self.c8.reg.v[y]

        elif opcode & 0xF00F == 0x8004: # 8xy4 - ADD Vx, Vy
            r = self.c8.reg.v[x] + self.c8.reg.v[y]
            self.c8.reg.v[0xF] = 1 if r > 255 else 0
            self.c8.reg.v[x] = r % 256

        elif opcode & 0xF00F == 0x8005: # 8xy5 - SUB Vx, Vy
            r = self.c8.reg.v[x] - self.c8.reg.v[y]
            if self.c8.reg.v[x] > self.c8.reg.v[y]:
                self.c8.reg.v[0xF] = 1
            else:
                self.c8.reg.v[0xF] = 0

        elif opcode & 0xF00F == 0x8006: # 8xy6 - SHR Vx {, Vy}
            r = self.c8.reg.v[x]
            self.c8.reg.v[0xF] = r % 2
            r = r >> 1
            self.c8.reg.v[x] = r

        elif opcode & 0xF00F == 0x8007: # SUBN Vx, Vy
            r = self.c8.reg.v[y] - self.c8.reg.v[x]
            if self.c8.reg.v[y] > self.c8.reg.v[x]:
                self.c8.reg.v[0xF] = 1
            else:
                self.c8.reg.v[0xF] = 0

        elif opcode & 0xF00F == 0x800E: # 8xyE - SHL Vx {, Vy}
            r = self.c8.reg.v[x]
            bit_seven = r >> 8
            self.c8.reg.v[0xF] = bit_seven
            r = r << 1
            self.c8.reg.v[x] = r

        elif opcode & 0xF00F == 0x9000: # 9xy0 - SNE Vx, Vy
            if self.c8.reg.v[x] != self.c8.reg.v[y]:
                pc += 2

        elif opcode & 0xF000 == 0xA000: # Annn - LD I, addr
            self.c8.reg.i = nnn

        elif opcode & 0xF000 == 0xB000: # JP V0, addr
            self.c8.reg.pc = nnn + self.c8.reg.v[0x0]

        elif opcode & 0xF000 == 0xC000: # RND Vx, byte
            self.c8.reg.v[x] = kk & int(random()*256)

        elif opcode & 0xF000 == 0xD000: # Dxyn - DRW Vx, Vy, nibble

            reg_x_coordinate = self.c8.reg.v[x]
            reg_y_coordinate = self.c8.reg.v[y]

            log("REG_X: " + str(x) + " " + str(reg_x_coordinate))
            log("REG_Y: " + str(y) + " " + str(reg_y_coordinate))
            self.c8.reg.v[0xF] = 0

            for y_offset in range(n): # y_offset is row of sprite

                # get byte representation
                sprite_int = self.c8.mem.mem[y_offset + self.c8.reg.i]

                actual_y_coordinate = reg_y_coordinate + y_offset
                actual_y_coordinate = actual_y_coordinate % 32

                for x_offset, bit in enumerate(format(sprite_int, '08b')):
                    # loop over each bit in the byte

                    actual_x_coordinate = reg_x_coordinate + x_offset
                    actual_x_coordinate = actual_x_coordinate % 32
                    log("y:" + str(actual_y_coordinate))
                    log("x:" + str(actual_x_coordinate))
                    gfx_mem_index = actual_y_coordinate * 64 + actual_x_coordinate
                    log(str(gfx_mem_index))
                    pixel = self.c8.mem.gfx[gfx_mem_index]

                    # XOR written like this for clarity
                    if int(bit) == 1 and pixel == 1:
                        self.c8.reg.v[0xF] = 1
                        self.c8.mem.gfx[gfx_mem_index] = 0

                    if int(bit) == 1 and pixel == 0:
                        self.c8.mem.gfx[gfx_mem_index] = 1

                    if int(bit) == 0 and pixel == 1:
                        self.c8.mem.gfx[gfx_mem_index] = 1

                    if int(bit) == 0 and pixel == 0:
                        self.c8.mem.gfx[gfx_mem_index] = 0

            self.c8.draw_flag = True


        elif opcode & 0xF0FF == 0xE09E: # SKP Vx
            # Skips the next instruction if the key stored in VX is pressed
            key = self.c8.mem.v[x]
            if self.c8.mem.keypad[key] == 1:
                pc += 2

        elif opcode & 0xF0FF == 0xE0A1: # SKNP Vx
            # Skips the next instruction if the key stored in VX is NOT pressed
            key = self.c8.mem.v[x]
            if self.c8.mem.keypad[key] == 0:
                pc += 2

        elif opcode & 0xF0FF == 0xF007: # LD Vx, DT
            self.c8.reg.v[x] = self.c8.tim.delay

        elif opcode & 0xF0FF == 0xF00A: # Fx0A - LD Vx, K
            # Ghetto solution
            self.c8.screen.nodelay(False)
            key = chr(self.c8.screen.getch())
            if key != -1:
                if key in self.c8.keypad:
                    self.c8.reg.v[x] = self.c8.keypad[key]
            self.c8.screen.nodelay(True)

        elif opcode & 0xF0FF == 0xF015: # Fx15 - LD DT, Vx
            self.c8.tim.delay = self.c8.reg.v[x]

        elif opcode & 0xF0FF == 0xF018: # Fx18 - LD ST, Vx
            self.c8.tim.sound == self.c8.reg.v[x]

        elif opcode & 0xF0FF == 0xF01E: # Fx1E - ADD I, Vx
            r = self.c8.reg.i + self.c8.reg.v[x]
            self.c8.reg.i = r

        elif opcode & 0xF0FF == 0xF029: # Fx29 - LD F, Vx
            self.c8.reg.i = self.c8.reg.v[x] * 5

        elif opcode & 0xF0FF == 0xF033: # Fx33 - LD B, Vx
            r = self.c8.reg.v[x]
            hundreds = math.floor(r / 100)
            r -= hundreds * 100
            tens = math.floor(r / 10)
            r -= tens * 10
            units = r
            self.c8.mem.mem[self.c8.reg.i  ] = hundreds
            self.c8.mem.mem[self.c8.reg.i+1] = tens
            self.c8.mem.mem[self.c8.reg.i+2] = units

        elif opcode & 0xF0FF == 0xF055: # Fx55 - LD [I], Vx
            for offset in range(x):
                self.c8.mem.mem[self.c8.reg.i + offset] = self.c8.reg.v[offset]

        elif opcode & 0xF0FF == 0xF065: # LD Vx, [I]
            for offset in range(x):
                 self.c8.reg.v[offset] = self.c8.mem.mem[self.c8.reg.i + offset]

        else:
            print("Unknown opcode: " + hex(opcode))
            log("Unknown opcode: " + hex(opcode))
            curses.nocbreak()
            self.c8.screen.keypad(False)
            curses.echo()
            curses.endwin()
            sys.exit()

        with open("log", "a") as f:
            f.write( hex(opcode) + " " + str(self.c8.ticks) )
            f.write( str(self.c8.reg) )
            f.write("\n")
        #print(self.c8.reg)
