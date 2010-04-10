#!/usr/bin/env python

"""
This is a Brainfuck interpreter (not a compiler) written in Python. It is
somewhat optimized for speed, as much as that is possible. By default it allows
for 30000 bytes of memory, but this can be configured by passing a parameter. 
 
Some protections are in place in order to keep the program from entering an
infinite loop. There is no recursion in the interpreter, in order to avoid
stack overflows. It also contains a very rudementary debugger which, for each
opcode, prints the current position in the code and the contents of the memory.
"""

import os
import sys
import cStringIO
import time

class BrainfuckError(Exception):          
    def __init__(self, message, errnr):   
        self.errnr = errnr                
        Exception.__init__(self, message) 

class Brainfuck(object):                                  
    """                                                   
    Brainfuck interpreter.                                
                                                          
    Example:                                              
        # Divide                                          
        bf = brainfuck.Brainfuck(                         
            \"""                                          
                ,>,>++++++[-<--------<-------->>]<<[>[->+>
                ]>[-<<-[>]>>>[<[>>>-<<<[-]]>>]<<]>>>+<<[-<
                ]<<<]>[-]>>>>[-<<<<<+>>>>>]<<<<++++++[-<++
                <.                                        
            \""",                                         
            '62')                                         
        out = bf.run()                                    
        print out              # 3                        
    """                                                   
                                                          
    operators = ['+', '-', '>', '<', '[', ']', '.', ',', '#']
 
    def __init__(self, code, input = sys.stdin, output = None):
        """
        Interpret and run Brainfuck code given in 'code'. Brainfuck program
        will read from input which can be either an open filehandle (default
        stdin) or a string. Will write to output. If output is None (default),
        the run() function will return the output instead.
        """
        if type(input) == type(''):
            self.input = cStringIO.StringIO(input)
        else:
            self.input = input

        if output == None:
            self.return_output = True
            self.output = cStringIO.StringIO()
        else:
            self.return_output = False
            self.output = output

        # First simple syntax checking
        if code.count('[') != code.count(']'):
            raise BrainfuckError('Unmatched number of brackets', 1)
 
        # Remove non-brainfuck operators so the interpreter doesn't have to
        # process them.
        code = ''.join([op for op in code if op in self.operators])

        # Find matching brackets
        jumps = {}
        code_len = len(code)
        stack = []
        for ip in range(0, code_len):
            if code[ip] == '[':
                stack.append(ip)
            elif code[ip] == ']':
                if len(stack) == 0:
                    raise BrainfuckError('Unmatched bracket at position %i' % ip, 4)
                sip = stack.pop()
                jumps[sip] = ip
                jumps[ip] = sip
        if len(stack):
            raise BrainfuckError('Unmatched bracket at position %i' % stack.pop(), 4)

        # Copy references
        self.code = code
        self.code_len = code_len
        self.jumps = jumps

    def run(self, mem_size = 30000, max_op = 1000000, debug=False):
        """
        Run the brainfuck code with a maximum number of instructions of
        max_op (to counter infinite loops). If self.output is None, it
        returns the output instead of directly writing to the file descriptor.
        If debug is set to True, the interpreter will output debugging
        information during execution.
        """

        # Copy self references for speed.
        code = self.code
        input = self.input
        output = self.output
        jumps = self.jumps
        code_len = self.code_len
 
        ic = 0                      # Instruction counter against infinite loops
        mem = [0] * mem_size        # Memory
        buffer = []                 # Output buffer for tiny speed increase
        ip = 0                      # Instruction pointer (current excecute place in code)
        dp = 0                      # Data pointer (current read/write place in mem)
        m_dp = 0                    # Maximum Data Pointer (largest memory index access by code)
 
        while ip < code_len:

            if ic > max_op:
                raise BrainfuckError('Maximum number of instructions exceeded', 2)
 
            op = code[ip]
 
            if op == '+':
                mem[dp] += 1
            elif op == '-':
                mem[dp] -= 1
            elif op == '>': 
                dp += 1
                if dp > m_dp:
                    m_dp = dp
            elif op == '<': 
                dp -= 1
                if dp > m_dp:
                    m_dp = dp
            elif op == '[':
                if mem[dp] == 0:
                    ip = jumps[ip]
            elif op == ']':
                if mem[dp] != 0:
                    ip = jumps[ip]
            elif op == '.':
                buffer.append(chr(mem[dp] % 256))
            elif op == ',':
                try:
                    mem[dp] = ord(input.read(1))
                except:
                    mem[dp] = -1
            elif op == '#':
                mem_ord = ['%3i ' % v for v in mem[:m_dp+1]]
                mem_chr = [chr(v % 256) for v in mem[:m_dp+1]]
                mem_ord[dp] = mem_ord[dp][0:3] + '*'
                print mem_ord
 
            ip += 1
            ic += 1
 
            if debug:
                sys.stdout.write(code + '    ')
                for i in range(m_dp + 1):
                    sys.stdout.write("%03i " % (mem[i]) )
                sys.stdout.write("{%i} " % ic )
                sys.stdout.write('\n')
                print ' ' * ip + '^' + ' ' * (code_len - ip) + '   ' + '    ' * dp + '^^^'
                sys.stdout.write('\n')
 
        output.write(''.join(buffer))
        if self.return_output:
            output.seek(0)
            return(output.read())


if __name__ == '__main__':
    '''
    Main entry point
    '''

    import getopt

    debug = False
    code = None
    
    try:                                
        opts, args = getopt.getopt(sys.argv[1:], "hds:", ["help", "debug", "source="])
    except getopt.GetoptError:
        print "Wrong parameters."
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print "Help! I need somebody"
            sys.exit()
        elif opt in ('-s', '--source'):
            if not os.path.exists(arg):
                print "File '%s' does not exist" % arg
                sys.exit(2)
            f = open(arg, 'r')
            code = f.read()
            f.close()
        elif opt in ('-d', '--debug'):
            debug = True

    if len(args):
        code = args[0]

    if not code:
        print "No code!"
        sys.exit(2)
    
    output = Brainfuck(code).run(debug=debug)
    print output

