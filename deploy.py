from tokenizer import Tokenizer
from analyser import Analyser
from compiler import Compiler
import hashlib 
import requests

import sys

with open(sys.argv[-1], encoding='utf-8') as f:
    tokenizer = Tokenizer(f.read())
    tokenizer.parse()
    analyser = Analyser(tokenizer.tokens)
    analyser.analys()
    compiler = Compiler(analyser.program)
    program = compiler.compile()
    if analyser.program.initial_data is not None:
        executive = len(program).to_bytes(8, byteorder='big') + program + len(analyser.program.initial_data.bt).to_bytes(8, byteorder='big') + analyser.program.initial_data.bt
        receiver = 'abcdef'
        message = 'hello'
        data = {
            "type": "external",
            "receiver": hashlib.sha256(executive).digest().hex(),
            "init": {
                "program": program.hex(),
                "data": analyser.program.initial_data.bt.hex()
            },
            "opcode": 0,
            "body": (len(receiver).to_bytes(8, byteorder='big') + receiver.encode('utf-8') + len(message).to_bytes(8, byteorder='big') + message.encode('utf-8')).hex()
        }
        response = requests.post('http://localhost:8080/message/send', json=data)
        print('Message sent successfully:', response.json())