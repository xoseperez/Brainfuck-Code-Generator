p0 will have partial results
p1 will have *10 partial results
p2 will be entry point for new chars
p3 will have temporary flags for loop control

Move to entry point

{0} >>

Set flag on to get into the loop-while structure

{2} >+[-<

Get input from user

{2} ,

Substract 10 to check if it's a new line (so end of input)

{2} ----------

If not get into the loop that adds input to partial result

{2} [

Move to partial result position

{2} <<

Multiply previous partial result * 10 into p1

{0} [>++++++++++<-]

Move back to p2

{0} >>

Substract 38 from input (so p2v=input\10\38) using p3 as temporary buffer

{2} >++++++[<------>-]<--

Add input to temporary result (p1v/=p2v)

{2} [<+>-]

Move partial result back to p1 (p1v=p2v)

{2} <[<+>-]>

Set loop flag on to keep on reading characters (p3v1)

{2} >+<

]>]

Move pointer back to next to last position (p1)

<<

#
