#!/usr/bin/env python3
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

        self.command_history = [] # list of commands which were entered by the user.
        self.command_history_index = 0 # this is the current place in the command history

        Command.state = self

    def print(self, txt):
        self.output_buffer.append(str(txt))

    def process_cmd(self):
        cmd = self.command_buffer.pop()
        self.command_history.append(cmd)
        self.command_history_index = len(self.command_history) # processing a command resets the history index to the end

        if cmd is None or cmd == '':
            return

        # determine if output should be supressed
        suppress_output = False
        if cmd[-1] == ';':
            suppress_output = True
            cmd = cmd[:-1]

        argv = cmd.split(' ')

        # remove blank tokens from superfluous whitespace
        while argv.count('') != 0:
            argv.remove('')

        # TODO the implied set_expr is not implemented yet.

        output = ''
        # check if this is the colon notation for set_expr
        # argv = [':', 'EXPRESSION_HANDLE', a+b=c]
        if argv[0] in Command.commands:
            output = Command.commands[argv[0]].callback(argv)
        elif argv[0].count(':') == 1:
            argv.insert(0, ':')
            output = Command.commands[argv[0]].callback(argv)
        elif argv[1].count(':') == 1:
            arg = argv[1].split(':')
            if len(arg) > 2:
                output = 'Error: malformed command'
            elif arg[0] != '':
                output = 'Error: malformed command'
            else:
                argv.insert(0, ':')
                argv[2] = arg[1]
                output = Command.commands[argv[0]].callback(argv)
        else:
            output = ('"' + argv[0] + '" is not a recognized command or script.')

        # don't print if there was a semicolon at the end of the input
        if suppress_output:
            return
        else:
            self.print(output)


class KeyEventHandler(QtCore.QObject):
    def __init__(self, window):
        self.window = window
        self.state = window.state
        self.cmd_input = window.cmd_input

        super().__init__(window)

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent):
        UP_ARROW = 16777235
        DOWN_ARROW = 16777237
        if event.type() == QtCore.QEvent.KeyPress:
            key_event = QtGui.QKeyEvent(event)

            # helper variables to make code more readable
            history = self.state.command_history
            index = self.state.command_history_index

            if key_event.key() == UP_ARROW:
                # cover the case when you type something and then want to go back
                #  store the last typed command on the history buffer fist
                if index == len(history) and self.cmd_input.text() != '':
                    self.state.command_history.append(self.cmd_input.text())

                if index > 0:
                    self.state.command_history_index -= 1
                    self.cmd_input.setText(self.state.command_history[self.state.command_history_index])

            elif key_event.key() == DOWN_ARROW:
                if index < len(history) and index != len(history) - 1:
                    self.state.command_history_index += 1
                    self.cmd_input.setText(self.state.command_history[self.state.command_history_index])
                elif index == len(history) - 1:
                    self.state.command_history_index += 1
                    self.cmd_input.clear()

            else:
                return QtCore.QObject.eventFilter(self, obj, event)

            return True
        else:
            # standard event processing
            return QtCore.QObject.eventFilter(self, obj, event)

class MainWindow(QtWidgets.QMainWindow):
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
        self.setCentralWidget(QtWidgets.QWidget()) # central widget needs a placeholder

        self.layout = QtWidgets.QVBoxLayout(self.centralWidget()) # add layout to central widget
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.output_hist, stretch=10)
        self.hlayout.addWidget(self.environment_list)

        self.layout.addLayout(self.hlayout)
        self.layout.addWidget(self.cmd_input)

        # add menu bar
        self._add_menu_bar()

        # connect signals/slots
        self.cmd_input.returnPressed.connect(self.on_enter)

        ev = KeyEventHandler(self)
        self.cmd_input.installEventFilter(ev)

        # load icons
        self.expression_list_icon = QtGui.QIcon()
        self.expression_list_icon.addFile("icons/expression_list_item.png")

    def _add_menu_bar(self):
        self.menuBar().setNativeMenuBar(False)

        file_menu = self.menuBar().addMenu('File')
        graph_menu = self.menuBar().addMenu('Graph')
        funcs_menu = self.menuBar().addMenu('Functions')
        help_menu = self.menuBar().addMenu('Help')

        new_act = QtGui.QAction('New', self)
        file_menu.addAction(new_act)

        for (k,v) in command_line.Exp.funcs.items():
            funcs_menu.addAction(QtGui.QAction(k, self))

        for (k,v) in Command.commands.items():
            action = QtGui.QAction(k, self)

            # XXX WOOO CLOSURES!!!!
            action.triggered.connect((lambda cmd: lambda: self.print(cmd.help()))(v))
            #action.triggered.connect(tmp)

            help_menu.addAction(action)

        self.menuBar().addAction(new_act)

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

    #BUG: output isn't shown immediately, user has to press enter first
    @QtCore.Slot(str)
    def print(self, txt):
        self.state.output_buffer.append(txt)   # record command in output

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

    # load Minecraft font
    fonts = QtGui.QFontDatabase.applicationFontFamilies(0)
    monofont = QtGui.QFont(fonts[0], 14)
    app.setFont(monofont)

    widget = MainWindow()
    widget.resize(800, 600)
    widget.show()

    app.exec()

    sys.exit()
