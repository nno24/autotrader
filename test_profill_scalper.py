import playsound

cash=1000
kurtasje=3.75*2
break_even=(kurtasje/cash)*100

print(break_even)

p1=10.0
p2=10.2

diff=(1 - (p1/p2))*100

if diff >= break_even:
    playsound("just-saying.mp3")
