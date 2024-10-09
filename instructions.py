from atypes import *

INSTRUCTION_SIZE = 1
UINT64_SIZE = 8
RELATIVE_REFERENCE = 2
INDEX_SIZE = 2

class Instruction:
    def compile(self, state: CompilerState):
        return ''.encode('utf-8')
    
    def __len__(self):
        return 0
    
class ReferenceInstruction(Instruction):
    def __init__(self, prefix: bytes, reference: Reference, relative: bool):
        self.prefix = prefix
        self.reference = reference
        self.relative = relative

    def compile(self, state: CompilerState):
        if self.relative:
            if state.current <= state.references[self.reference.name]:
                return self.prefix + (state.references[self.reference.name] - state.current - RELATIVE_REFERENCE - 1).to_bytes(RELATIVE_REFERENCE, byteorder='big')
            else:
                ref = (state.current - state.references[self.reference.name] + 1 + RELATIVE_REFERENCE) | (0b1 << 15)
                return self.prefix + ref.to_bytes(RELATIVE_REFERENCE, byteorder='big')
        return self.prefix + state.references[self.reference.name].to_bytes(UINT64_SIZE, byteorder='big')
    
    def __len__(self):
        if self.relative:
            return len(self.prefix) + RELATIVE_REFERENCE
        return len(self.prefix) + UINT64_SIZE

class BytesInstruction(Instruction):
    def __init__(self, bts: bytes):
        self.bts = bts

    def compile(self, state: CompilerState = None):
        return self.bts
    
    def __len__(self):
        return len(self.bts)

class InstructionFactory:
    def __init__(self, opcode: int):
        self.opcode = opcode

    def build(self):
        return BytesInstruction(self.opcode.to_bytes(INSTRUCTION_SIZE, byteorder='big'))

class IPush(InstructionFactory):
    def __init__(self, opcode, size: int):
        super().__init__(opcode)
        self.size = size

    def build(self, value: Number):
        return BytesInstruction(super().build().compile() + value.value.to_bytes(self.size, byteorder='big'))


class Stackable(InstructionFactory):
    def __init__(self, opcode):
        super().__init__(opcode)

    def build(self, index: Index):
        return BytesInstruction(super().build().compile() + index.value.to_bytes(INDEX_SIZE, byteorder='big'))

class BPush(InstructionFactory):
    def __init__(self, opcode):
        super().__init__(opcode)

    def build(self, block: Block):
        return BytesInstruction(super().build().compile() + len(block.bt).to_bytes(UINT64_SIZE, byteorder='big') + block.bt)

class Change(InstructionFactory):
    def __init__(self, opcode):
        super().__init__(opcode)

    def build(self, first: Index, second: Index):
        return BytesInstruction(super().build().compile() + first.value.to_bytes(INDEX_SIZE, byteorder='big') + second.value.to_bytes(INDEX_SIZE, byteorder='big'))

class Jmp(InstructionFactory):
    def __init__(self, opcode, relative: bool):
        super().__init__(opcode)
        self.relative = relative

    def build(self, reference: Reference):
        return ReferenceInstruction(super().build().compile(), reference, self.relative)
    
class Counter():
    def __init__(self):
        self.value = 0
    
    def count(self):
        value = self.value
        self.value += 1
        return value

counter = Counter()

INSTRUCTIONS = {
    'IPUSH64': IPush(counter.count(), 8),         # IPUSH [value]
    'IPUSH8': IPush(counter.count(), 1),          # IPUSH [value]
    'SPUSH': Stackable(counter.count()),          # SPUSH #[value]
    'BPUSH': BPush(counter.count()),              # BPUSH [length], [bytes...]
    'DROPN': Stackable(counter.count()),          # DROP [value]
    'CHG': Change(counter.count()),               # CHG #[value], #[value]
    'SWAP': InstructionFactory(counter.count()),          # ###
    
    'BHASH': InstructionFactory(counter.count()),
    'BLEN': InstructionFactory(counter.count()),

    'MKSLICE': InstructionFactory(counter.count()),       # MKSLICE
    'IREAD64': InstructionFactory(counter.count()),       # U64READ
    'IREAD8': InstructionFactory(counter.count()),        # U8READ
    'BREAD': InstructionFactory(counter.count()),        # BREAD
    'SLLEN': InstructionFactory(counter.count()),        # SLLEN

    'MKBUILDER': InstructionFactory(counter.count()),    # MKBUILDER
    'IWRITE64': InstructionFactory(counter.count()),     # U64WRITE
    'IWRITE8': InstructionFactory(counter.count()),      # U8WRITE
    'BWRITE': InstructionFactory(counter.count()),       # BWRITE
    'BUILD': InstructionFactory(counter.count()),        # BUILD
    'BLLEN': InstructionFactory(counter.count()),        # BUILD

    'ADD': InstructionFactory(counter.count()),          # ADD
    'SUB': InstructionFactory(counter.count()),          # SUB
    'MUL': InstructionFactory(counter.count()),          # MUL
    'DIV': InstructionFactory(counter.count()),          # DIV
    'MOD': InstructionFactory(counter.count()),          # MOD
    'INC': InstructionFactory(counter.count()),          # MOD ###

    'CMB': InstructionFactory(counter.count()),          # >
    'CML': InstructionFactory(counter.count()),          # <
    'CMBE': InstructionFactory(counter.count()),         # >=
    'CMLE': InstructionFactory(counter.count()),         # <=
    'CME': InstructionFactory(counter.count()),          # ==
    'CMNE': InstructionFactory(counter.count()),         # !=

    'JMP': Jmp(counter.count(), False),          # JMP &[ip]
    'JMT': Jmp(counter.count(), False),          # JMT &[ip]
    'JMF': Jmp(counter.count(), False),          # JMF &[ip]
    'RJMP': Jmp(counter.count(), True),          # Relative JMP &[ip]
    'RJMT': Jmp(counter.count(), True),          # Relative JMT &[ip]
    'RJMF': Jmp(counter.count(), True),          # Relative JMF &[ip]
    'CALL': Jmp(counter.count(), False),         # CALL &[ip]
    'RET': InstructionFactory(counter.count()),          # RET

    'HALT': InstructionFactory(counter.count()),          # HALT

    'LDATA': InstructionFactory(counter.count()),         # LDATA
    'SDATA': InstructionFactory(counter.count()),         # SDATA
    'MESSAGE': InstructionFactory(counter.count()),       # MESSAGE
    'SEND': InstructionFactory(counter.count()),
}
