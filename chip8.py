from dataclasses import dataclass, field
from opcode_handler import OpcodeHandler

@dataclass
class Registers(object):
    v     : list = field(default_factory=list)
    stack : list = field(default_factory=list) #lazy but who cares
    pc    : int  = 0x200
    i     : int  = 0

    def __post_init__(self):
        self.v = [0]*16

@dataclass
class Timers(object):
    sound : int = 0
    delay : int = 0

@dataclass
class Memory(object):
    mem    : list = field(default_factory=list)
    gfx    : list = field(default_factory=list)
    keypad : list = field(default_factory=list)

    def __post_init__(self):
        self.mem    = [0]*4096
        self.gfx    = [0]*32*64 #[[0]*64 for x in range(32)]
        self.keypad = [0]*16
        # Load fontset
        self.mem[0:79] = [0xF0, 0x90, 0x90, 0x90, 0xF0,
                          0x20, 0x60, 0x20, 0x20, 0x70,
                          0xF0, 0x10, 0xF0, 0x80, 0xF0,
                          0xF0, 0x10, 0xF0, 0x10, 0xF0,
                          0x90, 0x90, 0xF0, 0x10, 0x10,
                          0xF0, 0x80, 0xF0, 0x10, 0xF0,
                          0xF0, 0x80, 0xF0, 0x90, 0xF0,
                          0xF0, 0x10, 0x20, 0x40, 0x40,
                          0xF0, 0x90, 0xF0, 0x90, 0xF0,
                          0xF0, 0x90, 0xF0, 0x10, 0xF0,
                          0xF0, 0x90, 0xF0, 0x90, 0x90,
                          0xE0, 0x90, 0xE0, 0x90, 0xE0,
                          0xF0, 0x80, 0x80, 0x80, 0xF0,
                          0xE0, 0x90, 0x90, 0x90, 0xE0,
                          0xF0, 0x80, 0xF0, 0x80, 0xF0,
                          0xF0, 0x80, 0xF0, 0x80, 0x80]

class Chip8(object):

    def __init__(self, screen, keypad):
        self.reg = Registers()
        self.mem = Memory()
        self.tim = Timers()
        self.opcode_handler = OpcodeHandler(self)
        self.draw_flag = True
        self.ticks = 0
        self.screen = screen
        self.keypad = keypad


    def load_game(self, game):
        data = open("roms/" + game + ".rom", "rb").read()

        for i, v in enumerate(data):
            self.mem.mem[0x200 + i] = v

    def tick(self):
        # Fetch opcode
        opcode = self.mem.mem[self.reg.pc] << 8 | self.mem.mem[self.reg.pc+1]

        # Execute opcode
        self.opcode_handler.run_instruction(opcode)

        # Update pc and timers
        self.reg.pc += 2

        if self.tim.delay != 0:
            self.tim.delay -= 1

        if self.tim.sound != 0:
            if self.tim.sound == 1:
                print('\a')

        self.ticks += 1
