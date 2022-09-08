# Test suite for axioms_2
# Purpose is to define how axioms work with test cases
# The goal of axioms_2 will be to satisfy this test doc
# 


import doctest
from axioms_2 import exp


# Class and function definitions to streamline comparing graphs
# axioms_2 operates on symbolic math using directed graph 
# To ensure axioms_2 is as complete as possible test cases need to be included for user errors
class test_graph():
    def __init__(self,head,right=None,left=None):
        pass
    
def equal(g1,g2):
    pass




doctest.testmod()