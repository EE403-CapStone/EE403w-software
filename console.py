#!/usr/bin/env python3
import sys
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import *
import command_line
from command_line import Process
import io
from queue import Queue, Empty
import threading

class Interpreter(QObject):
    '''
    Wrapper/Interface  between   calculator  runtime  application  and   the  Qt
    environment.  Emits a  signal whenever  there is  output which  needs to  be
    displayed to the  screen. a slot in  the terminal is then  connected to this
    signal prints text from the ostream to its internal buffer.

    It derives  from QObject  so that  it can  be integrated  into the  Qt Event
    system
    '''

    class State(command_line.State):
        '''wrapper class to extend functionality of put method'''
        def __init__(self, interp):
            super().__init__()
            self.interp = interp
        def put(self, s: str):
            super().put(s)
            self.interp.recv_txt.emit()

    recv_txt = QtCore.Signal()
    def __init__(self):
        super().__init__()

        self.state = Interpreter.State(self)

        self.t = threading.Thread(target=self._run)
        self.t.start()

    def _run(self):
        '''target for thread object'''
        self.state.fg_proc.run()

    def flush(self):
        '''tells anything looking for text in ostream to check the queue.'''
        self.recv_txt.emit()


class KeyEventHandler(QtCore.QObject):
    '''
    DEPRECATION WARNING
    this code  is pretty much  entirely deprecated. it  is only here  because it
    contains functionality which needs to be ported over to the Terminal class
    '''
    def __init__(self, window):
        self.window = window
        self.state = window.interpreter.state
        self.output_hist = window.output_hist

        self.output_buffer = []

        super().__init__(window)

    # BUG backspace doesn't work.
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
                # BUG we got rid of the cmd_input!!!
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
        if event.type() == QtCore.QEvent.CursorChange:
            pass
        else:
            # standard event processing
            return QtCore.QObject.eventFilter(self, obj, event)

    def print_buff(self, buff: list):
        for t in buff:
            self.output_buffer.append(t)

        output = ''
        for t in self.output_buffer:
            output += t

        self.output_hist.setText(output)


class Terminal(QtWidgets.QScrollArea):
    '''
    "Dumb" terminal. It does dumb terminal things, like send/recieve characters,
    and print the characters it revieves to the screen.

    soon it will support even more dumb terminal things, like a cursor.
    '''
    def __init__(self, parent, istream: Queue, ostream: Queue):
        super().__init__(parent)
        self.setWidgetResizable(True)

        self.text = QLabel(self)

        self.text.setWordWrap(True)
        self.text.setScaledContents(False)
        self.text.setContentsMargins(0,0,0,0)
        self.text.setFrameStyle(QtWidgets.QFrame.Box)
        self.text.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.text.setText('hello there\ngeneral kenobi')
        self.text.setAlignment(QtCore.Qt.AlignTop)

        super().setWidget(self.text)

        self.istream = istream
        self.ostream = ostream

    def setText(self, text):
        self.text.setText(text)

    def keyPressEvent(self, event):
        UP_ARROW = 16777235
        DOWN_ARROW = 16777237
        key_event = QtGui.QKeyEvent(event)

        if key_event.key() == UP_ARROW:
            pass
        elif key_event.key() == DOWN_ARROW:
            pass
        elif len(key_event.text()) != 0:
            self.istream.put(key_event.text())

        return True

        if event.type() == QtCore.QEvent.CursorChange:
            pass
        else:
            # standard event processing
            return QtCore.QObject.eventFilter(self, obj, event)

    def append(self, c:str):
        txt = self.text.text() + c
        self.text.setText(txt)

    def recv_text(self):
        txt = self.text.text()
        while True:
            try:
                c = self.ostream.get_nowait()
                if len(c) != 1:
                    raise command_line.LengthError

                if c == '\x7f':
                    txt = txt[:-1]
                else:
                    txt += c

            except Empty:
                break

        self.text.setText(txt)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.interpreter = Interpreter()

        istream = self.interpreter.state.istream
        ostream = self.interpreter.state.ostream
        self.output_hist = Terminal(self, istream, ostream)

        #self.output_hist.setReadOnly(True)

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

        #ev = KeyEventHandler(self)
        #self.output_hist.installEventFilter(ev)
        self.interpreter.recv_txt.connect(self.output_hist.recv_text)
        self.interpreter.flush()

        # load icons
        self.expression_list_icon = QtGui.QIcon()
        self.expression_list_icon.addFile("icons/expression_list_item.png")

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
