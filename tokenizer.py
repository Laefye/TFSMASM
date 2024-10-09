NEW_LINE = ['\r', '\n']
WHITESPACE = ['\t', ' ']
COMMENT = ';'
STRING = '"'

class Token:
    def __init__(self, type: str):
        self.type = type

class TokenMacros(Token):
    def __init__(self, name: str):
        super().__init__('macros')
        self.name = name

    def __str__(self):
        return f"TokenMacros(name='{self.name}')"

    def __repr__(self):
        return self.__str__()

class TokenSection(Token):
    def __init__(self, name: str):
        super().__init__('section')
        self.name = name

    def __str__(self):
        return f"TokenSection(name='{self.name}')"

    def __repr__(self):
        return self.__str__()

class TokenBlock(Token):
    def __init__(self, value: str):
        super().__init__('block')
        self.value = value

    def __str__(self):
        return f"TokenBlock(value='{self.value}')"

    def __repr__(self):
        return self.__str__()

class TokenReference(Token):
    def __init__(self, name: str):
        super().__init__('reference')
        self.name = name

    def __str__(self):
        return f"TokenReference(name='{self.name}')"

    def __repr__(self):
        return self.__str__()

class TokenString(Token):
    def __init__(self, value: str):
        super().__init__('string')
        self.value = value

    def __str__(self):
        return f"TokenString(value='{self.value}')"

    def __repr__(self):
        return self.__str__()
    
class TokenNumber(Token):
    def __init__(self, value: str):
        super().__init__('number')
        self.value = value

    def __str__(self):
        return f"TokenNumber(value='{self.value}')"

    def __repr__(self):
        return self.__str__()
    
    def size(self):
        if self.value.endswith('u8'):
            return 1
        return 8

    def to_int(self):
        return int(self.value)

class TokenIndex(Token):
    def __init__(self, value: str):
        super().__init__('index')
        self.value = value

    def __str__(self):
        return f"TokenIndex(value='{self.value}')"

    def __repr__(self):
        return self.__str__()
    
    def to_int(self):
        return int(self.value)
    

class TokenInstruction(Token):
    def __init__(self, name: str):
        super().__init__('index')
        self.name = name

    def __str__(self):
        return f"TokenInstruction(name='{self.name}')"

    def __repr__(self):
        return self.__str__()

class Tokenizer:
    def __init__(self, source: str):
        self.source = source
        self.i = 0
        self.tokens = []

    def d(self):
        return self.i < len(self.source)
    
    def advance(self):
        self.i += 1

    def c(self):
        return self.source[self.i]
    
    def is_finish(self):
        if self.c() in NEW_LINE or self.c() in WHITESPACE:
            return True
        return False
    
    def parse_string(self):
        if self.c() != '"':
            return False
        self.advance()
        value = ''
        while self.d() and self.c() != '"':
            value += self.c()
            self.advance()
        self.advance()
        self.tokens.append(TokenString(value))
        return True

    def parse_macro(self):
        if self.c() != '.':
            return False
        self.advance()
        macros = ''
        while self.d() and not self.is_finish():
            macros += self.c()
            self.advance()
        self.tokens.append(TokenMacros(macros))
        return True
    
    def parse_comment(self):
        if self.c() != ';':
            return False
        while self.d() and self.c() not in NEW_LINE:
            self.advance()
        return True
    
    def parse_word(self):
        if self.is_finish():
            return False
        identifier = ''
        while self.d() and not self.is_finish():
            identifier += self.c()
            self.advance()
        if identifier[-1] == ':':
            self.tokens.append(TokenSection(identifier[:-1]))
        else:
            self.tokens.append(TokenInstruction(identifier))
        return True

    def parse_number(self):
        if not self.c().isdigit():
            return False
        number = ''
        while self.d() and not self.is_finish():
            number += self.c()
            self.advance()
        self.tokens.append(TokenNumber(number))
        return True

    def parse_reference(self):
        if self.c() != '&':
            return False
        self.advance()
        name = ''
        while self.d() and not self.is_finish():
            name += self.c()
            self.advance()
        self.tokens.append(TokenReference(name))
        return True
    
    def parse_index(self):
        if self.c() != '#':
            return False
        self.advance()
        index = ''
        while self.d() and not self.is_finish() and self.c().isdigit():
            index += self.c()
            self.advance()
        self.tokens.append(TokenIndex(index))
        return True

    def parse_block(self):
        if self.c() != '[':
            return False
        self.advance()
        hexed = ''
        while self.d() and not self.is_finish() and self.c() != ']':
            hexed += self.c()
            self.advance()
        if self.c() == ']':
            self.advance()
        self.tokens.append(TokenBlock(hexed))
        return True

    def parse(self):
        while self.d():
            if self.parse_comment():
                continue
            if self.parse_macro():
                continue
            if self.parse_reference():
                continue
            if self.parse_number():
                continue
            if self.parse_string():
                continue
            if self.parse_index():
                continue
            if self.parse_block():
                continue
            if self.parse_word():
                continue
            self.advance()

