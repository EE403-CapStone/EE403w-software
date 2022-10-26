## Math Engine

The calculators runtime enviorment is an application to manipulate mathematical expressions. This enviorment has been split into 2 parts. The UX and a math engine. The UX calls upon the math engine to perform tasks that we define with custom syntax. This leaves the Math engine to physically carry out symbolic math operations. 

This section will describe how the math engine can be used in a python enviorment.

To import the math engine axioms_2 into a python enviorment

```python
from axioms_2 import expr
```

expr is an object class with instance variable root. The value of root is the root node of an expression tree. One hurdle was converting a text expression into a directed graph. 

### Nodes and Math Expressions as directed graphs

Math expressions can be described as directed graphs. An expression 'a+b' can be saved in memory as a directed graph as follows

```python
class node:
    def __init__(self,val,left=None,right=None):
        self.val = val
        self.left = left
        self.right = right

root = node('+',left = node('a'), right = node('b'))
```

expr.__init__() automates this process so complex mathematical graphs can be instantiated with strings. This process replicates the PEMDOS order of operation. __init__() recognizes True, False, integers, floating point and complex values. Variables are recognized as anything that starts with a character that is not the reserved strings e, pi, j. e is Eulers number. pi is the ratio of circles diameter to it's circumfrence. 'j' is the $\sqrt{-1}$

![](expression2graph.png)

The above figure shows  