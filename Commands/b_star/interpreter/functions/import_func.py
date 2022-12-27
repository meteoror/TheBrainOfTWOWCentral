import Commands.b_star.interpreter.globals as globals
from Commands.b_star.interpreter.expression import Expression
from Commands.b_star.interpreter.parse import parseCode
from Config._db import Database


def import_func(name):
    # TODO: tag.func import syntax
    # tag_name, func = name.split(".")

    db = Database()
    tag = db.get_entries("bsprograms", columns=["name", "program", "author", "uses", "created", "lastused"], conditions={"name": name})[0]

    if tag is None:
        raise Exception(f"Tag **{name}** not found!")
    else:
        # Add it to the codebase functions
        code = parseCode(tag[1])

        # Run each line (effectively importing it)
        for line in code.children:
            Expression(line, globals.codebase)
