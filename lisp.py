from functools import reduce
import os, sys, re

RESERVED = ['define', 'if', 'mod', 'and', 'or', 'not', 'fun']

class Env(dict):    #scope
    def __init__(self, parms=(), args=(), outer=None):
        super().__init__()
        self.update(zip(parms, args))
        self.outer = outer

    def __getitem__(self, key):
        if key in self: return super().__getitem__(key)
        return self.outer[key] if self.outer else None

    def print_env(self):
        for key, value in self.items():
            print(key, value.get_name() if type(value) == Func else value)
        
        if self.outer is not None:
            print("outer")
            self.outer.print_env()
    
    def find(self, var):
        return self[var] if (var in self) else self.outer.find(var) if self.outer or self.outer.outer else None

class Func():
    def __init__(self, func_name="non", func=None, num_args=None, arg_compare=None, type_args=None):
        self.func, self.name= func, func_name
        self.num_args, self.type_args, self.arg_compare = num_args, type_args, arg_compare
    
    def __call__(self, *args):
        self._check_type(args)
        return self.func(*args)
    
    def get_name(self):
        return self.name

    def _check_type(self, args):
        assert eval(f' {self.num_args} {self.arg_compare} {len(args)}'), (   # check number of args
                    f'Expected {self.num_args} arguments, got {len(args)}')
        if self.type_args is not None:  # check type of args
            if self.type_args == '=':
                arg_type = type(args[0])
            else:
                arg_type = self.type_args
            
            for arg in args:
                assert type(arg) == arg_type, (f'Expected argument with type {arg_type}, got {type(arg) if type(arg) != Func else "function"}')

    def __repr__(self):
        return str(self)

Arg = (bool, int)
RESERVED_OP = ('+', '-', '*', '/', 'mod', '=', '>', '<', 'and', 'or', 'not', 'print-num', 'print-bool')

def initial_Env() -> Env:  # scope
    env = Env()
    env.update({
        '+':         Func('+', lambda *args: sum(args), 2, '<=', int),
        '-':         Func('-', lambda x, y: x - y, 2, '==', int),
        '*':         Func('*', lambda *args: reduce(lambda x, y: x * y, args), 2, '<=', int),
        '/':         Func('/', lambda x, y: x // y, 2, '==', int),
        'mod':       Func('mod', lambda x, y: x % y, 2, '==', int),
        '=':         Func('=', lambda *args: all(arg == args[0] for arg in args), 2, '<=', int),
        '>':         Func('>', lambda x, y: x > y, 2, '==', int),
        '<':         Func('<', lambda x, y: x < y, 2, '==', int),
        'and':       Func('and', lambda *arg: all(arg), 2, '<=', bool),
        'or':        Func('or', lambda *arg: any(arg), 2, '<=', bool),
        'not':       Func('not', lambda x: not x, 1, '==', bool),
        'print-num': Func('print-num', lambda x: print(x), 1, '==', int),
        'print-bool':Func('print-bool', lambda x: print({True: '#t', False: '#f'}[x]), 1, '==', bool)
    })
    return env

def parse(code: str) -> list:
    return read_expr(tokenize(code))

def tokenize(code: str) -> list:
    return code.replace('(', ' ( ').replace(')', ' ) ').split()

def read_expr(tokens: list):
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')' and len(tokens) > 0:
            L.append(read_expr(tokens))     # recursive call
        tokens.pop(0) # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token: str) -> int or bool:
    try: return int(token)
    except ValueError:
        return str(token)

def id_check(id):
    id_re = r"[a-z]([a-z]|[0-9]|\-)*"
    if id in RESERVED:
        raise SyntaxError(f'{id} is a reserved word')
    if not re.fullmatch(id_re, id):
        raise SyntaxError(f'{id} is not a valid identifier')


def evalute(exp, env, func=None):
    # print("evalute:", exp)
    if isinstance(exp, int) or isinstance(exp, bool):
        return exp
    if exp == '#t' or exp == '#f':
        return True if exp == '#t' else False

    if isinstance(exp, str):
        try:
            return env.find(exp)    #會從自己的env或outer_env找變數
        except Exception as e:
            print(e)
            raise NameError(f'Undefined name: {exp}')

    op, *args = exp

    if op == 'if':
        test_exp, then, else_exp = args
        bool_exp = evalute(test_exp, env)
        if not isinstance(bool_exp, bool):
            raise TypeError(f'IF: Expected bool, got {type(bool_exp)}')
        exp = then if bool_exp else else_exp
        return  evalute(exp, env)
    elif op == 'define':
        var, exp = args
        id_check(var)
        env[var] = evalute(exp, env)
        return
    elif op == 'fun':
        parameter, *defines,exp = args
        # print("defines: ", defines)
        inside_env = Env(outer=env)
        for define in defines:
            evalute(define, inside_env)
        return Func(func=lambda *args: evalute(exp, Env(parameter, args, outer=inside_env) ), num_args=len(parameter), arg_compare='==')
    elif type(op) == str and env.find(op) != None: #處裡有定義的函數
        func = env.find(op)
        if not isinstance(func, Func):
            raise TypeError(f'{op} is not a function')
        func_arg = [evalute(arg, env) for arg in args]
        for param, evaluated in zip(args, func_arg):
            if not isinstance(evaluated, Arg):  # 如果回傳值不是參數型態，則拋出錯誤
                if type(evaluated) == Func and evaluated.get_name() in RESERVED_OP:
                    raise SyntaxError(f"unexpected '{param}'")
        return func(*func_arg)
    else:   #處理op是list的情況
        func = evalute(op, env)
        if not isinstance(func, Func):
            raise TypeError(f'{op} is not a function')
        func_arg = [evalute(arg, env) for arg in args]
        for param, evaluated in zip(args, func_arg):
            if not isinstance(evaluated, Arg):  # 如果回傳值不是參數型態，則拋出錯誤
                if type(evaluated) == Func and evaluated.get_name() in RESERVED_OP:
                    raise SyntaxError(f"unexpected '{param}'")
        return func(*func_arg)


def run(code: str):
    program = parse(f'({code})')
    global_env = initial_Env()
    for exp in program:
        evalute(exp, global_env)

if __name__ == '__main__':
    sys.tracebacklimit = 0
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        run(open(sys.argv[1]).read())

    else:
        while True:
            try:
                run(input('lisp> '))
            except:
                break
