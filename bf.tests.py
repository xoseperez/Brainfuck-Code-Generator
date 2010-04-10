#!/usr/bin/env python

from xbf import Brainfuck

tests = (
    ('helloworld', '++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.', '', 'Hello World!\n'),
    ('divide1', ',>,>++++++[-<--------<-------->>]<<[>[->+>+<<]>[-<<-[>]>>>[<[>>>-<<<[-]]>>]<<]>>>+<<[-<<+>>]<<<]>[-]>>>>[-<<<<<+>>>>>]<<<<++++++[-<++++++++>]<.', '62', '3'),
    ('divide2', ',>,>++++++[-<--------<-------->>]<<[>[->+>+<<]>[-<<-[>]>>>[<[>>>-<<<[-]]>>]<<]>>>+<<[-<<+>>]<<<]>[-]>>>>[-<<<<<+>>>>>]<<<<++++++[-<++++++++>]<.', '92', '4'),
)

for test in tests:
    output = Brainfuck(test[1], test[2]).run(debug=False)
    if output != test[3]:
        print "Test %-20s: Failed. Output = %s" % ('\''+test[0]+'\'', output)
    else:
        print "Test %-20s: Success" % ('\''+test[0]+'\'')




