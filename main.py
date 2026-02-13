# DEMO PROJECT
# im moving the project to rust to learn more and because python is slow


def parse(string, char, appendlast=False, stripnewlines=True, begin_chars = {"[", "(", "{"}, end_chars = {"]", ")", "}"}): # parse anything by a character but ignore if inside quotes or parenthathes
    if stripnewlines:
        string = string.replace("\n","") # strip \n
    quotecheck = True
    escaped = False
    nest = 0
    ls = []
    finstr = ""
    for i in string:
        if i == "\"" and not escaped:
            quotecheck = not quotecheck
        elif i == "\\":
            escaped = True
        if quotecheck and not escaped:
            if i in begin_chars:
                nest += 1
            elif i in end_chars:
                nest -= 1
            if i == char and nest == 0: # if on division mark, only runs if its not inside parenthathes or quotes
                ls.append(finstr.lstrip())
                finstr = ""
                continue
        if not i == "\\" or escaped:
            finstr += i # append current character to full string
        if escaped and not i == "\\":
            escaped = False
    if appendlast:
        ls.append(finstr)
    return ls

def getfile(file): # jsut, get file i guess?
    with open(file, "r") as f:
        return f.read()
def compilecode(code): # planning more for this, just splits up the code by ; as newlines and . to seperate commands and values
    parsed = parse(code, ";")
    compiled = []
    for i in parsed:
        lines = parse(i, ".", True)
        compiled.append(lines)
    return compiled

def interpret_val(inp, args=[]): # interpret values
    expsol = inp # solved expression
    def solve(exp, args_):
        # tokenize expression
        quotecheck = False
        escaped = False
        tokens = []
        chars = ""
        regops = {"+","-","*","/","=","==","<=",">=","<",">","!=","+=","-=","*=","/=","!","||","&&","in"} # operators that use 2 values on each side and the symbol in between, like 1 + 1
        idx = 0
        while idx < len(exp):
            i = exp[idx]
            if i in regops and not quotecheck and not escaped: # if pointer is on operator
                if exp[idx+1] in {"=","|","&"}: # check if next character is expected to be in a 2-character expression symbol
                    if i + exp[idx+1] in regops:
                        tokens.append(chars)
                        chars = ""
                        tokens.append(i + exp[idx+1])
                        idx += 1
                elif i == "-" and exp[idx-1] in regops: # check for negative numbers
                    chars += "-"
                else:
                    tokens.append(chars)
                    chars = ""
                    tokens.append(i)
            elif chars in vars and exp.replace(" ", "")[idx:idx+2] not in {"=", "+=", "-=", "*=", "/="}:
                    chars = str(vars[chars])
            elif i == '"' and not escaped: # handle escaping and quotes
                quotecheck = not quotecheck
            elif i == '\\':
                escaped = True
                continue
            elif not (not quotecheck and i == " "):
                chars += str(i)
            if escaped:
                escaped = False
                continue
            idx += 1
        if chars in vars and exp.replace(" ", "")[idx:idx+2] not in {"=", "+=", "-=", "*=", "/="}:
            chars = str(vars[chars])
        tokens.append(chars)
        # solve step by step ↓
        # solve 1 expression
        def solvesmall(tokens):
            if len(tokens) >= 3:                  
                if tokens[1] in regops:
                    if tokens[1] == "=":
                        vars[tokens[0]] = tokens[2]     
                    elif tokens[1] == "+=":
                        vars[tokens[0]] = int(tokens[2]) + int(vars[tokens[0]])
                    elif tokens[1] == "-=":
                        vars[tokens[0]] = int(tokens[2]) - int(vars[tokens[0]])
                    elif tokens[1] == "*=":
                        vars[tokens[0]] = int(tokens[2]) * int(vars[tokens[0]])
                    elif tokens[1] == "/=":
                        vars[tokens[0]] = int(tokens[2]) / int(vars[tokens[0]])
                    else:
                        tokens[0] = eval(str(tokens[0])+tokens[1]+str(tokens[2]))
                    tokens.pop(1)
                    tokens.pop(1)
        # go through expressions
        while len(tokens) > 1:
            solvesmall(tokens)
        return tokens[0]
    
    def isfinquery(exp): # check
        quotecheck = False
        escaped = False
        for i in exp:
            if i in {"(",")"} and not escaped and not quotecheck:
                return False
            if i == '"' and not escaped:
                quotecheck = not quotecheck
            if escaped:
                escaped = False
            if i == '\\':
                escaped = True
        return True
    # solve parentheses
    quotecheck = False
    escaped = False
    stack = []
    while not isfinquery(expsol):
        index = 0
        while index < len(expsol):
            char = expsol[index]
            if char == "(" and not quotecheck and not escaped:
                stack.append(index)
            if char == ")" and not quotecheck and not escaped:
                # handle expressions
                lastopen = stack.pop()
                # print("solving: ",expsol)
                expsol = expsol[:lastopen] + str(solve(expsol[lastopen+1:index], args)) + expsol[index+1:]
                index = lastopen
                continue
            if char == '"' and not escaped:
                quotecheck = not quotecheck
            if escaped:
                escaped = False
            if char == '\\':
                escaped = True
            index+=1
    # print("solving:",expsol)
    return(solve(expsol, args))

def error(msg,line=(),end=True):
    if len(line) > 1:
        print(f"error at line {line[0]}:\n{line[1]}")
    else:
        print("error at unknown location")
        print("this is not as scary as it looks, it just means the error was spotted outside of the main loop in the interpreter")
    print("error message:")
    print(msg)
    print("stopping..")
    sys.exit()

def interpret_code(parsed,args=[]): # interpret command for command
    i = 0 # use index for line number, more flexible than `for i`
    while i <= len(parsed) - 1:
        cmd = parsed[i]
        match cmd[0]:
            case "echo":
                print(interpret_val(cmd[1], args=args))
            case "sleep":
                time.sleep(int(interpret_val(cmd[1], args=args)))
            case "":
                if len(cmd) == 2:
                    interpret_val(cmd[1], args=args)
                else:
                    error("empty command only takes 1 argument, have you checked for unquoted dots?",(i,".".join(cmd)))
            case "if":
                if interpret_val(cmd[1], args=args):
                    if len(cmd) == 4:
                        interpret_code(compilecode(cmd[2][1:-1]),args+ast.literal_eval(interpret_val(cmd[3])))
                    elif len(cmd) == 3:
                        interpret_code(compilecode(cmd[2][1:-1]),args)
                    else:
                        error("invalid amount of values for if statement (if statements only take 2-3 + command), use like so;\nif.(True/False).{script}.[args];",(i,".".join(cmd)))
            case "while":
                while True:
                    if not interpret_val(cmd[1], args=args):
                        break
                    if len(cmd) == 4:
                        interpret_code(compilecode(cmd[2][1:-1]),args+ast.literal_eval(interpret_val(cmd[3])))
                    elif len(cmd) == 3:
                        interpret_code(compilecode(cmd[2][1:-1]),args)
                    else:
                        error("invalid amount of values for while loop (while loops only take 2-3 + command), use like so;\nwhile.(amt).{script}.[args];",(i,".".join(cmd)))
        i += 1

def run(file,args=[]): # run.. file? simpler than whatever this is at least, cdrl.run() i guess idk im tired
    interpret_code(compilecode(getfile(file)),args)

import ast
import time
import sys
start = time.perf_counter()
global vars
vars = {"testvar":10}
run("test.cdrl")
print("time elapsed: ",time.perf_counter()-start, "s")
