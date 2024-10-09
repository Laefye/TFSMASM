class Section:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f'{self.name}:'
    
    def __repr__(self):
        return self.__str__()

class Reference:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f'&{self.name}'
    
    def __repr__(self):
        return self.__str__()
    
class Number:
    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        return f'({self.value})'
    
    def __repr__(self):
        return self.__str__()
    
class Index:
    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        return f'#{self.value}'
    
    def __repr__(self):
        return self.__str__()
    
class Block:
    def __init__(self, bt: bytes):
        self.bt = bt

    def __str__(self):
        return f'{self.bt.hex()}'
    
    def __repr__(self):
        return self.__str__()
    
class CompilerState:
    def __init__(self, references: dict[str, int], current: int):
        self.references = references
        self.current = current
