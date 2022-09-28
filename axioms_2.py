# Author: Erik Huuki
# The backend software of EE403 capstone Design project
# Description:
# Axioms_2 is a symbolic math library that converts mathematical statements binary trees
# This is for the purposes of automating symbolic math operations that 
# undergraduates frequently do


from ast import operator
import doctest
import numpy as np

class exp:
    def __init__(self,exp:str=None,root=None,**kwargs):
        # str expressions and roots of trees to define expression objects
        self.root = root

        if isinstance(exp,str):
            self.root = self.exp2tree(exp)
        
        if 'root' in kwargs:
            self.root = self.exp2tree(kwargs['roots'])
        
        if 'exp' in kwargs:
            self.root = self.exp2tree(kwargs['exp'])
        self.dir = {}
        self.map()

    def exp2tree(self,exp,latex = False):
        # Converts the raw string into a tree
        # ex. list2tree('a+b')=> node(val='+', left=node('a'), right=node('b'))
        

        # check for mismatched delimiters
        if exp.count('(')!= exp.count(')'):
            raise Exception('Mismatched delimiters')
        
        exp = exp.replace(' ','')       # Remove blank space

        # Need to check for incomplete expressions / errors in expressions

        # tokenizes the string expression into a list
        exp_list = _tokenize(exp)
        exp_list = [self._str2values(val) for val in exp_list]
        root = self.list2tree(exp_list)
        return root

    def _str2values(self,s:str)->any:
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

    def list2tree(self,op_list:list):
        # Converts a tokenized expression to a tree
        # list2tree(['a','+','b'])=> node(val='+', left=node('a'), right=node('b'))
        # Handles parhentesis

        while '(' in op_list:           # compresses parhentesis protected expressions
            op_list = self.compress_parhentesis(op_list)

        if len(op_list)==1:
            if type(op_list[0])in [str,bool, int, float, complex]:
                return node(op_list[0])

            elif type(op_list[0])==list:
                return self.list2tree(op_list[0])
        
        if op_list[0]=='-':            # case of -x
            op_list[:2] = [-1,'*',op_list[1]]
            
        next_operator = self.next_operator(op_list)
        single_operators = ['cos','sin','tan','sec','csc','cot','asin','acos','atan','!']
        
        if op_list[next_operator] in single_operators:
            return node(op_list[next_operator],right = self.list2tree(op_list[next_operator+1:]))

        val = op_list[next_operator]
        left = self.list2tree(op_list[:next_operator])
        right = self.list2tree(op_list[next_operator+1:])

        return node(val,left,right)
    
    def next_operator(self,exp_list):
        # Returns the index of the macro operation
        # 'macro operation': if left and right components of the operation are grouped by parhentesis 
        # it wouldn't change the expression. 'a $ b' = '(a) $ (b)', where a and b are 
        # expressions and '$' is an operator
        # ex. 
        # next_operator('a+b*c') => 1
        # a+b*c = (a)+(b*c)

        operator = [
            '=',
            '|',
            '&',
            '!',
            '+',
            '-',
            '%',
            '*',
            '/',
            '^',
            '==',
            '<',
            '<=',
            '>',
            '>=',
            'cos',
            'sin',
            'tan',
            'sec',
            'csc',
            'cot',
            'asin',
            'acos',
            'atan'] # disregarding ['<'...] operators for now

        for op in operator:
            if op in exp_list:
                return exp_list.index(op)

    def compress_parhentesis(self,exp_list):

        p1 = exp_list.index('(')   # left outermost parhentesis
        depth = 1
        for i,c in enumerate(exp_list[p1+1:]):
            if c=='(':
                depth+=1
            elif c==')':
                depth-=1
            
            if depth==0:
                break
        
        p2 = p1+i+1

        exp_list[p1:p2+1] = [[exp_list[p1+1:p2]]]
        return exp_list

    def evaluate(self,root=None):
        # Evaluates an expression tree
        # If all the end nodes are operatable expressions returns value
        # Else returns None
        # Assumes the expression to be valid ie. For expressions with logical statements or equivalencies
        # it is assumed the expressions are valid
        if root==None:
            root =self.root
        # For when the root val type is in a value set return the raw value
        if type(root.val) in [bool,int,float,float,complex]:
            return root.val

        operator = {    # Operators with 2 inputs
            '+':lambda a,b: a+b,
            '-':lambda a,b: a-b,
            '/':lambda a,b: a/b,
            '*':lambda a,b: a*b,
            '^':lambda a,b: a**b,
            '&':lambda a,b: a&b,
            '|':lambda a,b: a|b,
            '%':lambda a,b: a%b,
            '>':lambda a,b:a>b,
            '<':lambda a,b:a<b,
            '>=':lambda a,b:a>=b,   # need to recognize these operators within text
            '<=':lambda a,b:a<=b,
            '=':lambda a,b: a if a!=None else b 
        }

        single_operators={          # operators with single inputs
            '!':lambda a:not a,
            'cos':lambda a: np.cos(a),
            'sin':lambda a: np.sin(a),
            'tan':lambda a: np.tan(a),
            'sec':lambda a: np.sec(a),
            'csc': lambda a: np.csc(a),
            'asin': lambda a: np.asin(a),
            'acos': lambda a: np.acos(a),
            'atan':lambda a : np.atan(a)
        }

        # Operators with both left or right parts
        if root.val=='=' and None not in[left,right] and left!=right:
            raise Exception(f'Invalid Expression\nLeft and right sides are not equal\n{self._str_aux(root.left)} !=  {self._str_aux(root.right)}')
        
        
        right = self.evaluate(root.right)

        if root.val in single_operators:
            return single_operators[root.val](right)
        elif root.val in operator:
            left = self.evaluate(root.left)
            return operator[root.val](left,right)

    def display(self,root=None):
        # Purely for debugging purposes
        if root==None:
            root = self.root
        lines, *_ = self._display_aux(root)
        for line in lines:
            print(line)

    def _display_aux(self,base=None):
        # For debugging purposes
        if base == None:
            base = self.root
        
        if base.right== None and base.left==None:
            line = '%s' % base.val
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Only left child.
        if base.right == None:
            lines, n, p, x = self._display_aux(base.left)
            s = '%s' % base.val
            u = len(s)
            first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s
            second_line = x * ' ' + '/' + (n - x - 1 + u) * ' '
            shifted_lines = [line + u * ' ' for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

        # Only right child.
        if base.left == None:
            lines, n, p, x = self._display_aux(base.right)
            s = '%s' % base.right
            u = len(s)
            first_line = s + x * '_' + (n - x) * ' '
            second_line = (u + x) * ' ' + '\\' + (n - x - 1) * ' '
            shifted_lines = [u * ' ' + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

        # Two children.
        left, n, p, x = self._display_aux(base.left)
        right, m, q, y = self._display_aux(base.right)
        s = '%s' % base.val
        u = len(s)
        first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s + y * '_' + (m - y) * ' '
        second_line = x * ' ' + '/' + (n - x - 1 + u + y) * ' ' + '\\' + (m - y - 1) * ' '
        if p < q:
            left += [n * ' '] * (q - p)
        elif q < p:
            right += [m * ' '] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + u * ' ' + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2

    def solve():
        pass

    def map(self,base = None,d = []):
        # Sets the index of the variable to the value index
        # Returns a dict of 'variable' and [path] pairs
        # path is an ordered list of '1/0'
        # Going left and right for 1,0 respectfully will lead to 'variable'

        if base == None:
            base = self.root

        if type(base.val) not in [bool,int,complex,float] and base.val not in '^*/%+-&|!<=>=':
            if base.val not in self.dir:
                self.dir[base.val] = []
            self.dir[base.val].append(d)

        if base.left is not None:
            self.map(base.left,d+[1])

        if base.right is not None:
            self.map(base.right,d+[0])

    def __str__(self):
        # Returns a string expression that is an equivalent expression to the graph
        # str and __init__ should be rough inverses of each other
        # 'a$b'== str(exp('a$b'))
        """
        >>> print(exp('a+b'))
        a+b
        >>> print(exp('(a+b)*c'))
        (a+b)*c
        """        
        return self._str_aux(self.root)

    def _str_aux(self,base,last_operator = None):
        # Auxillary equation of __str__
        # Referenced locally so technical parameters are hidden that are used for recursive calls

        op_order = {
            '=':1,
            '|':2,
            '&':3,
            '+':4,
            '-':4,
            '/':5,
            '*':5,
            '^':6
            }

        single_op = {
            '!':6,
            'sin':6,
            'cos':6,
            'tan':6,
            'csc':6,
            'sec':6,
            'cot':6,
            'asin':6,
            'acos':6,
            'atan':6
        }
        if base.val in single_op:
            return base.val+'('+self._str_aux(base.right)+')'

        if base.val not in op_order:
            return str(base.val)
        
        if last_operator and op_order[base.val]<op_order[last_operator]:
            return '('+ self._str_aux(base.left,base.val)+base.val+self._str_aux(base.right,base.val)+')'

        return self._str_aux(base.left,base.val) + base.val + self._str_aux(base.right,base.val)

    def invert_branch(self,var,root=None,inv_tree=None, path:list=[],include_var:bool=False):
        # Used for generating symbolic algebraic solutions to equations
        # inverts a particular path of the tree
        # generally used for inverting the path to a particular var
        # 'include_var'=True if the returned tree to be expressed as 'var = inv_tree'

        if root==None:
            root=self.root
            if var not in self.dir:
                raise Exception(f'\'{var}\' not found in Expression')
            path = self.dir[var][0] # if path is not specified takes the first path in dir
        
        
        for d in path:
            inv_tree = self.__invert_aux(root,d,inv_tree)
            root = root.left if d else root.right

        if include_var:
            inv_tree = node('=',root,inv_tree)
        return exp(root = inv_tree)

    def __invert_aux(self,tree,left:int,inv_root=None):
        # Performs the inverse operation of a single node operation 
        # given the left/right direction of the component that is being solved for
        # returns a inv_tree that is the parameter inv_tree operated on by the 
        # inv of the base.val operation

        operator = tree.val

        if operator=='=':
            if inv_root==None:
                return tree.right if left else tree.left
            else:
                return node('=',left = inv_root,right =tree.right if left else tree.left)

        elif operator=='+':
            return node('-',left = inv_root,right = tree.right if left else tree.left)
        
        elif operator=='-':
            if left:
                return node('+',left = inv_root,right = tree.right)
            return node('-',left = tree.left,right=inv_root)
        
        elif operator == '*':
            return node('/',left = inv_root,right = tree.right if left else tree.left)
        
        elif operator=='/':
            if left:
                return node('*',left=inv_root,right=tree.right)

            node('/',left=tree.left,right=inv_root)

        elif operator == '^':
            if left:
                pow_node = node('/',left=node(1),right=tree.right)
                return node('^',left=inv_root,right=pow_node)



def _tokenize(input_str:str)->list:
    # Tokenize a string into a list of the macro elements of the exp
    # For each reserved command replace it with comma it and comma delimiters and finally split by commas
    """
    >>> _tokenize('a+b')
    ['a', '+', 'b']
    """
    exp_list = [
        '=',
        '(',
        ')',
        '+',
        '-',
        '*',
        '/',
        '^',
        '==',
        '|',
        '&',
        '>',
        '>=',
        '<',
        '<=',
        '!',
        'cos',
        'sin',
        'tan',
        'sec',
        'csc',
        'cot',
        'asin',
        'acos',
        'atan'
    ]
    
    for e in exp_list:
        input_str = input_str.replace(e,','+e+',')
    
    tokenize_str = [val for val in input_str.split(',') if val!='']

    return tokenize_str

class node:
    # Units of expression objects
    # Describes the structure of mathematical expressions in with 
    # operations and left and right components

    def __init__(self,val,left:any= None,right:any = None):
        self.val = val
        self.right = right
        self.left = left


if __name__=="__main__":
    import doctest
    doctest.testmod()