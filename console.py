#!/usr/bin/env python3
from axioms_2 import exp


"""
The State class contains the current state of the application.
it provides methods which can be used to modify the state, or be bound
to commands which are then typed by the user.

this design pattern has the benefit which allows the type of interface
used easily interchangable (ie, output using curses to terminal, create a custom window
with a graphcis library such as WebGPU or OpenGL and draw to a pixel buffer)
"""
class State:
    def __init__(self):
        self.expressions = []
        self.exit_prog = False

    # TODO this doesn't parse the expression, and includes the command keyword in cmd
    def set_expr(self, cmd):
        self.expressions.append(exp(cmd))

    def exit_prog(self, cmd):
        self.exit_prog = True

    def list_exprs(self, cmd):
        print(self.expressions)




"""
this is the user input loop. It collects and parses user input.
there are certain commands which are supported, and a valid command must be used
for an operation to be valid.

list of valid commands:
    - set_expr EXPRESSION
    - load FILE
    - eval EXPRESSION
    - clear
    - del EXPRESSION
    - help

for convenience, there is an implicit set_expr command. If the first token isn't
a valid command, then it is assumed that the user input are paremeters for set_expr
"""
state = State()
while True:
    cmd_string = input('>> ')

    tokens = cmd_string.split(' ')

    # these are the bindings between the state modifier functions and the
    # commands that the user can actually type
    #
    # Commands are standardized in that they only take the command line string.
    # each function is responsible for parsing the input itself.
    #
    # TODO the implied set_expr is not implemented yet.
    # TODO create a new commmand class which includes documentation for each command
    commands = {
        "exit": State.exit_prog,
        "set_expr": State.set_expr,
        "list": State.list_exprs,
        "help": lambda state, cmd : print(list(commands.keys()))
    }

    # after the command is evaluated, then any changes in state are reflected
    # in the user interface.
    if tokens[0] in commands:
        commands[tokens[0]](state, cmd_string)

    if state.exit_prog == True:
        break
