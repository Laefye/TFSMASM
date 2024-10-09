from analyser import *

class Compiler:
    def __init__(self, program: Program):
        self.program = program
        self.code = bytes()
        self.references: dict[str, int] = {}

    def calculate_references(self):
        bts = 0
        for part in self.program.code:
            if isinstance(part, Instruction):
                bts += len(part)
            if isinstance(part, Section):
                self.references[part.name] = bts

    def compile(self):
        self.calculate_references()
        for part in self.program.code:
            if isinstance(part, Instruction):
                self.code += part.compile(state=CompilerState(self.references, len(self.code)))
                pass
        program = bytes()
        if self.program.internal is not None:
            program += b'\1' + self.references[self.program.internal.name].to_bytes(UINT64_SIZE, byteorder='big')
        else:
            program += b'\0'
        if self.program.external is not None:
            program += b'\1' + self.references[self.program.external.name].to_bytes(UINT64_SIZE, byteorder='big')
        else:
            program += b'\0'
        if self.program.view is not None:
            program += b'\1' + self.references[self.program.view.name].to_bytes(UINT64_SIZE, byteorder='big')
        else:
            program += b'\0'
        program += self.code
        return program
        
