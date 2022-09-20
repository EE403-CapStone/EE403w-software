#!/usr/bin/env python3
from axioms_2 import exp
import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
"""
returns the arguments of cmd_string
"""
def trim_command(cmd_string):
    if not ' ' in cmd_string:
        return '' # there is only one token in this string

    n = cmd_string.find(' ')
    return cmd_string[n+1:]



"""
The State class contains the current state of the application.
it provides methods which can be used to modify the state, or be bound
to commands which are then typed by the user.

this design pattern allows the interface type to be easily interchangable (ie, output
using curses to terminal, create a custom window with a graphcis library such as WebGPU
or OpenGL and draw to a pixel buffer)
"""
class State:
    def __init__(self):
        self.expressions = {}
        self.exit_prog = False
        self.command_buffer = [] # commands which need to be processed
        self.output_buffer = [] # lines which need to be printed to the screen

    # TODO this doesn't parse the expression, and includes the command keyword in cmd
    def set_expr(self, cmd):
        n = trim_command(cmd)
        self.expressions['ans'] = exp(n)
        self.print('ans: ' +  str(self.expressions['ans']))

    def exit_prog(self, cmd):
        self.exit_prog = True

    def list_exprs(self, cmd):
        for k,e in self.expressions.items():
            self.print(str(k) + ': ' + str(e))

    def print(self, txt):
        self.output_buffer.append(str(txt))

    def process_cmd(self):
        cmd = self.command_buffer.pop()

        if cmd is None:
            return

        tokens = cmd.split(' ')

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
            "help": lambda state, cmd : self.print(list(commands.keys()))
        }

        # after the command is evaluated any changes in state are reflected
        # in the user interface.
        if tokens[0] in commands:
            commands[tokens[0]](self, cmd)
        else:
            self.print('"' + tokens[0] + '" is not a recognized command or script.')



class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.state = State()

        self.command_buffer = [] # list of commands which still need to be processed

        # history output. FIXME text is vertically aligned at top of frame
        # TODO add label widget next to line entry widget
        self.output_hist = QtWidgets.QTextEdit('')
        self.output_hist.setText(
"""CALCULATOR RUNTIME ENVIRONMENT
Written by Ethan Smith and Erik Huuki
for a list of available commands, type 'help'
"""
        )
        self.output_hist.setReadOnly(True)

        self.cmd_input = QtWidgets.QLineEdit()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.output_hist)
        self.layout.addWidget(self.cmd_input)

        self.cmd_input.returnPressed.connect(self.on_enter)

    @QtCore.Slot()
    def on_enter(self):
        self.state.command_buffer.append(self.cmd_input.text())  # put command in line to be processed
        self.state.output_buffer.append(self.cmd_input.text())   # record command in output
        self.cmd_input.clear()

        self.state.process_cmd()

        for t in self.state.output_buffer:
            self.output_hist.append(t)

        self.state.output_buffer.clear()
        self.state.output_buffer.append('') # add a blank line for formatting



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
if __name__ == "__main__":
    #setup QT6 context
    app = QtWidgets.QApplication([])

    widget = MainWindow()
    widget.resize(800, 600)
    widget.show()

    app.exec()

    sys.exit()
