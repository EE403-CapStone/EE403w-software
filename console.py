#!/usr/bin/env python3
import sys
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import *
import command_line
from command_line import Process
"""
returns the arguments of cmd_string
"""
def trim_command(cmd_string):
    if not ' ' in cmd_string:
        return '' # there is only one token in this string

    n = cmd_string.find(' ')
    return cmd_string[n+1:]

class IOAbstraction:
    def __init__(self):
        # TODO change from lists to dequeues (for efficiency)
        self.input_buffer = []
        self.output_buffer = []

        self.flush_func = None

    def print(self, txt: str):
        self.output_buffer += [c for c in txt]

    def println(self, txt: str):
        self.output_buffer += [c for c in txt]
        self.output_buffer.append('\n')

    def flush(self):
        if self.flush_func == None:
            raise NotImplementedError

        self.flush_func(self.output_buffer)
        self.output_buffer.clear()

    def set_flush(self, flush_func):
        # TODO do some tests to make sure that flush_func is the correct type
        self.flush_func = flush_func


class cmd_line(Process):
    def __init__(self, argv: list, state):
        """
        argv[0]: cmd_line
        argv[1]: 's' for silent or 'v' for verbose
        argv[2]: initial command
        """
        super().__init__(argv, state)

        self.current_line = ''
        self.return_from_call = True

    def callback(self, keyevent: str):
        # print prompt if necessary
        if self.return_from_call:
            self.state.io.print("> ")
            self.state.io.flush()
            self.return_from_call = False

        if keyevent == '\r':
            self.state.io.println('')
            try:
                self._run_cmd()
            except Exception as e:
                self.state.io.println('ERROR: there was a problem with processing that command')
                self.state.io.println(str(e))

            self.return_from_call = True
            self.current_line = ''
        else:
            self.current_line += keyevent

        self.state.io.print(keyevent)
        self.state.io.flush()

    def _run_cmd(self):
        cmd = self.current_line

        # case where use just pressed enter
        if cmd == '':
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
        # TODO implement supressed output

        # BUG 'F::a+b=c' generates an error

        # check if this is the colon notation for set_expr
        # argv = [':', 'EXPRESSION_HANDLE', a+b=c]
        if argv[0] in Process.commands:
            # command isn't using ':' notation
            Process.commands[argv[0]](argv, self.state)

        # these cases may be ':' notation of setexpr
        elif argv[0].count(':') == 1:
            argv.insert(0, ':')
            Process.commands['setexpr'](argv, self.state)
        elif argv[1].count(':') == 1:
            arg = argv[1].split(':')
            if len(arg) > 2:
                self.state.io.println('Error: malformed command')
            elif arg[0] != '':
                self.state.io.println('Error: malformed command')
            else:
                argv.insert(0, ':')
                argv[2] = arg[1]
                Process.commands['setexpr'](argv, self.state)
        else:
            self.state.io.println('"' + argv[0] + '" is not a recognized command or script.')


    def __str__(self):
        return 'cmd_line {\n' +\
        f'    current_line: {self.current_line}\n' +\
        f'    self.return_from_call: {self.return_from_call}\n' +\
        '}'


class State:
    """
    The State class contains the current state of the application.
    it provides methods which can be used to modify the state, or be bound
    to commands which are then typed by the user.

    this design pattern allows the interface type to be easily interchangable (ie, output
    using curses to terminal, create a custom window with a graphcis library such as WebGPU
    or OpenGL and draw to a pixel buffer)

    The state class takes a pointer to a print function. whenever state.print(txt) is called,
    the state updates the internal output buffer, then calls the external print function. the
    external print function do whatever it needs to display the current state of the output buffer.
    """
    outputChanged = QtCore.Signal(str)

    """
    TODO describe io_system
    """
    def __init__(self, io_system):
        self.expressions = {}
        self.exit_prog = False

        self.io = io_system
        self.screen_mode = False # screen mode is used when a process want to take over the entire window.
        self.screen_mode_buff = []

        # HACK this probably shouldn't be done like this.
        Process.state = self

        # process which will be called
        self.fg_proc = cmd_line([], self)

        self.command_history = [] # list of commands which were entered by the user.
        self.command_history_index = 0 # this is the current place in the command history

    def push_cmd(self, cmd:str):
        self.command_history.append(cmd)
        self.command_history_index = len(self.command_history) # processing a command resets the history index to the end

    def process_cmd(self, cmd: str):
        self.command_history.append(cmd)
        self.command_history_index = len(self.command_history) # processing a command resets the history index to the end

        if cmd is None or cmd == '':
            return (cmd_line, [])

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

        # BUG 'F::a+b=c' generates an error
        output = ''
        # check if this is the colon notation for set_expr
        # argv = [':', 'EXPRESSION_HANDLE', a+b=c]
        if argv[0] in Process.commands:
            return (Process.commands[argv[0]], argv)
        elif argv[0].count(':') == 1:
            argv.insert(0, ':')
            return (Process.commands[argv[0]], argv)
        elif argv[1].count(':') == 1:
            arg = argv[1].split(':')
            if len(arg) > 2:
                output = 'Error: malformed command'
            elif arg[0] != '':
                output = 'Error: malformed command'
            else:
                argv.insert(0, ':')
                argv[2] = arg[1]
                return (Process.commands[argv[0]], argv)
        else:
            output = ('"' + argv[0] + '" is not a recognized command or script.')

        # don't print if there was a semicolon at the end of the input
        if suppress_output:
            return (cmd_line, [])
        else:
            self.io.println('')
            self.io.println(output)
            return (cmd_line, [])


class KeyEventHandler(QtCore.QObject):
    def __init__(self, window, io_system):
        self.window = window
        self.state = window.state
        self.output_hist = window.output_hist

        self.io_system = io_system
        self.io_system.set_flush(self.print_buff)

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
                self.state.fg_proc.callback(key_event.text())

            return True
        else:
            # standard event processing
            return QtCore.QObject.eventFilter(self, obj, event)

    def print_buff(self, buff: list):
        for t in buff:
            self.output_hist.insertPlainText(t)

    def get_io_system(self) -> IOAbstraction:
        return self.io_system

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        io_system = IOAbstraction()
        self.state = State(io_system)

        self.output_hist = QtWidgets.QTextEdit('')

        """CALCULATOR RUNTIME ENVIRONMENT
        Written by Ethan Smith and Erik Huuki
        for a list of available commands, type 'help'
        """
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

        ev = KeyEventHandler(self, io_system)
        self.output_hist.installEventFilter(ev)

        # load icons
        self.expression_list_icon = QtGui.QIcon()
        self.expression_list_icon.addFile("icons/expression_list_item.png")

        self.state.fg_proc.callback('')

    def _add_menu_bar(self):
        self.menuBar().setNativeMenuBar(False)
        # TODO add edit/application menu item to allow changing fonts etc.
        file_menu = self.menuBar().addMenu('File')
        graph_menu = self.menuBar().addMenu('Graph')
        funcs_menu = self.menuBar().addMenu('Functions')
        help_menu = self.menuBar().addMenu('Help')

        new_act = QtGui.QAction('New', self)
        file_menu.addAction(new_act)

        for (k,v) in command_line.Exp.funcs.items():
            funcs_menu.addAction(QtGui.QAction(k, self))

        for (k,v) in Process.commands.items():
            action = QtGui.QAction(k, self)

            # XXX WOOO CLOSURES!!!!
            action.triggered.connect((lambda cmd: lambda: self.print(cmd.help()))(v))

            help_menu.addAction(action)

        self.menuBar().addAction(new_act)


    """
    @QtCore.Slot()
    def on_enter(self):
        self.state.output_buffer.append(self.cmd_input.text())   # record command in output

        cmd = self.cmd_input.text()
        self.state.process_cmd(cmd)
        self.cmd_input.clear()

        for t in self.state.output_buffer:
            self.output_hist.append(t)

        # update the list view
        self.environment_list.clear()

        for e in self.state.expressions:
            label = e + ': ' + str(self.state.expressions[e])

            item = QtWidgets.QListWidgetItem()
            item.setIcon(self.expression_list_icon)
            item.setText(label)

            self.environment_list.addItem(item)

    #BUG: output isn't shown immediately, user has to press enter first
    """

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
