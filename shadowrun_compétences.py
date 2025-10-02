def amelioration(initial, temps, karma = 0):
    karma_a_depenser = 0
    rangs = [[0,0]]
    print(rangs[-1][1])
    iterations = 0
    while rangs[-1][0] + rangs[-1][1]< temps:
        print( rangs[-1][0] + rangs[-1][1])
        iterations +=1
        if iterations+initial > 3:
            print("a")
            rangs.append([(iterations+initial)*14+rangs[-1][0], (iterations+initial)*4+rangs[-1][1]])
        elif iterations+initial == 3:
            print("b")
            rangs.append([(iterations+initial)*14+rangs[-1][0], (iterations+initial)*3+rangs[-1][1]])
        elif iterations+initial == 2:
            print("c")
            rangs.append([(iterations+initial)*14+rangs[-1][0], (iterations+initial)*2+rangs[-1][1]])
        elif iterations+initial == 1:
            print("d")
            rangs.append([(iterations+initial)*14+rangs[-1][0], (iterations+initial)*1+rangs[-1][1]])
    return  f'vous passez {(rangs[-1][0] + rangs[-1][1])/7} semaines ({(rangs[-1][0] + rangs[-1][1])} jours pour passer du rang {initial} au rang {initial+iterations})'


print(amelioration(0, 9991, 0))