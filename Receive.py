import subprocess

p = subprocess.Popen('chuck chuck_files/FFT.ck 2>&1 > /dev/null', shell=True, stdout = subprocess.PIPE,)

CurrentFreq = 0
FreqList = [1,2,3,4]
CurrentByte = [-1,-1,-1,-1,-1,-1,-1,-1]
ByteString = ""
JustCaught = 0
streak = False
PrintBit = False
StartBit = False

def ClearByte():
    return [-1,-1,-1,-1,-1,-1,-1,-1]


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
                    PrintBit = True
                    #print 'Caught ' + NewOutList[0]
                JustCaught = NewOutList[0]

            if PrintBit:
                if JustCaught == "19125":
                    StartBit = True
                    PrintBit = False
                    #print 'Start'
                elif JustCaught == "19500" and StartBit:
                    PrintBit = False
                    StartBit = False
                    CurrentByte.insert(0,0)
                    CurrentByte.pop()
                    #print CurrentByte
                elif JustCaught == "19875" and StartBit:
                    PrintBit = False
                    StartBit = False
                    CurrentByte.insert(0,1)
                    CurrentByte.pop()
                    #print CurrentByte

                if CurrentByte.count(-1) == 0:
                    #CurrentByte.reverse()
                    #print CurrentByte
                    for x in CurrentByte:
                        ByteString += str(x)
                    #print ByteString
                    print chr(int(ByteString,2))
                   # ByteString = ByteString.decode("binary")
                    CurrentByte = ClearByte()
                    ByteString = ""

