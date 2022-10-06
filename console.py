#!/usr/bin/env python3
from axioms_2 import exp
import sys
from PySide6 import QtCore, QtWidgets, QtGui
import command_line
from command_line import Command
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

        Command.state = self

    def print(self, txt):
        self.output_buffer.append(str(txt))

    def process_cmd(self):
        cmd = self.command_buffer.pop()

        if cmd is None:
            return

        # determine if output should be supressed
        suppress_output = False
        if cmd[-1] == ';':
            suppress_output = True
            cmd = cmd[:-1]

        # BUG error if there is leading whitespace
        argv = cmd.split(' ')

        # TODO the implied set_expr is not implemented yet.

        # check if this is the colon notation for set_expr
        # BUG if someone enters ':: some_expr' then weird things happen
        # BUG if someone enters 'A:some_expr' it is not recognized as an expression
        if argv[0][-1] == ':':
            # argv = [':', 'EXPRESSION_HANDLE', a+b=c]
            argv.insert(1, argv[0][:-1])
            argv[0] = ':'

        output = ''
        if argv[0] in Command.commands:
            output = Command.commands[argv[0]].callback(argv)
        else:
            output = ('"' + argv[0] + '" is not a recognized command or script.')

        # don't print if there was a semicolon at the end of the input
        if suppress_output:
            return
        else:
            self.print(output)


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
        self.environment_list = QtWidgets.QListWidget()

        # create main layout, QWindow (I think) is its parent
        self.layout = QtWidgets.QVBoxLayout(self)

        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.output_hist, stretch=10)
        self.hlayout.addWidget(self.environment_list)

        self.layout.addLayout(self.hlayout)
        self.layout.addWidget(self.cmd_input)

        # connect signals/slots
        self.cmd_input.returnPressed.connect(self.on_enter)

        # load icons
        self.expression_list_icon = QtGui.QIcon()
        self.expression_list_icon.addFile("icons/expression_list_item.png")


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

        # update the list view
        self.environment_list.clear()

        for e in self.state.expressions:
            label = e + ': ' + str(self.state.expressions[e])

            item = QtWidgets.QListWidgetItem()
            item.setIcon(self.expression_list_icon)
            item.setText(label)

            self.environment_list.addItem(item)


"""
this is the user input loop. It collects and parses user input.
there are certain commands which are supported, and a valid command must be used
for an operation to be valid.

list of valid commands:
    - set_expression Name EXPRESSION
        - Name: Expression (set_expression colon operator)
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

    # TODO make this a list of list of strings, to add all the fonts for each font family
    fonts = ['fira-mono/FiraMono-Regular.otf',
             'OCR A Std Regular/OCR A Std Regular.ttf',
             'Minecraft/Minecraft-Regular.otf'
            ]

    for font in fonts:
        font_dir = QtCore.QDir.currentPath() + '/fonts/' + font
        id = QtGui.QFontDatabase.addApplicationFont(font_dir)
        print(font+':', id)

    # load Minecraft font
    fonts = QtGui.QFontDatabase.applicationFontFamilies(0)
    print(fonts)
    monofont = QtGui.QFont(fonts[0], 14)
    app.setFont(monofont)

    widget = MainWindow()
    widget.resize(800, 600)
    widget.show()

    app.exec()

    sys.exit()
