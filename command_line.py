from axioms_2 import exp


def isvalid(s):
    # Statements that check if statements are able to be processed
    return True


# Reserved characters that perform actions
r_chars = [
    ':'
]

exp_dir = {}

while True:
    s = input('> ')
    output = (s[-1]==';')
    output_string = ''
    s = s[:-1] if output else s

    # Check validity of statements according to our spec
    if not isvalid(s):
        print('Invalid Statement')
        continue

    if s=='clear':
        exp_dir = {}
    
    if ':' in s:
        if s.count(':')>1:  # Need to 
            print('Invalid expression')
        
        l = s.split(':')

        exp_dir[l[0]]=exp(l[1])
        output_string = exp_dir[l[0]]
    else: 
        exp_dir['ans']=exp(l[0])
        output_string = str(exp_dir['ans'])
    
    if output:
        print(output_string)
    
