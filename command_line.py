from axioms_2 import exp,node

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

"""
New commands must derive from this class.

there are two static fields:
    - commands: a dictionary of all the commands currently registered
    - state: a handle to the current state of the application
"""
class Command:
    # all of the defined commands
    commands = {}

    # handle to application state.
    # THIS MUST BE SET
    state = None

    def __init__(self, cmd_str:str, help_str:str, callback=None):
        self.cmd_str = cmd_str
        self.help_str = help_str
        self.callback = callback
        Command.commands[cmd_str] = self

    def help(self) -> str:
        return self.help_str

    def callback(argv: list) -> str:
        return "default callback"


class _set_expr(Command):
    def __init__(self):
        cmd_str = "setexpr"
        help_str = "help page for setexpr.\nDescription: binds an expression to an expression object\nUsage: setexpr EXP_NAME EXPRESSION"

        super().__init__(cmd_str, help_str, _set_expr.callback)

        # TODO add specific help instructions for this syntax
        super().__init__(":", help_str, _set_expr.callback) # also initialize an instance for colon operator

    # argv[0]: : or setexpr
    # argv[1]: expression symbol (ex. 'ans')
    # argv[2]: expression value (ex. 'x+y=2')
    def callback(argv:list):
        # BUG argv[1] may not exist
        if argv[1] == '':
            argv[1] = 'ans'

        # TODO you need to mirror axioms code here to parse and interpret
        #  functions such as invert.
        expression = exp(argv[2])
        Command.state.expressions[argv[1]] = expression

        return('    ' + argv[1] + ' <- ' +  str(Command.state.expressions[argv[1]]))

class _list_expr(Command):
    def __init__(self):
        cmd_str = "list"
        help_str = "help page for list.\nDescription: displays currently defined expressions\nUsage: list"

        super().__init__(cmd_str, help_str, _list_expr.callback)

    def callback(argv:list):
        output = ''
        for k,e in Command.state.expressions.items():
            output += str(k) + ': ' + str(e) + '\n'

        return output

class _help(Command):
    def __init__(self):
        cmd_str = "help"
        help_str = "help page for help.\nDescripton: displays help text for a given command\nUsage: help COMMAND\n       help all #to display all commands"

        super().__init__(cmd_str, help_str, _help.callback)

    # argv[0]: help
    # argv[1]: COMMAND
    def callback(argv:list):
        print('cmd_line.py', argv)
        output = ''
        if len(argv) == 1:
            output = Command.commands['help'].help()
        elif argv[1] == 'all':
            for cmd in Command.commands:
                output += cmd+'\n'

            output += '\nuse "help COMMAND" to get details on a specific command'
        else:
            if argv[1] in Command.commands:
                output += Command.commands[argv[1]].help()
            else:
                output += 'the command "' + argv[1] + '" is not a valid command'

        return output

class _exit(Command):
    def __init__(self):
        cmd_str = "exit"
        help_str = "help page for exit.\nDescripton: exits calculator program\nUsage: exit"

        super().__init__(cmd_str, help_str, _exit.callback)

    # argv[0]: exit
    def callback(argv:list):
        Command.state.exit_prog = True
            
# register predefined commands.
_set_expr()
_list_expr()
_help()
_exit()

################################################
# TODO integrate Erik's code into setexpr
def isvalid(s):
    # Statements that check if statements are able to be processed
    return True


# Can be more complex, for now only considering s of the form F(var=val)
def function_form(s):
    if s.count('(')!=1 or s.count(')')!=1:
        return False
    return True

def _str2values(s:str)->any:
    # Given str inputs recognizes bool int float and complex values
    # recognizes reserved values such as 'pi'
    if s=='True':
        return True
    elif s=='False':
        return False
    elif s=='pi':
        return 3.14159265358979323846
    elif s == 'e':
        return 2.718281828459045
    
    ## Need to make a list of reserved strings ##

    # recognize if the string is a valid number return an error if not
    iscomplex = s[-1]=='j' and s != 'j'
    s = s[:-1] if iscomplex else s

    # Handling integer values
    if s.isdigit():
        r = int(s)*1j if iscomplex else int(s)
        return r
    
    # Handling floats
    if s.count('.')==1:
        z,decimal = s.split('.')
        if not z.isdigit() or not decimal.isdigit():
            raise Exception(f'{s} is not a valid number or variable')

        r = r*1j if iscomplex else r
        return r

    elif s.count('.')>1:
        raise Exception(f'{s} is not a valid number or variable')
    

    if s[0].isdigit():
        raise Exception(f'variable {s} cannot start with a number or is an incorrectly formatted number')
    
    # When s cannot be converted into some number and is correctly formatted as a variable
    # pass it back as a string
    s = s+'j' if iscomplex else s
    return s


exp_dir = {}

if __name__ == "__main__":
    # Command line interface loop
    while True:
        s = input('> ')

        if s=='':
            continue
        if not isvalid(s): # Check validity of statements according to our spec
            print('Invalid Statement')
            continue

        output = (s[-1]!=';')
        output_string = ''
        s = s[:-1] if not output else s

        if s=='clear':
            exp_dir = {}

        if s=='list exps':
            output_string = '\n'.join([str(e) for e in exp_dir.values()])

        if ':' in s:
            l = s.split(':')

            exp_dir[l[0]] = exp(l[1])
            output_string = exp_dir[l[0]]
        else:
            exp_dir['ans']=exp(l[0])
            output_string = str(exp_dir['ans'])

        if function_form(s):    # When of the form exp(var=val) evaluate
            tokens = s.split('(')
            e = tokens[0]

            var_args = tokens[1][:-1]
            var_args = var_args.split(',')
            val_dict = {}

            for arg in var_args:
                key,val = arg.split('=')
                val_dict[key] = _str2values(val)    # Assuming val can be converted to a raw val

            output_string = str(exp_dir[e].evaluate(val_dict=val_dict))
            exp_dir['ans'] = exp(root=node(exp_dir[e].evaluate(val_dict=val_dict)))

        if s=='break': # For debugging purposes
            break

        if output:
            print(output_string)
