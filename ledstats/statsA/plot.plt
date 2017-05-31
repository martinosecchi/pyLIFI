set term pngcairo dashed
set out "transmission.png"
set title "Transmission of message: \"a\"\nLocal maximums"
set yrange[-10:110]
set xrange [-10:222]
set ylabel "brigthnes [%]"
set xlabel "time [ms]"
set grid x2tics
set x2tics 10 format "" scale 0

set encoding utf8 

# set arrow from -10,65.2 to 150,65.2 nohead lt 1 lw 2 lc rgb "red"
# set arrow from -10,57.4 to 150,57.4 nohead lt 1 lw 2 lc rgb "orange"
# set arrow from -10,73 to 150,73 nohead lt 1 lw 2 lc rgb "orange"
# set arrow from -10,80.7 to 150,80.7 nohead lt 1 lw 2 lc rgb "green"
# set arrow from -10,49.7 to 150,49.7 nohead lt 1 lw 2 lc rgb "green"

plot \
"xA1.txt" w linespoints title "1" pt 12, \
"xA2.txt" w linespoints title "2" pt 12,\
"xA3.txt" w linespoints title "3" pt 12,\
"xA4.txt" w linespoints title "4" pt 12,\
"xA5.txt"  w linespoints title "5" pt 12 lt rgb "blue"

#-100 title "avg peak" lt rgb "red", \
#-100 title "μ ± σ" lt rgb "orange", \
#-100 title "μ ± 2σ" lt rgb "green"

# "xA6.txt" w linespoints title "6" pt 12,\
# "xA7.txt" w linespoints title "7" pt 12,\
# "xA8.txt" w linespoints title "8" pt 12,\
# "xA9.txt" w linespoints title "9" pt 12,\

set xrange[-10:110]
set yrange[-10:60]
unset arrow

set out "hist1.png"
set title "Distribution of brightness levels for 1s"
set xlabel "brigthness [%]"
set ylabel "frequency [%]"
set arrow from 64.6,-5 to 65.2,50 nohead lt 1 lw 1 lc rgb "red"
set arrow from 56.9,-5 to 56.9,50 nohead lt 1 lw 1 lc rgb "orange"
set arrow from 72.3,-5 to 72.3,50 nohead lt 1 lw 1 lc rgb "orange"
set arrow from 80.0,-5 to 80.0,50 nohead lt 1 lw 1 lc rgb "green"
set arrow from 49.2,-5 to 49.2,50 nohead lt 1 lw 1 lc rgb "green"
plot "hist1.txt" w boxes notitle, \
-100 title "avg peak" lt rgb "red", \
-100 title "μ ± σ" lt rgb "orange", \
-100 title "μ ± 2σ" lt rgb "green"

unset arrow
set out "hist0.png"
set title "Distribution of brightness levels for 0s"
set xlabel "brigthness [%]"
set ylabel "frequency [%]"
set arrow from 33.5,-5 to 33.5,50 nohead lt 1 lw 1 lc rgb "red"
set arrow from 21.3,-5 to 21.3,50 nohead lt 1 lw 1 lc rgb "orange"
set arrow from 45.6,-5 to 45.6,50 nohead lt 1 lw 1 lc rgb "orange"
set arrow from 57.6,-5 to 57.6,50 nohead lt 1 lw 1 lc rgb "green"
set arrow from 09.2,-5 to 09.2,50 nohead lt 1 lw 1 lc rgb "green"
plot "hist0.txt" w boxes notitle, \
-100 title "avg peak" lt rgb "red", \
-100 title "μ ± σ" lt rgb "orange", \
-100 title "μ ± 2σ" lt rgb "green"