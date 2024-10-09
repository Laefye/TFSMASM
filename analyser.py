from tokenizer import *
from instructions import *

class Program:
    def __init__(self):
        self.internal: Reference | None = None
        self.external: Reference | None = None
        self.view: Reference | None = None
        self.initial_data: Block | None = None
        self.code: list[Instruction | Section] = []

class Analyser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.i = 0
        self.program = Program()

    def d(self):
        return self.i < len(self.tokens)
    
    def advance(self):
        self.i += 1

    def c(self):
        return self.tokens[self.i]
    
    def execute_macros(self):
        if not isinstance(self.c(), TokenMacros):
            return False
        macros: TokenMacros = self.c()
        self.advance()
        if macros.name == 'internal':
            if not isinstance(self.c(), TokenReference):
                raise Exception('Need reference in internal')
            reference: TokenReference = self.c()
            self.advance()
            self.program.internal = Reference(reference.name)
        elif macros.name == 'external':
            if not isinstance(self.c(), TokenReference):
                raise Exception('Need reference in external')
            reference: TokenReference = self.c()
            self.advance()
            self.program.external = Reference(reference.name)
        elif macros.name == 'view':
            if not isinstance(self.c(), TokenReference):
                raise Exception('Need reference in view')
            reference: TokenReference = self.c()
            self.advance()
            self.program.view = Reference(reference.name)
        elif macros.name == 'data':
            if isinstance(self.c(), TokenString):
                string: TokenString = self.c()
                self.advance()
                self.program.initial_data = Block(string.value.encode('utf-8'))
            elif isinstance(self.c(), TokenBlock):
                block: TokenBlock = self.c()
                self.advance()
                self.program.initial_data = Block(bytes.fromhex(block.value))
            else:
                raise Exception('Need data in data, yeah :\\')
        elif macros.name == 'include':
            if not isinstance(self.c(), TokenString):
                raise Exception('Include need string')
            include_file: TokenString = self.c()
            self.advance()
            with open(include_file.value, encoding='utf-8') as f:
                tokenizer = Tokenizer(f.read())
                tokenizer.parse()
                new_tokens = self.tokens[:self.i]
                new_tokens.extend(tokenizer.tokens)
                new_tokens.extend(self.tokens[self.i:])
                self.tokens = new_tokens
        return True
    
    def add_section(self):
        if not isinstance(self.c(), TokenSection):
            return False
        section: TokenSection = self.c()
        self.advance()
        self.program.code.append(Section(section.name))
        return True
    
    def parse_instruction(self):
        if not isinstance(self.c(), TokenInstruction):
            return False
        token_instruction: TokenInstruction = self.c()
        self.advance()
        instruction_factory = INSTRUCTIONS[token_instruction.name]
        if isinstance(instruction_factory, IPush):
            if isinstance(self.c(), TokenNumber):
                number: TokenNumber = self.c()
                self.program.code.append(instruction_factory.build(Number(number.to_int())))
                self.advance()
        elif isinstance(instruction_factory, Stackable):
            if isinstance(self.c(), TokenIndex):
                index: TokenIndex = self.c()
                self.program.code.append(instruction_factory.build(Index(index.to_int())))
                self.advance()
        elif isinstance(instruction_factory, BPush):
            if isinstance(self.c(), TokenString):
                string: TokenString = self.c()
                self.program.code.append(instruction_factory.build(Block(string.value.encode('utf-8'))))
                self.advance()
            elif isinstance(self.c(), TokenBlock):
                block: TokenBlock = self.c()
                self.program.code.append(instruction_factory.build(Block(bytes.fromhex(block.value))))
                self.advance()
        elif isinstance(instruction_factory, Change):
            if isinstance(self.c(), TokenIndex):
                first: TokenIndex = self.c()
                self.advance()
                if isinstance(self.c(), TokenIndex):
                    second: TokenIndex = self.c()
                    self.program.code.append(instruction_factory.build(Index(first.to_int()), Index(second.to_int())))
                    self.advance()
        elif isinstance(instruction_factory, Jmp):
            if isinstance(self.c(), TokenReference):
                reference: TokenReference = self.c()
                self.program.code.append(instruction_factory.build(Reference(reference.name)))
                self.advance()
        elif isinstance(instruction_factory, InstructionFactory):
            self.program.code.append(instruction_factory.build())
        return True

    def analys(self):
        while self.d():
            if self.execute_macros():
                continue
            if self.add_section():
                continue
            if self.parse_instruction():
                continue
            self.advance()