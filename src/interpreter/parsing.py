from traceback import format_exc

from src.interpreter.expression import Expression


class Codebase:
    def __init__(self, lines):
        self.lines = lines
        self.variables = {}
        self.output = ""


def parseCode(program: str):
    parseTree = []
    activityStack = [parseTree]

    newString = True
    backslashed = False
    inString = False

    # parse the program!
    for c in program:

        if newString and c not in ["[", " ", "\n"]:
            activityStack[-1].append("")
            newString = False

        if len(activityStack) == 1:
            if c == "[":
                activityStack[-1].append([])
                activityStack.append(activityStack[-1][-1])
                newString = True
            else:
                activityStack[-1][-1] += c

        elif backslashed:
            if c == "n":
                activityStack[-1][-1] += "\n"
            else:
                activityStack[-1][-1] += c
            backslashed = False

        elif inString:
            if c == "\\":
                backslashed = True
            elif c == "\"":
                inString = False
            else:
                activityStack[-1][-1] += c

        elif c == "\\":
            backslashed = True
        elif c == "\"":
            inString = True
        elif c in [" ", "\n"]:
            newString = True
        elif c == "[":
            activityStack[-1].append([])
            activityStack.append(activityStack[-1][-1])
            newString = True
        elif c == "]":
            activityStack.pop()
            if len(activityStack) == 1:
                activityStack[-1].append("")
        else:
            activityStack[-1][-1] += c

    return parseTree


def runCode(code: str):
    parsed_code = parseCode(code)
    codebase = Codebase(parsed_code)

    for statement in parsed_code:
        try:
            if type(statement) == str:
                result = statement
            else:
                result = Expression(statement, codebase)

            print(result)
            if result is not None:
                codebase.output += str(result)

        except Exception as e:
            errmsg = f"ERROR at `{statement}`:\n{e}"
            print(f"{errmsg}\n\n{format_exc()}") # print stack trace too
            return errmsg

    # print(codebase.variables)
    # print(codebase.output)
    if len(codebase.output) > 2000:
        return "ERROR: Output too long!"
    return codebase.output
