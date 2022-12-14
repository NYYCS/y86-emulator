import itertools
import ctypes
import math


class BadAddress(Exception):
    pass


class BadInstruction(Exception):
    pass


class Memory:

    def __init__(self) -> None:
        self._storage = {}

    def get_byte(self, addr):
        if addr < 0:
            raise BadAddress
        return self._storage.get(addr, 0)

    def get_quad(self, addr):
        if addr < 0:
            raise BadAddress
        word = 0
        for pos in reversed(range(addr, addr + 8)):
            word <<= 8
            word |= self.get_byte(pos)
        return ctypes.c_long(word).value

    def set_byte(self, addr, byte):
        if addr < 0:
            raise BadAddress
        self._storage[addr] = byte & 255

    def set_quad(self, addr, word):
        if addr < 0:
            raise BadAddress
        for pos in range(addr, addr + 8):
            self.set_byte(pos, word)
            word >>= 8

    def to_json(self):
        data = {}
        for addr, _ in itertools.groupby(self._storage.keys(), lambda x: math.floor(x / 8) * 8):
            word = self.get_quad(addr)
            if word:
                data[addr] = word
        return data

    @classmethod
    def from_json(cls, data):
        mem = cls()
        for addr, word in data.items():
            mem.set_quad(int(addr), word)
        return mem

    def load_yo_buffer(self, buffer):
        for text in buffer.strip().split('\n'):
            addr_bincode, _ = text.split('|')
            addr_bincode = addr_bincode.split(':')
            if len(addr_bincode) == 2:
                addr, bincode = addr_bincode

                addr = int(addr, 16)
                bincode = bincode.strip()

                for byte_offset, byte_start_pos in enumerate(range(0, len(bincode), 2)):
                    byte = int(bincode[byte_start_pos: byte_start_pos + 2], 16)
                    self.set_byte(addr + byte_offset, byte)


class Registers:
    RAX = 0x0
    RCX = 0x1
    RDX = 0x2
    RBX = 0x3
    RSP = 0x4
    RBP = 0x5
    RSI = 0x6
    RDI = 0x7
    R8  = 0x8
    R9  = 0x9
    R10 = 0xa
    R11 = 0xb
    R12 = 0xc
    R13 = 0xd
    R14 = 0xe

    def __init__(self) -> None:
        self._reg = [
            0,  # RAX
            0,  # RCX
            0,  # RDX
            0,  # RBX
            0,  # RSP
            0,  # RBP
            0,  # RSI
            0,  # RDI
            0,  # R8
            0,  # R9
            0,  # R10
            0,  # R11
            0,  # R12
            0,  # R13
            0,  # R14
        ]

    def __getitem__(self, index):
        return ctypes.c_long(self._reg[index]).value

    def __setitem__(self, index, value):
        self._reg[index] = ctypes.c_long(value).value

    def to_json(self):
        data = {}
        for i, reg in enumerate(['rax', 'rcx', 'rdx', 'rbx', 'rsp', 'rbp', 'rsi', 'rdi', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14']):
            data[reg] = self[i]
        return data

    @classmethod
    def from_json(cls, data):
        reg = cls()
        reg._reg = [
            data.pop(r)    
            for r in ['rax', 'rcx', 'rdx', 'rbx', 'rsp', 'rbp', 'rsi', 'rdi', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14']
        ]
        return reg


class OPCode:
    HALT   = 0x00
    NOP    = 0x10
    RRMOVQ = 0x20
    CMOVLE = 0x21
    CMOVL  = 0x22
    CMOVE  = 0x23
    CMOVNE = 0x24
    CMOVGE = 0x25
    CMOVG  = 0x26
    IRMOVQ = 0x30
    RMMOVQ = 0x40
    MRMOVQ = 0x50
    ADDQ   = 0x60
    SUBQ   = 0x61
    ANDQ   = 0x62
    XORQ   = 0x63
    JMP    = 0x70
    JLE    = 0x71
    JL     = 0x72
    JE     = 0x73
    JNE    = 0x74
    JGE    = 0x75
    JG     = 0x76
    CALL   = 0x80
    RET    = 0x90
    PUSHQ  = 0xa0
    POPQ   = 0xb0
    IADDQ  = 0xc0
    ISUBQ  = 0xc1
    IANDQ  = 0xc2
    IXORQ  = 0xc3


class CONDCode:
    NC = 0x0
    LE   = 0x1
    L    = 0x2
    E    = 0x3
    NE   = 0x4
    GE   = 0x5
    G    = 0x6


class OPQCode:
    ADD = 0x0
    SUB = 0x1
    AND = 0x2
    XOR = 0x3


class STATCode:
    AOK = 0x1
    HLT = 0x2
    ADR = 0x3
    INS = 0x4


def bisect_byte(byte):
    a = (byte >> 4) & 15
    b = byte & 15
    return a, b


class CPU:
    def __init__(self):
        self.PC = 0
        self.STAT = STATCode.AOK
        self.CC = {
            'ZF': 1,
            'SF': 0,
            'OF': 0,
        }
        self.REG = Registers()
        self.MEM = Memory()

    @property
    def state(self):
        state = {
            "PC": self.PC,
            "REG": self.REG.to_json(),
            "MEM": self.MEM.to_json(),
            "CC": self.CC,
            "STAT": self.STAT,
        }
        return state

    @state.setter
    def state(self, value): 
        self.PC = value.pop('PC')
        self.CC = value.pop('CC')
        self.STAT = value.pop('STAT')
        self.MEM = Memory.from_json(value.pop('MEM'))
        self.REG = Registers.from_json(value.pop('REG'))

    def load_program(self, buffer):
        self.MEM.load_yo_buffer(buffer)

    def cond(self, ifun):

        ZF = bool(self.CC['ZF'])
        SF = bool(self.CC['SF'])
        OF = bool(self.CC['OF'])

        if ifun == CONDCode.NC:
            return True
        elif ifun == CONDCode.LE:
            return ZF ^ OF | SF
        elif ifun == CONDCode.L:
            return SF ^ OF
        elif ifun == CONDCode.E:
            return ZF
        elif ifun == CONDCode.NE:
            return not ZF
        elif ifun == CONDCode.GE:
            return not (SF ^ OF)
        elif ifun == CONDCode.G:
            return not (ZF ^ OF | SF)

    def update_CC(self, ifun, a, b, t):
        self.CC["ZF"] = int(t == 0)
        self.CC["SF"] = int(bool(t >> 63))

        if ifun == OPQCode.ADD:
            self.CC["OF"] = int(bool(a < 0 == b < 0 and t < 0 != a < 0))
        elif ifun == OPQCode.SUB:
            self.CC["OF"] = int(bool(a < 0 == b < 0 and t < 0 != b < 0))
        else:
            self.CC["OF"] = 0

    def op(self, ifun):
        if ifun == OPQCode.ADD:
            return lambda a, b: b + a
        elif ifun == OPQCode.SUB:
            return lambda a, b: b - a
        elif ifun == OPQCode.AND:
            return lambda a, b: b & a
        elif ifun == OPQCode.XOR:
            return lambda a, b: b ^ a

    def fetch_decode_execute(self):
        opcode = self.MEM.get_byte(self.PC)
        icode, ifun = bisect_byte(opcode)
        try:
            if opcode == OPCode.HALT:
                self.STAT = STATCode.HLT
            elif opcode == OPCode.NOP:
                val_p = self.PC + 1
                self.PC = val_p
            elif opcode in (OPCode.RRMOVQ,
                            OPCode.CMOVLE,
                            OPCode.CMOVL,
                            OPCode.CMOVE,
                            OPCode.CMOVNE,
                            OPCode.CMOVGE,
                            OPCode.CMOVG):
                val_p = self.PC + 2
                if self.cond(ifun):
                    ra, rb = bisect_byte(self.MEM.get_byte(self.PC + 1))
                    val_a = self.REG[ra]
                    self.REG[rb] = val_a    
                self.PC = val_p
            elif opcode == OPCode.IRMOVQ:
                _, ra = bisect_byte(self.MEM.get_byte(self.PC + 1))
                val_p = self.PC + 10
                val_c = self.MEM.get_quad(self.PC + 2)
                self.REG[ra] = val_c
                self.PC = val_p
            elif opcode == OPCode.RMMOVQ:
                ra, rb = bisect_byte(self.MEM.get_byte(self.PC + 1))
                val_p = self.PC + 10
                val_c = self.MEM.get_quad(self.PC + 2)
                val_a = self.REG[ra]
                val_b = self.REG[rb]
                val_e = val_a + val_b
                self.MEM.set_quad(val_e, val_a)
                self.PC = val_p
            elif opcode == OPCode.MRMOVQ:
                ra, rb = bisect_byte(self.MEM.get_byte(self.PC + 1))
                val_c = self.MEM.get_quad(self.PC + 2)
                val_p = self.PC + 10
                val_b = self.REG[rb]
                val_e = val_b + val_c
                val_m = self.MEM.get_quad(val_e)
                self.REG[ra] = val_m
                self.PC = val_p
            elif opcode in (OPCode.ADDQ,
                            OPCode.SUBQ,
                            OPCode.ANDQ,
                            OPCode.XORQ):
                ra, rb = bisect_byte(self.MEM.get_byte(self.PC + 1))
                val_p = self.PC + 2
                val_a = self.REG[ra]
                val_b = self.REG[rb]
                val_e = self.op(ifun)(val_a, val_b)
                self.update_CC(ifun, val_a, val_b, val_e)
                self.REG[rb] = val_e
                self.PC = val_p
            elif opcode in (OPCode.JMP,
                            OPCode.JLE,
                            OPCode.JL,
                            OPCode.JE,
                            OPCode.JNE,
                            OPCode.JGE,
                            OPCode.JG):
                val_p = self.PC + 9
                if self.cond(ifun):
                    val_c = self.MEM.get_quad(self.PC + 1)
                    self.PC = val_c
                else:
                    self.PC = val_p
            elif opcode == OPCode.CALL:
                val_c = self.MEM.get_quad(self.PC + 1)
                val_p = self.PC + 9
                val_b = self.REG[Registers.RSP]
                val_e = val_b - 8

                self.MEM.set_quad(val_e, val_p)
                self.REG[Registers.RSP] = val_e
                self.PC = val_c
            elif opcode == OPCode.RET:
                val_p = self.PC + 1
                val_a = self.REG[Registers.RSP]
                val_b = self.REG[Registers.RSP]
                val_e = val_b + 8
                val_m = self.MEM.get_quad(val_a)
                self.REG[Registers.RSP] = val_e
                self.PC = val_m
            elif opcode == OPCode.PUSHQ:
                ra, _ = bisect_byte(self.MEM.get_byte(self.PC + 1))
                val_p = self.PC + 2
                val_a = self.REG[ra]
                val_b = self.REG[Registers.RSP]
                val_e = val_b - 8
                self.REG[Registers.RSP] = val_e
                self.MEM.set_quad(val_e, val_a)
                self.PC = val_p
            elif opcode == OPCode.POPQ:
                ra, _ = bisect_byte(self.MEM.get_byte(self.PC + 1))
                val_p = self.PC + 2
                val_a = self.REG[Registers.RSP]
                val_b = self.REG[Registers.RSP]
                val_e = val_b + 8
                val_m = self.MEM.get_quad(val_a)
                self.REG[Registers.RSP] = val_e
                self.REG[ra] = val_m
                self.PC = val_p
            elif opcode in (OPCode.IADDQ,
                            OPCode.ISUBQ,
                            OPCode.IANDQ,
                            OPCode.IXORQ):
                _, ra = bisect_byte(self.MEM.get_byte(self.PC + 1))
                val_p = self.PC + 10
                val_c = self.MEM.get_quad(self.PC + 2)
                val_a = self.REG[ra]
                val_e = self.op(ifun)(val_c, val_a)
                self.update_CC(ifun, val_c, val_a, val_e)
                self.REG[ra] = val_e
                self.PC = val_p
            else:
                raise BadInstruction
        except BadAddress:
            self.STAT = STATCode.ADR
        except BadInstruction:
            self.STAT = STATCode.INS

    def run(self):
        while self.STAT == STATCode.AOK:
            self.fetch_decode_execute()
            yield self.state
