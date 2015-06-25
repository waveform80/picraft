# NOTE: This file has a different suffix simply to ensure the Makefile doesn't
# try and render it into an image

# This script expects a couple of parameters which define the limits of the
# axes. The first parameter ($0) specifies the "from" value of the range, while
# the second parameter ($1) specifies the "to" value of the range

range_from = $0
range_to = $1
tic_from = $0 + 1
tic_to = $1 - 1

set linetype 1 lw 1 lc rgb "black"
set linetype 2 lw 1 lc rgb "slategray"
set linetype 3 lw 1 lc rgb "gray80"
set xrange [range_from:range_to]
set yrange [range_to:range_from]
set zrange [range_from:range_to]
set xlabel "X" offset first range_to,0,0 textcolor rgb "slategray"
set ylabel "Z" offset first -0.5,range_to,0 textcolor rgb "slategray"
set zlabel "Y" offset first 0.5,0,range_to textcolor rgb "slategray"
set border 0
set xyplane at 0
set xzeroaxis lt 2
set yzeroaxis lt 2
set zzeroaxis lt 2
set tics axis nomirror format ""
set xtics tic_from,1,tic_to
set ytics tic_from,1,tic_to
set ztics tic_from,1,tic_to
set view 60,15,1.3,1.3
set grid
unset key

