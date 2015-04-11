import subprocess

p = subprocess.Popen('chuck chuck_files/FFT.ck 2>&1 > /dev/null', shell=True, stdout = subprocess.PIPE,)

CurrentFreq = 0
FreqList = [1,2,3,4]
JustCaught = 0
streak = False
while p.poll() is None:
    output = p.stdout.readline()
    if "Spacer" in output:
#        print ''
         pass

    else:
        NewOut = output.strip().replace('.000000','')
        NewOut = NewOut.replace(')','').replace('%(','').replace(',',' ').replace('*pi','')
        NewOutList = NewOut.split()
#        print NewOutList[1]

        if float(NewOutList[1]) > .0020:
            FreqList.insert(0,int(NewOutList[0]))
            FreqList.pop()
            streak = FreqList.count(FreqList[0]) == len(FreqList)
            if streak:
                if JustCaught != NewOutList[0]:
                    print "Caught " + str(JustCaught)
                JustCaught = NewOutList[0]
