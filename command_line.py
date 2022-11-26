from axioms_2 import expr as ExpBase
from axioms_2 import node
from queue import Queue
import threading
from textwrap import dedent, indent

class LengthError(Exception):
    '''
    Raised when there the text in the input/output queues are not exactly 1
    character long
    '''
    def __str__(self):
        return 'LengthError: the terminal sent a string with a size other than 1'

class State:
    '''
    provides  attributes and  methods  which  define the  current  state of  the
    runtime environment.  input/output, expressions,  command history,  and many
    other things are stored in this class.

    In order  to start  the application,  an instant of  State must  be created,
    then, fg_proc().run() must  be called. This starts the  first process, which
    is by  default, the  command line. All  Processes send/recieve  their inputs
    through  the  istream/ostream  queues.  This  class  is  thread  safe.  When
    interfacing to a  front end, the user  may encapsulate State in  a new class
    and  override  its put  method  to  signal an  update  to  the display  (for
    example).
    '''
    def __init__(self):
        self.expressions = {}
        self.exit_prog = False

        self.istream = Queue()
        self.ostream = Queue()

        # process which will be called
        self.fg_proc = cmd_line([], self)

        self.command_history = [] # list of commands which were entered by the user.
        self.command_history_index = 0 # this is the current place in the command history

    def push_cmd(self, cmd:str):
        self.command_history.append(cmd)
        self.command_history_index = len(self.command_history) # processing a command resets the history index to the end

    def put(self, s: str):
        '''
        sends a string down the output pipe.

        front-end implementations may want to  override this method to send some
        kind of  signal to update  their display buffer. otherwise,  the ostream
        needs to be polled.
        '''
        # NOTE: this can probably be optimized. it doesn't really need to send
        # strings one character at a time.
        for c in s:
            self.ostream.put(c)

    def putln(self, s: str = None):
        '''like put, but adds a newline to the end.'''
        if s != None:
            for c in s:
                self.ostream.put(c)

        self.ostream.put('\n')

    def get(self):
        '''
        reads  a character  from the  input  \'stream\'. Blocks  until there  is
        something in the queue.
        '''
        c = self.istream.get()

        if len(c) != 1:
            raise LengthError

        return c

    def getline(self):
        '''
        reads a line from the input  \'stream\'. Blocks until there is something
        in the queue.

        this functions performs  the line editing operations that  you would see
        from a tty driver (ie backspace, echoing the character, etc.)
        '''
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
    All Commands/Processes must derive from this class. If the process should be
    callable from  the command line,  then it needs  to be registered  using the
    register function.

    command  class names  must follow  this naming  convention: '_somecmd'.  the
    class  name is  used to  identify the  command the  user types.  Alternative
    spellings for commands  may be defined by setting cmd_str  to something oher
    than none.  Help text is generated  for each command through  the statically
    assigned help_list attribute.  every subclass should redefine  this to suite
    its needs.

    DEPRECATION  WARNING
    Whenever a  process is called,  it tracks the  parent process, and  sets the
    state foreground process tracker to  itself. Once the process is terminated,
    the foreground process  must be restored. This process may  be deprecated in
    the future.  Originally, the  callback function every  time a  character was
    typed, so  this was needed to  track which callback to  call. Now, Processes
    use  blocking input  functions,  so  it no  longer  necessary  to track  the
    callback like this.

    Required Static Fields in Subclasses:
        - help_list: list
        - cmd_str: str (or none)

    Override Methods:
        - run()

    Static Fields:
        - commands: a dictionary of all the commands currently registered
        - help_list: list of tuples of the form (title:str, body:str). Provided
          here for reference.
    """
    # dict of all defined commands
    commands = {}

    # help_list should be re-defined in each sub-class
    help_list = [
        ('Description', None),
        ('Input', None),
        ('Output', None),
        ('Effects', None),
        ('Usage', None)
    ]

    cmd_str = None

    def __init__(self, argv: list, state):
        '''
        argv: list of arguments which are provided to the application
        state: reference to the state
        stdout: output stream
        '''
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

    def run(self):
        return "default callback"

    def help(self) -> str:
        '''
        Uses the  statically defined help_list  (redefined in each  subclass) to
        generate  and format  help  text  for the  command.  If help_list  isn't
        defined in the  subclass, the the default one in  Process is used (where
        everything is none.)
        '''
        help_txt = ''
        for (title, content) in self.help_list:
            if content == None:
                continue

            help_txt += title.upper() + '\n'
            help_txt += indent(dedent(content), '    ') + '\n'

        # tell the user if nothing was defined for the command
        if help_txt == '':
            help_txt = 'No documentation has been defined for this command'

        return help_txt

    def register(proc):
        '''
        registers this process as a callable command.

        if cmdstr  is not  defined in  the class statically,  the class  name is
        used. it  uses the class  name (without  the leading underscore)  as the
        name of  the class this  function requires an  instance of the  class to
        register (though this instance is not referenced).

        example command registration: 'Process.register(_somecmd)'
        '''
        cmd_str = proc.__name__[1:]

        # use registered cmd_string if applicable
        if proc.cmd_str != None:
            cmd_str = proc.cmd_str

        Process.commands[cmd_str] = proc


    def putln(self, s: str):
        '''helper function to reduce typing'''
        self.state.putln(s)
    def put(self, s: str):
        '''helper function to reduce typing'''
        self.state.put(s)
    def get(self):
        '''helper function to reduce typing'''
        return self.state.get()
    def getline(self):
        '''helper function to reduce typing'''
        return self.state.getline()

class cmd_line(Process):
    '''
    This process is akin to bash, zsh, or any other shell in a unix system. It's
    job is  to collect  input, run  programs, and present  their outputs  to the
    user.
    '''
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
                self.state.putln()
                self._run_cmd(line)
            except Exception as e:
                self.state.putln('ERROR: there was a problem processing that command')
                self.state.putln(str(e) + ', ' + str(type(e)))

    def _run_cmd(self, cmd: str):
        '''helper function which reduces special syntax'''
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

        # see if the command is registered
        if argv[0] in Process.commands:
            # command isn't using ':' notation
            Process.commands[argv[0]](argv, self.state).run()
            return

        # Command could be in colon notation
        # Proper colon notation:
        #  F: a+b=c
        #  F :a+b=c
        #  F : a+b=c
        #  F:a+b=c
        # Improper colon notation (error):
        #  F:
        #  F:: a+b=c
        #  F :: a+b=c
        #  F ::a+b=c
        #  F::a+b=c
        #
        # essentially, as long as there is only one colon in the command, then
        # the format is valid.
        colon_fmt = cmd.split(':')
        if len(colon_fmt) == 2:
            argv = ['setexpr', colon_fmt[0], colon_fmt[1]]
            Process.commands[argv[0]](argv, self.state).run()
            return

        self.putln(f'command not found: "{argv[0]}"')
        return

    def __str__(self):
        return 'cmd_line {\n' +\
        f'    current_line: {self.current_line}\n' +\
        f'    self.return_from_call: {self.return_from_call}\n' +\
        '}'


class _setexpr(Process):
    """
    This command supports colon syntax. use 'setexpr' when indexing this process
    in Process.commands
    """
    help_list = [
        ('Description', 'binds an expression to an expression object'),
        ('Usage', 'setexpr EXP_NAME EXPRESSION')
    ]

    # argv[0]: : or setexpr
    # argv[1]: expression symbol (ex. 'ans')
    # argv[2]: expression value (ex. 'x+y=2')
    def run(self):
        self.state.fg_proc = self.parent_process
        argv = self.argv

        # argv must be at least three to be functional (if its just one, print
        # the help text)
        # ['setexpr', 'name', 'expression', ...]
        if len(argv) == 1:
            self.putln(self.help())
        elif len(argv) < 3:
            self.putln('argument error: expected at least 2, got 1')
            return

        # remove any leading/trailing whitespace
        argv[1] = argv[1].strip()

        forbidden_chars = '+=*&^%$#@!~`\|(){}[];:\'"/?.>,<`'
        for c in argv[1]:
            if c in forbidden_chars:
                self.putln(f'invalid character errror: "{c}"')
                return

        if argv[1] == '':
            argv[1] = 'ans'

        exp_str = ''
        for e in argv[2:]:
            exp_str += e

        try:
            expression = Exp(exp_str)
        except Exception as e:
            self.putln(f'expression format error: {e}')
            return

        self.state.expressions[argv[1]] = expression

        eval_result = expression.evaluate()
        if eval_result != None:
            self.putln(f'    ⍄ {str(eval_result)}')

        self.putln(f'    {argv[1]} <- {str(self.state.expressions[argv[1]])}')

class _list(Process):
    '''lists all the expressions which are currently defined.'''
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
    '''provides access to the robust help features of this application.'''
    help_list = [
        ('Description', 'displays help text for a given command'),
        ('Usage', \
        '''\
        help COMMAND   # to see help on a specific command
        help all       # to see all available commands
        ''')
    ]

    # argv[0]: help
    # argv[1]: COMMAND
    def run(self):
        argv = self.argv
        self.state.fg_proc = self.parent_process

        output = ''
        if len(argv) == 1:
            self.putln(self.commands['help']([], self.state).help())
        elif argv[1] == 'all':
            for cmd in self.commands:
                self.state.putln(cmd)

            self.state.putln('\nuse "help COMMAND" to get details on a specific command')
        else:
            if argv[1] in self.commands:
                self.putln(self.commands[argv[1]]([], self.state).help())
            else:
                self.putln(f'the command "{argv[1]}" is not a valid command')

        return

class _exit(Process):
    '''supposedly exits the application.'''
    # argv[0]: exit
    def run(self):
        self.state.fg_proc = self.parent_process

        self.state.exit_prog = True

class _echo(Process):
    '''prints its arguments to the screen'''
    help_list = [
        ('Description', 'print the arguments onto the screen.'),
        ('Usage', 'echo hello world')
    ]

    def run(self):
        argv = self.argv
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
    '''evaluates the given expression'''
    help_list = [
        ('Description', 'Evaluates expression (functions, numerica values, etc.)'),
        ('Usage', 'eval EXPRESSION')
    ]

    # argv[0]: eval
    # argv[1]: EXPRESSION
    def run(self):
        argv = self.argv
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

    def run(self, argv: list, state):
        pass

Process.register(_setexpr)
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
