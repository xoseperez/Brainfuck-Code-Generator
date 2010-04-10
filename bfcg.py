#!/usr/bin/env python

import re
import sys
import shlex
import math

# -----------------------------------------------------------------------------

#argv = "3 3 POW debug"
#argv = "'Hello World!' PRINT_STR_AND_CLEAN"
#argv = "'Hello World!' BOL PRINT_STR"
#argv = "0 0 AND 0 1 AND 2 0 AND 2 34 AND debug"
#argv = "1 2 3 NDUP 1 DUP debug"
#argv = "17 1 DIV 17 3 DIV 17 5 DIV debug"
#argv = "3 5 SUB debug"
#argv = "'xose.perez@gmail.com\n' PRINT_STR_AND_CLEAN"
#argv = "100 3 MUL debug"
#argv = "'GCD using Euclidean algorithm\n' PRINT_STR_AND_CLEAN READ_NUM READ_NUM debug DUP IF NDUP 2 DIV SWAPDROP DUP PREVIOUS ENDIF PREVIOUS 'Result: ' PRINT_STR_AND_CLEAN PRINT_NUM LF debug" 
#argv = "'The answer is 42.' PRINT_STR_AND_CLEAN LF"
#argv = "READ_NUM debug PRINT_NUM debug"
#argv = "2 3 DUP MUL ADD"
#argv = "'Enter a number: ' PRINT_STR_AND_CLEAN NEXT READ_NUM DUP WHILE DEC DUP ENDWHILE PREVIOUS PREVIOUS WHILE NEXT MUL PREVIOUS ENDWHILE NEXT INC NEXT debug PRINT_NUM CLEAN debug"
argv = "'41 39 25 02 14 21' PRINT_STR_AND_CLEAN" 
# =============================================================================
# FUNCTIONS
# =============================================================================

operators = {}

# -----------------------------------------------------------------------------
# SUPPORT
# -----------------------------------------------------------------------------

operators['debug'] = { "code": "#" }
operators['CLEAN'] = { "code": "<[[-]<]" }
operators['CLR'] = { "code": "<[-]" }
operators['BOL'] = { "code": "<[<]>" }
operators['EOL'] = { "code": "[>]" }

# -----------------------------------------------------------------------------
# FLOW CONTROL
# -----------------------------------------------------------------------------

def flow_move(n):
    n = int(n)
    if n>0:
        return ">" * n
    elif n<0:
        return "<" * -n
operators['MOVE'] = { "callable": flow_move, "parameters": 1 }
operators['NEXT'] = { "code": ">" }
operators['PREVIOUS'] = { "code": "<" }

operators['IF'] = { "code": "<[[-]" }             # This instructions require the logic inside
operators['WHILE'] = { "code": "<[>" }            # to be deltaP=0
operators['ENDIF'] = { "code": "]" }
operators['ENDWHILE'] = { "code": "<]" }

# -----------------------------------------------------------------------------
# LOGIC
# -----------------------------------------------------------------------------

operators['NOT'] = { "code": "+<[[-]>-<]>[<+>-]" }
operators['OR'] = { "code": "<<[[-]>>+<<]>[[-]>+<]>[[-]<<+>>]<" }
operators['AND'] = { "code": "<<[[-]>[[-]>+<]<]>>[<<+>>-]<[-]" }

# -----------------------------------------------------------------------------
# OPERATORS
# -----------------------------------------------------------------------------

operators['ADD'] = { "code" : "<[<+>-]" }
operators['SUB'] = { "code" : "<[<->-]" }
operators['MUL'] = { "code" : "<<[>[>+>+<<-]>[<+>-]<<-]>>>[<<<+>>>-]<<[-]" }
operators['DIV'] = { "code" : "<-[+<[->-[>+>>]>[+[-<+>]>+>>]<<<<<]>>>[<<<+>>>-]<<[-]>[<+>-]>+<]>[-<]" }
#operators['POW'] = { "code" : "<-[>+<-]>[<<[>++<-]>[<+>-]>-]<<" }                 # DOES NOT WORK

def operator_incn(n=1):
    return "<" + ("+" * int(n)) + ">"
operators['INCN'] = { "callable" : operator_incn, "parameters": 1 }
operators['INC'] = { "callable" : operator_incn, "parameters": 0 }

def operator_decn(n=1):
    return "<" + ("-" * int(n)) + ">"
operators['DECN'] = { "callable" : operator_decn, "parameters": 1 }
operators['DEC'] = { "callable" : operator_decn, "parameters": 0 }

# -----------------------------------------------------------------------------
# STACK OPERATORS
# -----------------------------------------------------------------------------

operators['SWAP'] = { "code" : "<<[>>+<<-]>[<+>-]>[<+>-]" }
operators['SWAPDROP'] = { "code" : "<<[-]>[<+>-]" }
operators['DROPSWAP'] = { "code" : "<[-]<[>+<-]>>" }
operators['DROP'] = { "code" : "<[-]" }
operators['ROT'] = { "code" : "<<<[>>>+<<<-]>[<+>-]>[<+>-]>[<+>-]" }

def stack_ndup(n=1):

    n = int(n)

    # Initialize buffer
    buffer = []

    # First DUP
    buffer.append("<" * n)
    buffer.append("[")
    buffer.append(">" * n)
    buffer.append("+>+")
    buffer.append("<" * (n+1))
    buffer.append("-]")
    buffer.append(">" * (n+1))
    buffer.append("[")
    buffer.append("<" * (n+1))
    buffer.append("+") 
    buffer.append(">" * (n+1))
    buffer.append("-]")

    return ''.join(buffer) * n
operators['NDUP'] = { "callable": stack_ndup, "parameters": 1 }
operators['DUP'] = { "callable": stack_ndup, "parameters": 0 }

# -----------------------------------------------------------------------------
# LOAD_NUM
# -----------------------------------------------------------------------------

def load_num_lineal(n):
    return "+" * n

def load_num_sqrt(n):
    
    # Initialize buffer
    buffer = []

    # Find the closes square root
    r=int(math.sqrt(n))
    if r>=15:
        r=15
    else:
        d=n-r*r
        if 2*(d-r)>3: 
            r+=1
    d=n-r*r

    # Output the square root calculation
    buffer.append(">")
    buffer.append("+" * r)
    buffer.append("[<")
    buffer.append("+" * r)
    buffer.append(">-]")
    buffer.append("<")

    # Output the rest
    if d > 0:
        buffer.append("+" * d)
    elif d < 0:
        buffer.append("-" * -d)

    return ''.join(buffer)    

def load_num_cluster(n, cluster_size = 16):

    # Initialize buffer
    buffer = []

    # Find the closes cluster start
    s = int(n / cluster_size)
    d = n-s*cluster_size
    if 2 * d - cluster_size > 2:
        s += 1
        d = n-s*cluster_size

    # Output the cluster
    buffer.append(">")
    buffer.append("+" * cluster_size)
    buffer.append("[<")
    buffer.append("+" * s)
    buffer.append(">-]")
    buffer.append("<")

    # Output the rest
    if d > 0:
        buffer.append("+" * d)
    elif d < 0:
        buffer.append("-" * -d)
    
    return ''.join(buffer)    

def load_num_cluster_8(n):
    return load_num_cluster(n, 8)

def load_num_cluster_16(n):
    return load_num_cluster(n, 16)

def load_num(n):
    '''
    Calculates the shortest BF code to load a given number
    '''
    n = int(n)
    
    # Start values
    code = None
    min = 1000

    for f in [ 
        load_num_lineal, 
        load_num_sqrt, 
        load_num_cluster_8,
        load_num_cluster_16,
    ]:
        tmp = f(n)
        if len(tmp) < min:
            code = tmp
            min = len(tmp)

    return "%s>" % code
operators['LOAD_NUM'] = { "callable": load_num, "parameters": 1 }

# -----------------------------------------------------------------------------
# PRINT_STR_AND_CLEAN
# -----------------------------------------------------------------------------

def print_str_and_clean_cluster(s, cluster_size = 16):

    # Initialize output buffer
    buffer = []

    # Initial cursor position
    cursor = 0

    # Decode the request string
    characters = [ord(c) for c in s]

    # Calculate the original starting positions:
    positions = []
    for character in characters:
        c = int(character / cluster_size) * cluster_size
        if not c in positions:
            positions.append(c)

    # Sanity gap
    buffer.append(">")
    
    # Load initial data
    buffer.append("+" * cluster_size)
    buffer.append("[")
    for i in range(0, len(positions)):
        buffer.append(">")
        buffer.append("+" * (positions[i] / cluster_size))
    buffer.append("<" * len(positions))
    buffer.append("-]>")

    for character in characters:

        # Find the best cursor position
        pos = 0
        distance = 1000
        for i in range(0, len(positions)):
            d = math.fabs(positions[i]-character)
            if d<=distance:
                distance=d
                pos = i
        
        # Move to that position
        if pos > cursor: 
            buffer.append(">" * (pos-cursor))
        if pos < cursor: 
            buffer.append("<" * (cursor-pos))
        cursor = pos

        # Change the cursor value
        if character > positions[cursor]: 
            buffer.append("+" * (character-positions[cursor]))
        if character < positions[cursor]: 
            buffer.append("-" * (positions[cursor]-character))
        positions[cursor] = character

        # Print it
        buffer.append(".")

    # Move to the end and clean
    buffer.append(">" * (len(positions)-cursor))
    buffer.append(operators['CLEAN']['code'])
    buffer.append("<")
    
    # Return result
    return ''.join(buffer)

def print_str_and_clean(s):
    return print_str_and_clean_cluster(s, 16)
operators['PRINT_STR_AND_CLEAN'] = { "callable": print_str_and_clean, "parameters": 1 }

# -----------------------------------------------------------------------------
# LOAD_STR
# -----------------------------------------------------------------------------

def load_str_cluster(s, cluster_size = 16):

    # Initialize output buffer
    buffer = []

    # Initial cursor position
    cursor = 0

    # Decode the request string
    characters = [ord(c) for c in s]

    # Get the closest cluster start for each character
    multipliers = [int(round(c/cluster_size,0)) for c in characters]

    # Load initial data
    buffer.append("+" * cluster_size)
    buffer.append("[")
    for multiplier in multipliers:
        buffer.append(">")
        buffer.append("+" * multiplier)
    buffer.append("<" * len(characters))
    buffer.append("-]>")

    # Add the rest
    for i in range(0, len(characters)):
        d = characters[i] - multipliers[i] * cluster_size
        if d>0:
            buffer.append("+" * d)
        elif d<0:
            buffer.append("-" * -d) 
        buffer.append(">")
    
    # Return result
    return ''.join(buffer)

def load_str(s):
    '''
    Calculates the shortest BF code to load a given string
    '''
    
    # Start values
    code = None
    min = 1000

    for size in range (8,16,2):
        tmp = load_str_cluster(s, size)
        if len(tmp) < min:
            code = tmp
            min = len(tmp)

    return code
operators['LOAD_STR'] = { "callable": load_str, "parameters": 1 }

# -----------------------------------------------------------------------------
# PRINT FUNTIONS
# -----------------------------------------------------------------------------

operators['LF'] = { "code": "++++++++++.[-]" }
operators['PRINT_CHR'] = { "code": "." }
operators['PRINT_STR'] = { "code": "[.>]" }
operators['PRINT_NUM'] = { "code": "<[>+<-]>[>+++++++++[+<[->-[>+>>]>[+[-<+>]>+>>]<<<<<]>>>[<<<+>>>-]<<[-]>[<+>-]>+<]>[-<]<<[>>+<<-]>[<+>-]>[<+>-]+++++++[<<+++++++>>-]<<->]<[.[-]<]" }

# -----------------------------------------------------------------------------
# READING FUNCTIONS
# -----------------------------------------------------------------------------

operators['READ_CHR'] = { "code": ",>" }
operators['READ_NUM'] = { "code": ">>>+[-<,----------[<<[>++++++++++<-]>>>++++++[<------>-]<--[<+>-]<[<+>-]>>+<]>]<<" }

# =============================================================================
# CONFIGURATION
# =============================================================================

APP_NAME = "BFCG (BrainFuck Code Generator)"
APP_VERSION = "0.1"

# =============================================================================
# MAIN CODE
# =============================================================================

def run(code, debug=False, linewrap=40):

    print code
    cursor = 0
    buffer = []

    if debug:
        title = "%s v%s" % (APP_NAME, APP_VERSION)
        print "=" * len(title)
        print title
        print "=" * len(title)
        print ""

    tokens = shlex.split(argv)
    while len(tokens):

        token = tokens.pop(0)
        parameters=[]

        if token in operators:

            op = operators[token]
            if 'code' in op:
                response = op['code']
            else:
                parameters = []
                for i in range(0, op['parameters']):
                    parameters.append(tokens.pop(0))
                response = op['callable'](*parameters)

        elif token.isdigit():
            response = load_num(int(token))        
            parameters = [token]
            token = "LOAD_NUM"

        else:
            if tokens[0] == "PRINT_STR_AND_CLEAN":
                response = print_str_and_clean(token)
                parameters = [token]
                token = "PRINT_STR_AND_CLEAN"
            else:
                response = load_str(token)
                parameters = [token]
                token = "LOAD_STR"
            if len(tokens) and tokens[0] == token:
                tokens = tokens[1:]

        if debug:
            if len(parameters):
                print "========= %s(%s) ==========" % ( token , ','.join(parameters))
            else:
                print "========= %s ==========" % token
            print
            print response
            print
        else:
            buffer.append(response)

        cursor += (response.count(">") - response.count("<"))

    if not debug:
        optimizations = [ '<>', '><', '+-', '-+', '#' ]
        response = ''.join(buffer)
        for item in optimizations:
            response = response.replace(item, '')
        while len(response):
            print response[:linewrap]
            response = response[linewrap:]    


if __name__ == '__main__':
    '''
    Main entry point
    '''

    run(argv, False, 40)
        
