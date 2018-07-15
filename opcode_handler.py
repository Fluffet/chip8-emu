import chip8

class OpcodeHandler(object):
    def __init__(self, chip8):
        self.c8 = chip8
        self.co = 0     # Current op, just to avoid parameter spam

    def run_instruction(self, opcode):
        # I guess this is where most of the fun stuff happens
        # Everything was learned here
        # http://devernay.free.fr/hacks/chip8/C8TECH10.HTM


        # OPCODEs starting with 0

        if opcode == 0x00EE:   # 00EE: Return from subroutine
                self.c8.mem.gfx = [0]*32*64
                self.c8.draw_flag = True
                return

        elif opcode == 0x00E0: # 00E0: Clear screen
                self.c8.pc = self.c8.reg.stack.pop()
                return

        nnn = opcode & 0x0FFF >> 4
        n   = opcode & 0x000F >> 4
        x   = opcode & 0x0F00 >> 8
        y   = opcode & 0x00F0 >> 4
        kk  = opcode & 0x00FF


        if opcode & 0xF000 == 0x1000: # 1NNN: Jump to NNN
            self.c8.pc = nnn

        elif opcode & 0xF000 == 0x2000:
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
            if result > 255:
                self.c8.reg.v[0xF] = 1
            else:
                self.c8.reg.v[0xF] = 0
            self.c8.reg.v[x] = r

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
            if result > 255:
                self.c8.reg.v[0xF] = 1
                r %= 256
            else:
                self.c8.reg.v[0xF] = 0
            self.c8.reg.v[x] = r

        elif opcode & 0xF00F == 0x8005: # 8xy5 - SUB Vx, Vy
            r = self.c8.reg.v[x] - self.c8.reg.v[y]
            if self.c8.reg.v[x] > self.c8.reg.v[y]:
                self.c8.reg.v[0xF] = 1
            else:
                self.c8.reg.v[0xF] = 0

        elif opcode & 0xF00F == 0x8006: # 8xy6 - SHR Vx {, Vy}
            r = self.c8.reg.v[x] >> 1
            self.c8.reg.v[0xF] = r % 2
            r = r/2
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

        print("UNKNOWN OPCODE: " + hex(opcode))


"""
        if instr == 0x0000:
            if instr == 0x0E0: # 00E0: Clear screen


        if instr == 0x00EE: # 00EE:  from subroutine
                self.reg.pc = self.reg.stack.pop()

        self.mem.gfx = [0]*32*64
        self.draw_flag = True
        pass


        if decoded == 0x00E0: # 00E0: Clear screen
            self.mem.gfx = [0]*32*64

    if decoded == 0x00EE: # 00EE:  from subroutine
            self.reg.pc = self.reg.stack.pop()

        if decoded ==

        if decoded == 0x3000: # 3XNN: if (V[X] == NN) skip next instr
            v_reg = opcode & 0x0F00
            nn = opcode & 0x00FF
            if self.reg.v[v_reg] == nn:
                self.reg.pc += 2

        if decoded == 0xA000: # ANNN: Sets I to address NNN
            self.reg.i = opcode & 0x0FFF

        if decoded == 0xB000: # BNNN: PC = V0 + NNN
            self.reg.pc = self.reg.v[0x0] + opcode & 0x0FFF


"""
