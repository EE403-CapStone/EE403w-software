from axioms_2 import exp,node


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
    
