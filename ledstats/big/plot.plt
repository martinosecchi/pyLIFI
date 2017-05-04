set term pngcairo
set out "warmup2.png"
set title "LED bulb AC warmup times"
set yrange[-10:110]
set xrange [-10:80]
set ylabel "brigthnes [%]"
set xlabel "time [ms]"
set grid x2tics
set x2tics 10 format "" scale 0
set arrow from -10,100 to 60,100 nohead lw 1 lt rgb "gray"
set arrow from -10,0 to 80,0 nohead lw 1 lt rgb "gray"
plot "xup1.txt" w linespoints title "1" pt 12,"xup2.txt" w linespoints title "2" pt 12,"xup3.txt" w linespoints title "3" pt 12,"xup4.txt" w linespoints title "4" pt 12,"xup5.txt"  w linespoints title "5" pt 12 lt rgb "blue"

set term pngcairo
set out "warmdown2.png"
set title "LED colldown times"
set yrange[-10:110]
set xrange [-10:200]
set ylabel "brigthnes [%]"
set xlabel "time [ms]"
set grid x2tics
set x2tics 10 format "" scale 0
set arrow from -10,100 to 60,100 nohead lw 1 lt rgb "gray"
set arrow from -10,0 to 150,0 nohead lw 1 lt rgb "gray"
plot "xdown1.txt" w linespoints title "1" pt 12,"xdown2.txt" w linespoints title "2" pt 12,"xdown3.txt" w linespoints title "3" pt 12,"xdown4.txt" w linespoints title "4" pt 12,"xdown5.txt"  w linespoints title "5" pt 12 lt rgb "blue"