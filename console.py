#!/usr/bin/env python3
#from axioms_2 import exp

"""
this is the user input loop. It collects and parses user input.
there are certain commands which are supported, and a valid command must be used
for an operation to be valid.

list of valid commands:
    - set_expr EXPRESSION
    - load FILE
    - eval EXPRESSION
    - clear

for convenience, there is an implicit set_expr command. If the first token isn't
a valid command, then it is assumed that the user input are paremeters for set_expr
"""
while True:
    cmd_string = input('>> ')

    # decode cmd_string
    # match command to correct operation

    if cmd_string == 'exit':
        break
    else:
        print('"' + cmd_string + '"', ' is not a recognized command or syntax' )
        continue
