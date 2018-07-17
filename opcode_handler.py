import chip8
from random import random
import math

def log(s):
    with open("log", "a") as f:
        f.write(s + "\n")

class OpcodeHandler(object):
    def __init__(self, chip8):
        self.c8 = chip8
        self.co = 0     # Current op, just to avoid parameter spam

    def run_instruction(self, opcode):
        # I guess this is where most of the fun stuff happens
        # Everything was learned here
        # http://devernay.free.fr/hacks/chip8/C8TECH10.HTM

        nnn = opcode & 0x0FFF
        n   = opcode & 0x000F
        x   = opcode & 0x0F00 >> 8
        y   = opcode & 0x00F0 >> 4
        kk  = opcode & 0x00FF

        #print(hex(opcode), self.c8.ticks)

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
            self.c8.reg.v[x] = kk

        elif opcode & 0xF000 == 0x7000: # 7xkk - ADD Vx, byte
            r = self.c8.reg.v[x] + kk
            self.c8.reg.v[0xF] = 1 if r > 255 else 0
            self.c8.reg.v[x] = r % 255

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
            self.c8.reg.v[x] = r % 255

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
            self.c8.reg.v[0xF] = r%2
            r = r*2
            self.c8.reg.v[x] = r

        elif opcode & 0xF00F == 0x9000: # 9xy0 - SNE Vx, Vy
            if self.c8.reg.v[x] != self.c8.reg.v[y]:
                pc += 2

        elif opcode & 0xF000 == 0xA000: # Annn - LD I, addr
            self.c8.reg.i = nnn

        elif opcode & 0xF000 == 0xB000: # JP V0, addr
            self.c8.reg.pc = nnn + self.c8.reg.v[0x0]

        elif opcode & 0xF000 == 0xC000: # RND Vx, byte
            self.c8.reg.v[x] = int(random()*256) & kk

        elif opcode & 0xF000 == 0xD000: # Dxyn - DRW Vx, Vy, nibble
            x_pos = self.c8.reg.v[x]
            y_pos = self.c8.reg.v[y]
            self.c8.reg.v[0xF] = 0

            for y_index in range(n):

                sprite_int = self.c8.mem.mem[y_index + self.c8.reg.i]

                for offset, bit in enumerate(bin(sprite_int)[2:]):
                    if int(bit) == 1:

                        gfx_mem_index = y_pos * 64 + x_pos + offset

                        if self.c8.mem.gfx[gfx_mem_index] == 1:
                            self.c8.reg.v[0xF] = 1
                            self.c8.mem.gfx[gfx_mem_index] = 0
                        else:
                            self.c8.mem.gfx[gfx_mem_index] = 1

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
            # Wait for a key press, store the value of the key in Vx.
            # All execution stops until a key is pressed
            # then the value of that key is stored in Vx
            # key = screen.getch()
            #emu.wait_for_key = True
            self.c8.screen.nodelay(False)
            key = self.c8.screen.getch()

            if key in self.c8.keypad:
                self.c8.reg.v[x] = self.keypad[key]

            self.c8.screen.nodelay(True)

        elif opcode & 0xF0FF == 0xF015: # Fx15 - LD DT, Vx
            self.c8.tim.delay = self.c8.reg.v[x]

        elif opcode & 0xF0FF == 0xF018: # Fx18 - LD ST, Vx
            self.c8.tim.sound == self.c8.reg.v[x]

        elif opcode & 0xF0FF == 0xF01E: # Fx1E - ADD I, Vx
            r = self.c8.reg.i + self.c8.reg.v[x]
            self.c8.reg.v[0xF] = 1 if r > 255 else 0
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
            self.c8.mem.mem[self.c8.reg.i]   = hundreds
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

        with open("log", "a") as f:
            f.write( hex(opcode) + " " + str(self.c8.ticks) )
            f.write( str(self.c8.reg) )
            f.write("\n")
        #print(self.c8.reg)
