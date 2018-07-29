def tokenize(s: str) -> list:
    current = ''
    tokens = []
    for c in s:
        if c in '()':
            if len(current) > 0:
                tokens.append(current)
                current = ''
            tokens.append(c)
        elif c.isspace():
            if len(current) > 0:
                tokens.append(current)
                current = ''
        else:
            current = current + c
    return tokens


def parse_tokens(tokens: list):
    res = []
    if len(tokens) == 0:
        raise SyntaxError()
    current = tokens.pop(0)
    if current == '(':
        while tokens[0] != ')':
            res.append(parse_tokens(tokens))
        tokens.pop(0)
        return res
    elif current == ')':
        raise SyntaxError()
    else:
        try:
            res.append(int(current))
        except ValueError:
            res.append(str(current))
        while tokens[0] != ')':
            current = tokens.pop(0)
            res.append(current)
        return res


def meval(expr, env):
    if is_primitive(expr):
        return eval_primitive(expr)
    elif is_if(expr):
        return eval_if(expr, env)
    elif is_definition(expr):
        return eval_definition(expr, env)
    elif is_name(expr):
        return eval_name(expr, env)
    elif is_lambda(expr):
        return eval_lambda(expr, env)
    elif is_application(expr):
        return eval_application(expr, env)
    else:
        eval_error('Unknown expression type:' + str(expr))


def is_number(expr):
    return isinstance(expr, str) and expr.isdigit()  # isinstance()保证isdigit()的调用安全


def is_primitive_procedure(expr):
    return callable(expr)


def is_primitive(expr):
    return is_number(expr) or is_primitive_procedure(expr)


def eval_primitive(expr):
    if is_number(expr):
            return int(expr)
    else:
        return expr


def primitive_plus(operands: list):
    if len(operands) == 0:
        return 0
    else:
        return operands[0] + primitive_plus(operands[1:])


def primitive_minus(operands: list):
    if len(operands) == 1:
        return 0 - operands[0]
    elif len(operands) == 2:
        return operands[0] - operands[1]
    else:
        eval_error("- expects 1 or 2 operands, given %s:%s" % (len(operands), str(operands)))


def primitive_times(operands: list):
    if len(operands) == 1:
        return 1
    else:
        return operands[0] * primitive_times(operands[1:])


def check_operands(oprands, num, prim):
    if len(oprands) != num:
        eval_error("Primitive %s expected %s operands, given %s:%s" % (prim, num, len(oprands), str(oprands)))


def primitive_equals(operands: list):
    check_operands(operands, 2, '=')
    return operands[0] == operands[1]


def primitive_lessthan(operands: list):
    check_operands(operands, 2, '<')
    return operands[0] < operands[1]


def eval_error(s):
    print(s)


# ##############################Primitives############################ #
def is_special_form(expr, keyword):
    return isinstance(expr, list) and len(expr) > 0 and expr[0] == keyword


def is_if(expr):
    return is_special_form(expr, 'if')


def eval_if(expr, env):
    if meval(expr[1], env) != False:
        return meval(expr[2], env)
    else:
        return meval(expr[3], env)


# ################################If################################# #
class Environment:
    def __init__(self, parent):
        self.parent = parent
        self.frame = {}

    def add_variable(self, name, value):
        self.frame[name] = value

    def lookup_variable(self, name):
        if name in self.frame:
            return self.frame[name]
        elif self.parent:
            return self.parent.lookup_variable(name)
        else:
            eval_error("Undefined name: %s" % name)


# ###############################Environment######################### #
def is_definition(expr):
    return is_special_form(expr, 'define')


def eval_definition(expr, env: Environment):
    name = expr[1]
    value = meval(expr[2], env)
    env.add_variable(name, value)


def is_name(expr):
    return isinstance(expr, str)


def eval_name(expr, env: Environment):
    return env.lookup_variable(expr)


# ###############################Definition######################### #
class Procedure:
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

    def get_params(self):
        return self.params

    def get_body(self):
        return self.body

    def get_env(self):
        return self.env


# ######################Definitions and Names####################### #
def is_lambda(expr):
    return is_special_form(expr, 'lambda')


def eval_lambda(expr, env):
    return Procedure(expr[1], expr[2], env)


# ############################Procedures############################ #
def is_application(expr):
    return isinstance(expr, list)


def eval_application(expr, env):
    subexprs = expr
    subexprvals = list(map(lambda sexpr: meval(sexpr, env), subexprs))
    return mapply(subexprvals[0], subexprvals[1:])


def mapply(proc, operands):
    if is_primitive_procedure(proc):
        return proc(operands)
    elif isinstance(proc, Procedure):
        params = proc.get_params()
        newenv = Environment(proc.get_env())
        if len(params) != len(operands):
            eval_error('Parameter length mismatch:%s given operands %s' % (str(proc), str(operands)))
        for i in range(0, len(params)):
            newenv.add_variable(params[i], operands[i])
        return meval(proc.get_body(), newenv)
    else:
        eval_error("Application of non-procedure:%s" % (proc))


# ##########################Applocation############################ #
def eval_loop():
    genv = Environment(None)
    genv.add_variable('true', True)
    genv.add_variable('false', False)
    genv.add_variable('+', primitive_plus)
    genv.add_variable('-', primitive_minus)
    genv.add_variable('*', primitive_times)
    genv.add_variable('=', primitive_equals)
    genv.add_variable('<', primitive_lessthan)
    while True:
        inv = input("Charme>")
        if inv == 'quit':
            break
        for expr in parse_tokens(tokenize(inv)):
            print(str(meval(expr, genv)))


if __name__ == '__main__':
    eval_loop()
