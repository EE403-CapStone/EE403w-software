class exp:
    def __init__(self,exp=None,**kwargs):
        self.root = None
        if isinstance(exp,str):
            self.root = self.exp2tree(exp)
        
        if 'root' in kwargs:
            self.root = self.exp2tree(kwargs['roots'])
        
        if 'exp' in kwargs:
            self.root = self.exp2tree(kwargs['exp'])


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
                    exp_list.append(temp_var)
                    temp_var = ''
                
                exp_list.append(val)    
            else:
                temp_var+=val
        
        if temp_var != '':
            exp_list.append(temp_var)

        
        root = self.list2tree(exp_list)

        return root
    
    def list2tree(self,op_list:list):
        while '(' in op_list:   # compresses parhentesis protected expressions
            op_list = self.compress_parhentesis(op_list)

        if len(op_list)==1:
            if isinstance(op_list[0],str):
                return node(op_list[0])
            else:
                return op_list[0]
        
        next_operator = self.next_operator(op_list)

        val = op_list[next_operator]
        right = self.list2tree(op_list[next_operator+1:])
        left = self.list2tree(op_list[:next_operator])

        return node(val,left,right)
    
    def next_operator(self,exp_list):
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



    def compress_parhentesis(self,expression):
        outerleft_P_indices = [None,None]

        p1 = expression.index('(')   # left parhentesis
        depth = 1
        for i,c in enumerate(expression[p1+1:]):
            if c=='(':
                depth+=1
            elif c==')':
                depth-=1
            
            if depth==0:
                break
        
        p2 = p1+i+1
        temp_root = self.list2tree(expression[p1+1:p2])
        expression[p1:p2+1] = [temp_root]
        return expression



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

    def __str__(self):
        pass
    


class node:
    def __init__(self,val,left = None,right = None):
        self.val = val
        self.right = right
        self.left = left

    # def __call__(self):
    #     return self.val