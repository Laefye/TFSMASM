from tokenizer import Tokenizer
from analyser import Analyser
from compiler import Compiler
import hashlib 

import sys

with open(sys.argv[-1], encoding='utf-8') as f:
    tokenizer = Tokenizer(f.read())
    tokenizer.parse()
    analyser = Analyser(tokenizer.tokens)
    analyser.analys()
    compiler = Compiler(analyser.program)
    program = compiler.compile()
    print('program: ' + program.hex())
    if analyser.program.initial_data is not None:
        executive = len(program).to_bytes(8, byteorder='big') + program + len(analyser.program.initial_data.bt).to_bytes(8, byteorder='big') + analyser.program.initial_data.bt
        print('executive: ' + executive.hex())
        print('address: ' + hashlib.sha256(executive).digest().hex())