from axioms_2 import expr as ExpBase
from axioms_2 import node
from queue import Queue
import threading
from textwrap import dedent

class LengthError(Exception):
    '''Raised when there the text in the input/output queues are not exactly 1 character long'''
    def __str__(self):
        return 'LengthError: the terminal sent a string with a size other than 1'

class Interpreter:
    def __init__(self):
        self.state = State()

        self.t = threading.Thread(target=self._run)
        self.t.start()

    def _run(self):
        self.state.fg_proc.run()
        print('please dont print me')

"""
Command Line

this file defines the commands which are able to be run on the command line.
new commands are created by creating a new class which inherits Command.
this new class must override the callback function. See commands like _set_expr
for an example.

it is crucial to create at least one instance of the class in this file.
whenever this module is imported into the console.py file, all the subclasses
need to be registered to the Command class. This is done automatically upon
instantiation of the subclass (when super().__init__(...) is called).
"""
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

    """
    TODO describe io_system
    """
    def __init__(self):
        self.expressions = {}
        self.exit_prog = False

        self.istream = Queue()
        self.ostream = Queue()
        self.screen_mode = False # screen mode is used when a process want to take over the entire window.
        self.screen_mode_buff = []

        # process which will be called
        self.fg_proc = cmd_line([], self)

        self.command_history = [] # list of commands which were entered by the user.
        self.command_history_index = 0 # this is the current place in the command history

    def push_cmd(self, cmd:str):
        self.command_history.append(cmd)
        self.command_history_index = len(self.command_history) # processing a command resets the history index to the end

    def put(self, s: str):
        for c in s:
            self.ostream.put(c)

    def get(self):
        c = self.istream.get()

        if len(c) != 1:
            raise LengthError

        self.put(c)

        return c

    def getline(self):
        line = ''
        while True:
            # get and validate a character
            c = self.istream.get()
            if len(c) != 1:
                raise LengthError

            if c in '\n\r':
                break
            elif c == '\x7f':
                if len(line) > 0:
                    line = line[:-1]
                    self.put(c)
            else:
                self.put(c)
                line += c

        return line

class Process:
    """
    All Commands/Processes must derive from this class.
    if the process should be callable from the command line, then it needs to
    be registered using the register function.

    command class names must follow this naming convention: '_somecmd'. the class
    name is used to identify the command the user types

    Whenever a process is called, it tracks the parent process, and sets the state foreground
    process tracker to itself. Once the process is terminated, the foreground process must be restored.
    there are two approaches to this:
        - Non-interactive processes :: everything the process needs to do is done in the __init__() function.
            at the end of the init function, set state.foreground_process to self.parent_process
        - Interactive processes :: initial set-up done in __init__(), then internal state is updated with self.callback()
            at some point within self.callback(), the process should relinquish control back to the parent process.

    Required Static Fields in Subclasses:
        - help_list: list (of tuples)
        - cmdstr: str (or none)

    Override Methods:
        - callback(keyevent: str)


    there are two static fields:
        - commands: a dictionary of all the commands currently registered
        - state: a handle to the current state of the application
    """
    # dict of all defined commands
    commands = {}

    # help_list should be defined in each sub-class
    help_list = [
        ('Description', None),
        ('Input', None),
        ('Output', None),
        ('Effects', None),
        ('Usage', None)
    ]

    cmd_str = None

    def __init__(self, argv: list, state):
        """
        argv: list of arguments which are provided to the application
        state: reference to the state
        stdout: output stream
        """
        self.state = state

        # track parent process
        try:
            self.parent_process = self.state.fg_proc
        except AttributeError:
            self.parent_process = None

        # set self as foreground process
        self.state.fg_proc = self

        # save argv for interactive processes
        self.argv = argv

    def run(self, keyevent:str):
        return "default callback"

    def help(self) -> str:
        # this will grab the help_list defined statically in the subclass. If help_list isn't defined
        # in the subclass, then the help list defined in Process is used.
        help_list = type(self).__class__.help_list

        help_txt = ''
        for (title, content) in help_list:
            if content == None:
                continue

            help_txt += title.upper() + '\n'
            # TODO: automatically insert indents and newlines depending on the width of the terminal screen.
            help_txt += content

        # tell the user if nothing was defined for the command
        if help_txt == '':
            help_txt = 'No documentation has been defined for this command'

        return help_txt

    def register(proc):
        """
        registers this process as a callable command.

        if cmdstr is not defined in the class statically, the class name is used. it uses the class name (without
        the leading underscore) as the name of the class this function requires an instance of the class to
        register (though this instance is not referenced).

        example command registration: 'Process.register(_somecmd)'
        """
        cmd_str = proc.__name__[1:]

        # use registered cmd_string if applicable
        if proc.cmd_str != None:
            cmd_str = proc.cmd_str

        Process.commands[cmd_str] = proc


class cmd_line(Process):
    def run(self):
        intro_text = """
        CALCULATOR RUNTIME ENVIRONMENT
        Written by Ethan Smith and Erik Huuki
        for a list of available commands, type 'help'
        """

        self.state.put(dedent(intro_text))
        self.state.put('\n')

        while True:
            # print prompt
            self.state.put('> ')

            # get user input
            try:
                line = self.state.getline()
            except Exception as e:
                self.state.put(f'Input Error: {str(e)}')
                continue

            try:
                self.state.put('\n')
                self._run_cmd(line)
            except Exception as e:
                self.state.put('ERROR: there was a problem with processing that command\n')
                self.state.put(str(e) + '\n')

    def _run_cmd(self, cmd: str):
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
                self.state.put('Error: malformed command')
            elif arg[0] != '':
                self.state.put('Error: malformed command')
            else:
                argv.insert(0, ':')
                argv[2] = arg[1]
                Process.commands['setexpr'](argv, self.state)
        else:
            self.state.put('"' + argv[0] + '" is not a recognized command or script.')

    def __str__(self):
        return 'cmd_line {\n' +\
        f'    current_line: {self.current_line}\n' +\
        f'    self.return_from_call: {self.return_from_call}\n' +\
        '}'


class _setexpr(Process):
    """This command supports colon syntax. use 'setexpr' when indexing this process in Process.commands"""
    help_list = [
        ('Description', 'binds an expression to an expression object'),
        ('Usage', 'setexpr EXP_NAME EXPRESSION')
    ]

    # argv[0]: : or setexpr
    # argv[1]: expression symbol (ex. 'ans')
    # argv[2]: expression value (ex. 'x+y=2')
    def run(self):
        self.state.fg_proc = self.parent_process

        # handle colon operator syntax
        if argv[0] == ':':
            arg = argv[1].split(':') # separate expression name from the expression (ie. EXP:a+b=c)

            if len(arg) == 1:
                pass
            else:
                argv[1] = arg[0] # add the name of the expression to argument list
                argv.insert(2, arg[1]) # add the first part of the expression to the argument list

        if argv[0] == 'setexpr' and len(argv) <= 1:
            print('Error: not supported', file=self.stdout)
            #self.state.io.print('Error: not supported!')
            return

        if argv[1] == '':
            argv[1] = 'ans'

        exp_str = ''
        for e in argv[2:]:
            exp_str += e

        expression = Exp(exp_str)

        self.state.expressions[argv[1]] = expression

        output = ''
        eval_result = expression.evaluate()
        if eval_result != None:
            output += '    ⍄ ' + str(eval_result) + '\n'

        output += '    ' + argv[1] + ' <- ' +  str(self.state.expressions[argv[1]])
        self.state.put(output)

class _list(Process):
    help_list = [
        ('Description', 'displays currently defined expressions'),
        ('Usage', 'list')
    ]

    def run(self):
        self.state.fg_proc = self.parent_process

        output = ''
        for k,e in self.state.expressions.items():
            output += str(k) + ': ' + str(e) + '\n'

        self.state.put(output)


class _help(Process):
    help_list = [
        ('Description', 'displays help text for a given command'),
        ('Usage', 'help COMMAND\n       help all #to display all commands')
    ]

    # argv[0]: help
    # argv[1]: COMMAND
    def startup(self):
        self.state.fg_proc = self.parent_process

        output = ''
        if len(argv) == 1:
            output = self.commands['help'].help()
        elif argv[1] == 'all':
            for cmd in self.commands:
                output += cmd+'\n'

            output += '\nuse "help COMMAND" to get details on a specific command'
        else:
            if argv[1] in self.commands:
                output += 'help page for "' + argv[1] + '"\n'
                output += self.commands[argv[1]].help()
            else:
                output += 'the command "' + argv[1] + '" is not a valid command'

        # add some indentation for more readability
        output = '    ' + output.replace('\n', '\n    ')

        #self.state.io.println(output)
        self.state.put(output)
        print(output)
        return

class _exit(Process):
    help_list = [
        ('Description', 'displays help text for a given command'),
        ('Usage', 'help COMMAND\n       help all #to display all commands')
    ]

    # argv[0]: exit
    def startup(self):
        self.state.fg_proc = self.parent_process

        self.state.exit_prog = True

class _echo(Process):
    help_list = [
        ('Description', 'print the arguments onto the screen.'),
        ('Usage', 'echo hello world')
    ]

    def startup(self):
        state.fg_proc = self.parent_process

        output = ''
        try:
            for i in argv[1:]:
                output += i + ' '
        except:
            pass

        self.state.put(output)
        return

class _eval(Process):
    help_list = [
        ('Description', 'Evaluates expression (functions, numerica values, etc.)'),
        ('Usage', 'eval EXPRESSION')
    ]

    # argv[0]: eval
    # argv[1]: EXPRESSION
    def startup(self):
        self.state.fg_proc = self.parent_process

        # TODO add the ability to parse an expression or expression reference
        if argv[1] not in self.state.expressions:
            self.state.println('    ERROR: expression "' + argv[1] + '" is not defined.')
            return

        exp = self.state.expressions[argv[1]]

        exp.evaluate_funcs(self.state.expressions)

        # XXX probably don't need to fix the variables twice.
        # fix the variables
        exp.dir.clear()
        exp.map()

        output = ''
        eval_result = exp.evaluate()
        if eval_result != None:
            output += '    ⍄ ' + str(eval_result) + '\n'

        output += '    ' + argv[1] + ' <- ' + str(exp)
        self.state.put(output)

class _table(Process):
    help_lis = [
        ('Description', 'Creates a table of values which can be used for plotting, evaluating, etc.'),
        ('Usage', 'table l w')
    ]

    def startup(self, argv: list, state):
        pass

Process.register(_list)
Process.register(_help)
Process.register(_exit)
Process.register(_echo)
Process.register(_eval)
Process.register(_table)

################################################
class ExpFunctionError(Exception):
    def __init__(self, function, detail):
        message = ': error in ' + function + ' :: ' + detail
        super().__init__(message)


class Exp(ExpBase):
    # these callbacks are static functions within this class.
    #  they could probably be moved into something similar
    #  CLI commands Command class. that would likely be a more
    #  robust solution
    def __init__(self, txt:str=None, root=None):
        # HACK Axioms recognizes arbitrary functions with a single argument.
        # HACK  unfortunately, commas cannot be used as delimeters, as they are
        # HACK  used internally by the tokenizer.
        # HACK
        # HACK The workaround for this is to replace all commas with a 'top-comma'
        # HACK  (ie, grave)
        formatted_txt = None
        if txt != None:
            formatted_txt = txt.replace(',','`')

        super().__init__(txt, root)

    '''
    looks for arbitrary functions in the expression tree.

    if a match is found, it is evaluated, and its result is
    spliced into the tree.
    '''
    def evaluate_funcs(self, root=None, env:dict=None):
        if root == None:
            root = self.root

        if root.val in Exp.funcs:
            # the arguments for the arbitrary function are a list of the parameters (split by comma)
            argv = root.right.val

            expr = Exp.funcs[root.val](argv, env)

            # splice in the root of the new expression at this node.
            root.val = expr.root.val
            root.left = expr.root.left
            root.right = expr.root.right # we can forget about the function arguments

            # the new expression that was spliced in may have arbitrary functions
            # as well. better evaluate_funcs() on them too.
            if root.left != None:
                self.evaluate_funcs(root.left, env)
            if root.right != None:
                self.evaluate_funcs(root.right, env)

        else:
            if root.left != None:
                self.evaluate_funcs(root.left, env)
            if root.right != None:
                self.evaluate_funcs(root.right, env)


    # argv[0]: EXPRESSION (from CLI namespace)
    # argv[1]: VARIABLE (from expression in argv[0])
    def _evaluate_invert(argv:list, env:dict):
        if argv[0] not in env:
            raise ExpFunctionError('invert', 'expression "' + argv[0] + '" does not exist.')

        # NOTE may raise "var not found in Expression" exception
        inverted_exp = env[argv[0]].invert_branch(argv[1]) # is of type ExpBase

        return Exp(root=inverted_exp.root)

    # argv[0]: EXPRESSION (from CLI namespace)
    # argv[1]: VARIABLE (from expression in argv[0])
    def _evaluate_pd(argv:list, env:dict):
        exp = argv[0]
        if exp not in env:
            raise ExpFunctionError('pd', f'expression "{exp}" does not exist.')

        derivative = env[exp].pD(argv[1])

        return Exp(root=derivative.root)

    # these callbacks must be of the form
    #  callback(argv:list, env:dict) -> Exp
    funcs = {
        'invert': _evaluate_invert,
        'pd': _evaluate_pd,
        'dummy': lambda : NotImplemented
    }
