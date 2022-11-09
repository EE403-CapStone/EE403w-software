from axioms_2 import expr as ExpBase
from axioms_2 import node
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

    def callback(self, keyevent:str):
        return "default callback"

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

class _setexpr(Process):
    """This command supports colon syntax. use 'setexpr' when indexing this process in Process.commands"""
    help_list = [
        ('Description', 'binds an expression to an expression object'),
        ('Usage', 'setexpr EXP_NAME EXPRESSION')
    ]

    # argv[0]: : or setexpr
    # argv[1]: expression symbol (ex. 'ans')
    # argv[2]: expression value (ex. 'x+y=2')
    def __init__(self, argv: list, state):
        super().__init__(argv, state)
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
            return('Error: not supported!')

        if argv[1] == '':
            argv[1] = 'ans'

        exp_str = ''
        for e in argv[2:]:
            exp_str += e

        expression = Exp(exp_str)

        Command.state.expressions[argv[1]] = expression

        output = ''
        eval_result = expression.evaluate()
        if eval_result != None:
            output += '    ⍄ ' + str(eval_result) + '\n'

        output += '    ' + argv[1] + ' <- ' +  str(Command.state.expressions[argv[1]])
        return(output)

class _list(Process):
    help_list = [
        ('Description', 'displays currently defined expressions'),
        ('Usage', 'list')
    ]

    def __init__(self, argv: list, state):
        super().__init__(argv, state)
        self.state.fg_proc = self.parent_process

        output = ''
        for k,e in Command.state.expressions.items():
            output += str(k) + ': ' + str(e) + '\n'

        return output

class _help(Process):
    help_list = [
        ('Description', 'displays help text for a given command'),
        ('Usage', 'help COMMAND\n       help all #to display all commands')
    ]

    # argv[0]: help
    # argv[1]: COMMAND
    def __init__(self, argv: list, state):
        super().__init__(argv, state)
        self.state.fg_proc = self.parent_process

        output = ''
        if len(argv) == 1:
            output = Command.commands['help'].help()
        elif argv[1] == 'all':
            for cmd in Command.commands:
                output += cmd+'\n'

            output += '\nuse "help COMMAND" to get details on a specific command'
        else:
            if argv[1] in Command.commands:
                output += 'help page for "' + argv[1] + '"\n'
                output += Command.commands[argv[1]].help()
            else:
                output += 'the command "' + argv[1] + '" is not a valid command'

        # add some indentation for more readability
        output = '    ' + output.replace('\n', '\n    ')

        return output

class _exit(Process):
    help_list = [
        ('Description', 'displays help text for a given command'),
        ('Usage', 'help COMMAND\n       help all #to display all commands')
    ]

    # argv[0]: exit
    def __init__(self, argv: list, state):
        super().__init__(argv, state)
        self.state.fg_proc = self.parent_process

        Command.state.exit_prog = True

class _eval(Process):
    help_list = [
        ('Description', 'Evaluates expression (functions, numerica values, etc.)'),
        ('Usage', 'eval EXPRESSION')
    ]

    # argv[0]: eval
    # argv[1]: EXPRESSION
    def __init__(self, argv: list, state):
        super().__init__(argv, state)
        self.state.fg_proc = self.parent_process

        # TODO add the ability to parse an expression or expression reference
        if argv[1] not in Command.state.expressions:
            return '    ERROR: expression "' + argv[1] + '" is not defined.'

        exp = Command.state.expressions[argv[1]]

        exp.evaluate_funcs(env=Command.state.expressions)

        # XXX probably don't need to fix the variables twice.
        # fix the variables
        exp.dir.clear()
        exp.map()


        output = ''
        eval_result = exp.evaluate()
        if eval_result != None:
            output += '    ⍄ ' + str(eval_result) + '\n'


        output += '    ' + argv[1] + ' <- ' + str(exp)
        return(output)

class _table(Process):
    help_lis = [
        ('Description', 'Creates a table of values which can be used for plotting, evaluating, etc.'),
        ('Usage', 'table l w')
    ]

    def __init__(self, argv: list, state):
        super().__init__(argv, state)

# register predefined commands.
Process.register(_setexpr)
Process.register(_list)
Process.register(_help)
Process.register(_exit)
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
