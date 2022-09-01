import math as m

class expression:
	def __init__(self,exp=None,root = None):
		self.root = root						# If a tree root is not passes it will toke on None
		self.dir = {}

		if root==None:
			if isinstance(exp,str):					# If a string expression is passed it will convert it to a list ops
				ops = []
				temp_var = ''
				for i,e in enumerate(exp):

					if e in ['+','-','=','/','*','^','(',')']:	# Recognized operations

						if temp_var!='':
							ops.append(self.str2operand(temp_var))
							temp_var = ''
						ops.append(operator(e))


					elif e=='(' or e==')':
						if temp_var!='':
							ops.append(self.str2operand(temp_var))
							temp_var = ''

						ops.append(operand(e))

					else:
						temp_var+=e				                # Else build temp_var

				if temp_var!='':
					ops.append(self.str2operand(temp_var))

				self.exp2tree(ops)								# convert the ordered list to a tree

			elif isinstance(exp,list):
				self.exp2tree(exp)								# For the case exp is an ordered list

	def tree2exp(self,base=None):
		if base==None:			#Starts the string at the root
			base = self.root

		# Recursively generates the expression from the tree
		# terminating when operands have None for left and right

		if base.left == None and base.right==None:
			return str(base.val)

		elif base.left==None:
			return str(base.val)+self.tree2exp(base.right)

		elif base.right == None:
			return self.tree2exp(base.left)+str(base.val)

		else:
			return self.tree2exp(base.left)+str(base.val)+self.tree2exp(base.right)

	def str2operand(self,op):
		try:
			temp = operand(float(op))	# try to float
			return temp

		except ValueError:
			try:
				temp = operand(complex(op))# try to complex
				return temp	
			except ValueError:
				return operand(op)	
				
	def compress_parenthesis(self,ops):

		depth = 1					# scans for the matching parhentesis depth is the current depth
		m = [None,-1] 				# [index of the first parhentese m is the depth, index of it's counterpart]

		for i,e in enumerate(ops):
			if e.val=='(':
				if m[0]==None:
					m[0] = i
				else:
					depth += 1		# depth increses for '('

			elif e.val==')':
				depth-=1			# depth decreases for ')'

			if depth==0:			# records the counterpart index
				m[1] = i
				break
		if depth>0:
			raise Exception('Mismatched delimeter')

		temp = expression(ops[m[0]+1:m[1]])	# Creates a tree expression from the elements within the ()
		temp.root.operand = True			# The root is represented as an operand
		temp.root.operation = False
		ops[m[0]:m[1]+1] = [temp.root]			# The indexes within () inclusive are replaced by the root of the expression contained

		return ops 									# returns the shortened list

	def exp2tree(self,ops):	# takes an expression and generates a binary tree representation

		i = 0
		while i<len(ops):						# As long as there are functional () compress() comrpresses () into the highest order operands and operations
			if ops[i].val=='(':
				ops = self.compress_parenthesis(ops)
				i = -1
			i+=1

		for i,e in enumerate(ops):						# If there is an equal sign it becomes the root
			if  e.val=='=':
				self.root = e
				e.left = expression(ops[:i])()		# Recursively generates the branches of the tree
				e.right = expression(ops[i+1:])()
				return e 								# When this is contained within the stack it returns the root of it's tree


		for i,e in enumerate(ops):
			if e.operation:								# When it's an operation it branches to the left and right within the ops
				if self.root==None:
					self.root = e
				e.left = expression(ops[:i])()			# left branch
				e.right = expression(ops[i+1:])()		# Right branch
				return e 								# When this itself is within the it returns it's root to the larger branch

		for i,e in enumerate(ops):						# The recursion terminates indexes are no longer operations
			if e.operand:
				if self.root==None:						# Cases where there is no equal or operators
					self.root = e 						# This can only occur when there no longer operators in the list

				if e.val in ['+','-','*','^','/','=']:
					e.operation =True
				return e

	def smooth_exp(self,base=None):
		if base==None:
			base = self.root

		if base.val=='-':		# replaces '-' with '+ (-)'
			base.val = '+'
			temp = base.right
			base.right = operator('*')
			base.right.left = temp
			base.right.right = operand(-1)

		elif base.val=='/':
			temp = base.right
			base.val='*'
			base.right = operator('^')
			base.right.right = operand(-1)
			base.right.left = temp

		if base.left is not None:
			self.smooth_exp(base.left)

		if base.right is not None:
			self.smooth_exp(base.right) 

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

	def map(self,base = None,d = []): # sets the index of the variable to the value index
		if base == None:
			base = self.root

		if self.isoperand(base.val):
			if base.val not in self.dir:
				self.dir[base.val] = []
			self.dir[base.val].append(d)

		if base.left is not None:
			self.map(base.left,d+[1])

		if base.right is not None:
			self.map(base.right,d+[0])

	def evaluate(self,root=None):
		
		if root==None:
			root= self.root

		if isinstance(root.val,int) or isinstance(root.val,float) or isinstance(root.val,complex):
			return root.val

		if root.operation:
			if root.val=='+':
				return self.evaluate(root.left)+self.evaluate(root.right)

			elif root.val=='-':
				return self.evaluate(root.left)-self.evaluate(root.right)

			elif root.val=='*':
				return self.evaluate(root.left)*self.evaluate(root.right)
				
			elif root.val=='^':
				return self.evaluate(root.left)**self.evaluate(root.right)

			elif root.val=='/':
				return self.evaluate(root.left)/self.evaluate(root.right)

			elif root.val=='=':
				try:
					r = self.evaluate(root.right)
					if r==None:
						raise TypeError ('Expression terminates on None')
					# print(self.tree2exp(root.right))
					return r

				except TypeError:
					try:
						r = self.evaluate(root.left)
						if r== None:
							raise TypeError ('Expression Terminates on None')

						# print(self.tree2exp(root.left))
						return r
					except:
						return None

		elif root.val=='pi':
			return 3.14159265358979323846

		elif root.val=='e':
			return 2.7182818284590455

			print('cannot evaluate{d}'.format(d=self.tree2exp(root)))		

	def constrain(self,var=None,val = 0):

		temp = expression('=')

		# Setting the right hand side of temp to different cases
		if isinstance(val,int) or isinstance(val,float) or isinstance(val,complex):	# numbers
			temp.root.right = operand(val)

		elif isinstance(val,str):	#strings
			temp.root.right = expression(val)()
		else:
			temp.root.right = val()# expression objects

		# Setting the left hand side of temp to the var

		if var==None:	# When var is None, constrain self
			temp.root.left = self.root
			self.root = temp

		elif isinstance(var,str):	# When var is a string replace said said string with (var=temp)
			temp.root.left = operand(var)
			self.replace(var,temp)

	def replace(self,var,replacement):
		self.dir = {}
		self.map()

		if var in self.dir:
			directions = self.dir[var]
		
		else:
			return

		for d in directions:
			root = self()
			
			for e in d[:-1]:
				if e:
					root = root.left
				else:
					root = root.right
			try:
				replacement()
				if d[-1]:
					root.left = replacement()
				else:
					root.right = replacement()
			except:	
				r = operand(replacement)
				if d[-1]:
					root.left = r
				else:
					root.right = r

	def invert_branch(self,var):
		self.dir = {}
		self.map()

		if var not in self.dir.keys():
			raise Exception(f"({var}) not in {self.tree2exp()}")
		
		d = self.dir[var]

		# if len(d)>1:
		# 	raise Exception(f"'{var}' appears multiple times")
		
		d = d[0]

		root = self.root
		invtree = expression()


		for e in d:

			if e:
				temp = root.right # the part that branches away from the direction to the var
				
			else:
				temp = root.left


			if root.val=='+':
				base = operator('-')
				base.left = invtree()
				base.right = temp

				invtree.root = base

			elif root.val=='-':
				if e:
					base = operator('+')
					base.right = invtree()
					base.left = temp

					invtree.root = base
				else:
					base = operator('-')
					base.right = invtree()
					base.left = temp

					invtree.root = base


			elif root.val=='*':
				base = operator('/')
				base.left = invtree()
				base.right = temp

				invtree.root = base

			elif root.val =='/':
				if e:
					base = operator('*')
					base.right = invtree()
					base.left = temp

					invtree.root = base

				else:
					base = operator('/')
					base.right = invtree()
					base.left = temp

					invtree.root = base

			
			elif root.val =='^':
				if e:
					base1 = operator('/')
					base1.left = operand(1)
					base1.right = temp

					base = operator('^')
					base.right = base1
					base.left = invtree()
					invtree.root = base
				else:
					raise Exception(f"Cannot evaluate '^' for '{root.val}' in ({self.tree2exp(temp)})^({self.tree2exp(root.right)})={self.tree2exp(invtree())}")

			elif root.val=='=':
				if invtree() is not None:
					base = operator('=')
					base.right = invtree()
					base.left = temp
					invtree.root = base

				else:
					invtree.root=temp


			if e:
				root = root.left # the path to var
				
			else:
				root = root.right

		return invtree

	def car2pol(self,cart):
		theta = m.atan(cart.imag/cart.real)*180/m.pi

		return abs(cart), theta-180*(cart.real<0)

	def solve(self):
		self.dir = {}
		self.map()

		sol = {'exp':self.evaluate()}

		for var in self.dir:
			try:
				Var_exp = self.invert_branch(var)
				evaluated = Var_exp.evaluate()

				if(evaluated is not None):
					print(f"{var} = {evaluated}")
					sol[var] = evaluated
			except:
				print(f"Cannot solve {var}")

		return sol

	def isoperand(self,var):
		try:
			if var in ['+','-','=','/','*','^','e','pi']:
				return False

			complex(var)
			
			return False
		
		except ValueError:
			return True

	def connect_exps(exps):
		r_exp = exps[0]
		r_exp.dir = {}
		r_exp.map()

		for e in exps[1:]:
			e.dir = {}
			e.map()

			for key in e.dir:
				if key in r_exp.dir:
					key_inv = e.invert_branch(key)
					r_exp.constrain(key,key_inv)
					r_exp.dir = {}
					r_exp.map()
					break

		return r_exp

	# def parD(self,var,root):

	# def pD(self,var):# Partial Derivative of expression with respect to var
		
	# 	self.dir = {}
	# 	self.map()

	# 	if var not in self.dir.keys():
	# 		raise Exception(f"({var}) not in {self.tree2exp()}")

	# 	d = self.dir[var]

	# 	# return self.parD(var,self.root)


	def __call__(self):
		return self.root

class operator:
	def __init__(self,val=None):
		self.val = val
		self.right = None
		self.left = None
		self.operand = False
		self.operation = True
		self.operator= True

class operand:
	def __init__(self,val=None):
		self.val = val
		self.operand = True
		self.operation = False
		self.right = None
		self.left = None

