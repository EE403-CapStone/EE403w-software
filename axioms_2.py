# Author: Erik Huuki
# The backend software of EE403 capstone Design project
# Description:
# Axioms_2 is a symbolic math library that converts mathematical statements binary trees
# This is for the purposes of automating symbolic math operations that 
# undergraduates and professional engineers frequent


from ast import Pass, operator
import doctest
import numpy as np

class expr:
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

    def exp2tree(self,exp):
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

    def _str2values(self,s):
        # Converts a string to values that are recognized as either bool, int, float, complex
        # Where naming conventions match python 

        special_cases = {
            '':None,
            'True':True,
            'False':False,
            'j':1j
        }

        if s in special_cases:
            return special_cases[s]


        iscomplex = s[-1]=='j'
        s = s[:-1] if iscomplex else s
        
        if s.count('.')==1:
            n,dec = s.split('.')
            power = len(dec)
            if n.isdigit() and dec.isdigit():
                n,dec = map(float,[n,dec])
                dec/=10**power
                return (n+dec)*1j if iscomplex else n+dec
        
        if s.isdigit():
            return int(s)*1j if iscomplex else int(s)
        
        if s[0].isdigit():
            raise Exception(f'{s} is an invalid variable name')

        return s+'j' if iscomplex else s

    def list2tree(self,op_list:list):
        # Converts a tokenized expression to a tree
        # list2tree(['a','+','b'])=> node(val='+', left=node('a'), right=node('b'))
        # Handles parhentesis

        single_arg_operators = [
            'sin',
            'cos',
            'tan',
            'csc',
            'sec',
            'cot',
            'asin',
            'acos',
            'atan',
            '!',
            'exp'
            ]
        
        while '(' in op_list:           # compresses parhentesis protected expressions
            op_list = self.compress_parhentesis(op_list)
        
        if len(op_list)==1:
            if type(op_list[0])in [str,bool, int, float, complex]:
                return node(op_list[0])

            elif type(op_list[0])==list:
                return self.list2tree(op_list[0])
        
        elif len(op_list)==2 and isinstance(op_list[0],str) and op_list[0] in single_arg_operators: # Recognized single argument expressions
            return node(op_list[0],right=self.list2tree(op_list[1]))

        elif len(op_list)==2 and isinstance(op_list[0],str) and isinstance(op_list[1],list):        # arbitrary function
            temp = ''.join(map(str,op_list[1][0]))
            temp = temp.split(',')
            return node(op_list[0],right = node(temp))
        
        if op_list[0]=='-':            # case of -x
            op_list[:2] = [-1,'*',op_list[1]]
            
        next_operator = self.next_operator(op_list)

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
            'atan',
            'ln']

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

    def evaluate(self,root=None,val_dict:dict={}):
        # Evaluates an expression tree
        # If all the end nodes are operatable expressions returns value
        # Else returns None
        # Assumes the expression to be valid ie. For expressions with logical statements or equivalencies
        # it is assumed the expressions are valid

        '''
        >>> a = expr('a+b')
        >>> a.evaluate(val_dict={'a':1,'b':2})
        3
        '''

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
            '==': lambda a,b: a==b,
            '=': 'Easter Egg'
        }

        single_operators={          # operators with single inputs
            '!':lambda a:not a,
            'cos':lambda a: np.cos(a),
            'sin':lambda a: np.sin(a),
            'tan':lambda a: np.tan(a),
            'sec':lambda a: np.sec(a),
            'csc': lambda a: np.csc(a),
            'asin': lambda a: np.arcsin(a),
            'acos': lambda a: np.arccos(a),
            'atan':lambda a : np.arctan(a),
            'ln': lambda a: np.log(a),
            'exp': lambda a:np.exp(a)
        }

        if isinstance(root.val,str) and root.val not in (operator or single_operators):# Identified variable type
            val_dict['pi'] = np.pi
            val_dict['e'] = np.e
            if root.val in val_dict:
                return val_dict[root.val]
            return None

        right = self.evaluate(root.right,val_dict=val_dict)

        if root.val=='=': # '=' operator requires a little more complication
            left = self.evaluate(root.left, val_dict=val_dict)
            if type(left) or type(right) in [bool,int,float,float,complex]:
                if left==None:
                    return right
                elif right==None:
                    return left
                elif right==left:
                    return right
                raise Exception('Invalid expression: '+str(self)) # Both left/right can be evaluated but are different

            return None # If neither left or right expresssions can be operated on

        if right==None:
            return None

        if root.val in single_operators:
            return single_operators[root.val](right)

        left = self.evaluate(root.left, val_dict=val_dict)

        if root.val in operator:
            if left ==None:
                return None
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
            s = '%s' % base.val
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
        
        arbitrary_function = base.right!=None and isinstance(base.right.val,list)

        if not arbitrary_function:
            if base.left is not None:
                self.map(base.left,d+[1])

            if base.right is not None:
                self.map(base.right,d+[0])

    def __str__(self):
        # Returns a string expression that is an equivalent expression to the graph
        # str and __init__ should be rough inverses of each other
        # 'a$b'== str(exp('a$b'))
        """
        >>> print(expr('a+b'))
        a+b
        >>> print(expr('(a+b)*c'))
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
            'atan':6,
            'ln':6,
            'exp':6
        }
        
        if base.val in single_op:
            return base.val+'('+self._str_aux(base.right)+')'
        elif isinstance(base.val,str) and base.left==None and base.right!=None: # Arbitrary functions
            return base.val+'('+','.join(base.right.val)+')'

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
        return expr(root = inv_tree)

    def __invert_aux(self,tree,left:int,inv_root=None):
        # Performs the inverse operation of a single node operation 
        # given the left/right direction of the component that is being solved for
        # returns a inv_tree that is the parameter inv_tree operated on by the 
        # inv of the base.val operation
        left_inv_dict = {
            '=':None,
            '+':None,
            '-':None,
            '*':None,
            '/':None,
            '^':None,
            '=':None
        }
        right_inv_dict={
            '=':None,
            '+':None,
            '-':None,
            '*':None,
            '/':None,
            '^':None,
            '!':None,
            'exp':None,
            'ln':None,
            'sin':None,
            'cos':None,
            'tan':None,
            'csc':None,
            'sec':None,
            'cot':None,
            'asin':None,
            'acos':None,
            'atan':None,
        }
        operator = tree.val
        # can make this a mapping of lambda functions for commutable operations and single operators

        # Double operations that are non commutable

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
            
            num = node('ln',right=inv_root)
            den = node('ln',right=tree.left)
            return node('/',left=num,right= den)
        
        
        ## Inverting single operators below
        # expressions of the form f(f(x))=a
        # maps inversion step to get f(x) = f^-1(a)

        inv_map = {
            'sin':lambda a:node('asin',right=a),
            'cos':lambda a:node('acos',right=a),
            'tan':lambda a:node('atan',right=a),
            'ln':lambda a:node('exp',right=a),
            'exp':lambda a:node('ln',right = a),
            '!':lambda a:node('!',right=a),
            'csc':lambda a:node('asin',right=node('/',node(1),a)),
            'sec':lambda a:node('acos',right=node('/',node(1),a)),
            'cot':lambda a:node('atan',right=node('/',node(1),a))
        }

        if operator in inv_map:
            return inv_map[operator](inv_root)

    def pD(self,var):
        root = self._partial_D_aux(self.root,var)
        root = self._reduce(root)
        return expr(root=root)
        

        #reduce functionality
        
    def _partial_D_aux(self,root,var=''):
        if var=='':
            raise Exception(f'df/d"x" not defined in partial derivative')
        # a is the root of an expr with left and right components
        # below is a map of derivative rules written as da/dvar where left and right
        # nodes of a are assummed to be functions of var
        
        d_map = {
            '+':lambda a,var: node( # f+g => f'+g'
                '+',self._partial_D_aux(a.left,var),self._partial_D_aux(a.right,var)),
            '-':lambda a,var: node( # f-g => f'-g'
                '-',self._partial_D_aux(a.left,var),self._partial_D_aux(a.right,var)),
            '*':lambda a,var: node( # f*g => f'g+fg'
                '+',
                left = node('*',self._partial_D_aux(a.left,var),a.right),
                right = node('*',a.left,self._partial_D_aux(a.right,var))),
            '/':lambda a,var:node( # f/g => (f'*g-f*g')/(g^2)
                '/',
                left=node(
                  '-',
                  left = node('*',a.right,self._partial_D_aux(a.left,var)),
                  right = node('*',a.left,self._partial_D_aux(a.right,var))
                ),
                right = node('^',left = a.right,right=node(2))
            ),

            '^':lambda a,var:self._power_D(a,var), ## general formula for f^g was too hairy for lambda function

            'sin':lambda a,var:node( # sin(f)=> f'*cos(f)
                '*',
                left = self._partial_D_aux(a.right,var),
                right = node('cos',right=a.right)
            ),
            'cos':lambda a,var:node( # cos(f)=> -f'*sin(f)
                '*',
                left = node('*',node(-1),self._partial_D_aux(a.right,var)),
                right = node('sin',node(a.right))
            ),
            'tan':lambda a,var:node( # tan(f)=> f'*sec(f)^2
                '*',
                left = self._partial_D_aux(a.right,var),
                right=node(
                    '^',
                    left = node('sec',right=a.right),
                    right = node(2))
            ),
            'csc':lambda a,var:node( # csc(f)=> -f'*csc(f)*cot(f)
                '*',
                node(-1),
                node(
                    '*',
                    node(self._partial_D_aux(a.right,var)),
                    node(
                        '*',
                        node('csc',right=a),
                        node('cot',right=a)
                    )
                )
            ),
            'cot':lambda a,var:node(  # cot(f) => -f'*csc(f)^2
                '*',
                node(-1),
                node(
                    '*',
                    self._partial_D_aux(a.right,var),
                    node(
                        '^',
                        node('csc',right=a),
                        node(2)
                    )
                )
            ),
            'asin':lambda a,var:node( # asin(f) => f'/sqrt(1-f^2)
                node(
                    '/',
                    self._partial_D_aux(a.right,var),
                    node(
                        '^',
                        node(
                            '-',
                            node(1),
                            node('^',a,node(2))
                        ),
                        node(1/2)
                    )
                )
            ),
            'acos':lambda a,var:node( # acos(f) => -1*f'/sqrt(1-f^2)
                node(
                    '/',
                    node(
                        '*',
                        node(-1),
                        self._partial_D_aux(a.right,var)
                    ),
                    node(
                        '^',
                        node(
                            '-',
                            node(1),
                            node('^',a,node(2))
                        ),
                        node(1/2)
                    )
                )
            ),
            'atan':lambda a,var:node( # atan(f) => f'/(1+f^2)
                '/',
                self._partial_D_aux(a.right,var),
                node(
                    '+',
                    node(1),
                    node(
                        '^',
                        a.right,
                        node(2)
                    )
                )
            ),
            'exp':lambda a,var: node( # exp(f) => f'*exp(f)
                '*',left=self._partial_D_aux(a.right,var),right=a),
            '=':lambda a,var:node( # f=g => f'=g'
                '=',
                self._partial_D_aux(a.left,var),
                self._partial_D_aux(a.right,var)
            )
        }


        if root.val==var:
            return node(1)
        
        elif root.right == None and root.val not in d_map or type(root) in [bool,int,float,complex]:
            return node(0)
        
        return d_map[root.val](root,var)


    def _reduce(self,root):
        
        if isinstance(root.val,str) and root.right==None: #instances of variables 
            return root
        elif type(root.val) in [int,bool,complex,float]:
            return root

        right = self._reduce(root.right)
        left = None
        if root.left:
            left = self._reduce(root.left)

        if root.val=='+':
            if left.val ==0:
                return right
            elif right.val == 0:
                return left
        elif root.val=='-':
            if right.val==0:
                return left
            elif left.val==0:
                return node('*',node(-1),right)
        
        elif root.val=='*':
            e = str(expr(root=root))

            if right.val==1:
                return left
            elif left.val==1:
                return right
            elif left.val==0 or right.val == 0:
                return node(0)

        elif root.val == '/':
            if right.val==1:
                return left
            if left.val==0:
                return left
            pass
        
        elif root.val=='exp':
            if right.val==0:
                return node(1)
            if right.val=='ln':
                return right.right
        
        elif root.val=='ln':
            if right.val=='e':
                return node(1)
            elif right.val=='^' and right.left.val=='e':
                return right.right
            elif right.val=='exp':
                return right.right            

        elif root.val=='^':
            if right.val==0 and left.val!=0:
                return node(0)
            elif left.val== (0) and right.val==(0):
                raise Exception('Invalid expression 0^0')
            elif left.val==1:
                return node(1)
        
        elif root.val=='sin':
            if right==0:
                return right
        elif root.val=='cos':
            if right==0:
                return node(1)
        
        return node(root.val,left,right)
        
        

    def _power_D(self,root,var):# general formula for df/dx(f^g) where f and g are functions of x
        f = root.left
        g = root.right
        
        # s1 = (g*f')/f
        s1 = node(
            '/',
            left = node(
                '*',
                g,
                self._partial_D_aux(f,var)
            ),
            right = f
        )
        # s2 = g'*ln(f)
        s2 = node(
            '*',
            left = self._partial_D_aux(g,var),
            right= node('ln',right=f)
        )

        s = node('+',s1,s2)

        return node('*',left = s,right=root)

    def _exp_classify():
        # Classifying expressions for the purposes making decisions of how to integrate,
        # and analyical or numerical solutions
        pass

    def replace(self,var:str, root):
        for path in self.dir[var]:
            temp = self.root
            for left in path:
                temp = temp.left if left else temp.right
            temp = root

def _tokenize(input_str:str)->list:
    # Tokenize a string into a list of the macro elements of the exp
    # For each reserved command replace it with comma it and comma delimiters and finally split by commas
    """
    >>> _tokenize('a+b')
    ['a', '+', 'b']
    """
    delimiter = ' '
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
        'atan',
        'ln',
        ','
    ]
    for e in exp_list:
        input_str = input_str.replace(e,' '+e+' ')
    
    tokenize_str = [val for val in input_str.split(' ') if val!='']

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