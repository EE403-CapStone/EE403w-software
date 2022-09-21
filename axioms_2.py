import doctest


class exp:
    def __init__(self,exp=None,root=None,**kwargs):
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
        exp_list = []

        # check for mismatched delimiters
        if exp.count('(')!= exp.count(')'):
            raise Exception('Mismatched delimiters')
        
        exp = exp.replace(' ','')       # Remove blank space

        # Need to check for incomplete expressions / errors in expressions

        # tokenizes the string expression into a list
        temp_var = ''
        for val in exp:
            # simple operators to handle in an exp
            if val in '()^*/%+-=&|!':
                if temp_var != '':
                    # str to values function
                    exp_list.append(self._str2values(temp_var))
                    temp_var = ''
                
                exp_list.append(val) 
            else:
                temp_var+=val
        
        if temp_var != '':
            exp_list.append(self._str2values(temp_var))

        
        root = self.list2tree(exp_list)

        return root

    def _str2values(self,s:str)->any:
        # recognize special string inputs example True False
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

        while '(' in op_list:   # compresses parhentesis protected expressions
            op_list = self.compress_parhentesis(op_list)

        if len(op_list)==1:
            if type(op_list[0])in [str,bool, int, float, complex]:
                return node(op_list[0])

            elif type(op_list[0])==list:
                return self.list2tree(op_list[0])
        
        if op_list[0]=='-':            # case of -x
            op_list[:2] = [-1,'*',op_list[1]]
            
        next_operator = self.next_operator(op_list)

        val = op_list[next_operator]
        left = self.list2tree(op_list[:next_operator])
        right = self.list2tree(op_list[next_operator+1:])
        

        return node(val,left,right)
    
    def next_operator(self,exp_list):
        # Switch case of PEMDOS in reverse order
        if '=' in exp_list:
            return exp_list.index('=')
        if '|' in exp_list:
            return exp_list.index('|')
        if '&' in exp_list:
            return exp_list.index('&')        
        if '+' in exp_list:
            return exp_list.index('+')
        if '-' in exp_list:
            return exp_list.index('-')
        if '/' in exp_list:
            return exp_list.index('/')
        if '*' in exp_list:
            return exp_list.index('*')
        if '^' in exp_list:
            return exp_list.index('^')

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
        if root==None:
            root= self.root

        # For when the root val is in this set of classes return the raw value
        if type(root.val) in [bool,int,float,float,complex]:
            return root.val

        elif root.val=='=':
            right = self.evaluate(root.left)
            if right==None:
                return self.evaluate(root.left)

        left = self.evaluate(root.left)
        right = self.evaluate(root.right)

        if left==None or right==None:
            return None

        if root.val=='+':
            return left+right

        elif root.val=='-':
            return left-right

        elif root.val=='*':
            return left*right
            
        elif root.val=='^':
            return left**right

        elif root.val=='/':
            return left/right

        elif root.val=='%':
            return left%right
        # Need to check functionality of logic operators
        elif root.val=='&':
            return left and right
        
        elif root.val=='|':
            return left or right
        
        elif root.val=='!':
            return not root.val

    def display(self,root=None):
        if root==None:
            root = self.root
        lines, *_ = self._display_aux(root)
        for line in lines:
            print(line)

    def _display_aux(self,base=None):
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

    def map(self,base = None,d = []): # sets the index of the variable to the value index
        if base == None:
            base = self.root

        if type(base.val) not in [bool,int,complex,float] and base.val not in '^*/%+-=&|!':
            if base.val not in self.dir:
                self.dir[base.val] = []
            self.dir[base.val].append(d)

        if base.left is not None:
            self.map(base.left,d+[1])

        if base.right is not None:
            self.map(base.right,d+[0])

    def __str__(self):
        # Returns a string expression that will produce the same graph
        # exp==exp(str(exp))
        """
        >>> print(exp('a+b'))
        a+b
        >>> print(exp('(a+b)*c'))
        (a+b)*c
        """        
        return self._str_aux(self.root)

    def _str_aux(self,base,last_operator = None):
        op_order = {'=':1,'|':2,'&':3,'+':4,'-':4,'/':5,'*':5,'^':6}

        if base.val not in op_order:
            return str(base.val)
        
        if last_operator and op_order[base.val]<op_order[last_operator]:
            return '('+ self._str_aux(base.left,base.val)+base.val+self._str_aux(base.right,base.val)+')'

        return self._str_aux(base.left,base.val) + base.val + self._str_aux(base.right,base.val)

### in production ###
    def invert_branch(self,var,root=None,inv_tree=None, path:list=[]):

        if root==None:
            root=self.root
            if var not in self.dir:
                raise Exception(f'\'{var}\': Not found in Expression')
            path = self.dir[var][0] # if path is not specified takes the first path in dir
        
        left = path[0]  # Path towards the variable 1 if left 0 if right 
        
        for d in path:
            inv_tree = self.__invert_aux(root,d,inv_tree)
            root = root.left if d else root.right

        inv_tree = node('=',root,inv_tree)
        return exp(root = inv_tree)

    
    def __invert_aux(self,tree,left:int,inv_root=None):
        operator = tree.val

        # Switch case for how to invert every operation
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
            else:
                return node('-',left = tree.left,right=inv_root)
        
        elif operator == '*':
            return node('/',left = inv_root,right = tree.right if left else tree.left)
        
        elif '^':
            if left:
                pow_node = node('/',left=1,right=tree.right)
                return node('^',left=inv_root,right=pow_node)

class node:
    def __init__(self,val,left:any= None,right:any = None):
        self.val = val
        self.right = right
        self.left = left

    # def __call__(self):
    #     return self.val


if __name__=="__main__":
    import doctest
    doctest.testmod()