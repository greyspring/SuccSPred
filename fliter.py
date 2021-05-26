def fileFilter(input, output):
    f = open(input, 'r')
    names = []
    data = []
    idx = 0
    for line in f:
        if (line.startswith('>')):
            line = line.split('\n')[0]
            line = line[1:len(line)]
            names.append(line)
        else:
            idx += 1
            line = line.replace(" ", "")
            line = line.split('\n')[0]
            if (len(line) == 21):
                if(line[10:11] == 'K'):
                    n = names.pop()
                    n += '[11]'
                    names.append(n)
                    data.append(line)
                else:
                    names.pop()
            elif (len(line) > 21):
                arr = []
                p = names.pop()
                for i in range(0,len(line)-20):
                    a = line[i:i+21]
                    print(a[10:11])
                    if(a[10:11] == 'K'):
                        b = []
                        b.append(i+11)
                        b.append(a)
                        arr.append(b)
                for one in arr:
                    print(one)
                    xl = p
                    xl+='['+str(one[0])+']'
                    print(xl)
                    names.append(xl)
                    data.append(one[1])
            else:
                names.pop()
    f.close()
    if (len(names) == len(data)):
        f1 = open(output, 'w')
        for i in range(0, len(names)):
            f1.writelines('>' + names[i] + '\n')
            f1.writelines(data[i] + '\n')
        f1.close()
        print('filter success')
    else:
        print('fliter error')