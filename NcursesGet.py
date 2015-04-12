import subprocess
import locale
import curses
import datetime
from curses import wrapper
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

def ClearByte():
        return [-1,-1,-1,-1,-1,-1,-1,-1]

def PrintTitle(stdscr,Xmax, Ymax):
    BottomHeight = 5
    Title = "Ultras0nic Air-Gap Receiver"
    Xloc = (Xmax/2) - (len(Title)/2)
    stdscr.addstr(1,Xloc,Title)
    stdscr.border()
    stdscr.addstr(Ymax-BottomHeight,Xmax-1,u'\u2524'.encode(code))
    stdscr.addstr(Ymax-BottomHeight,0,u'\u251c'.encode(code))
    for x in range(1,Xmax-1):
        stdscr.addstr(Ymax-BottomHeight,x,u'\u2500'.encode(code))
    stdscr.addstr(Ymax-BottomHeight+1,2,"19125:")
    stdscr.addstr(Ymax-BottomHeight+2,2,"19500:")
    stdscr.addstr(Ymax-BottomHeight+3,2,"19875:")
    stdscr.refresh()


def main(stdscr):
    stdscr = curses.initscr()
    curses.curs_set(False)
    stdscr.nodelay(True)
    ScreenSize = stdscr.getmaxyx()
    Ymax = ScreenSize[0]
    Xmax = ScreenSize[1]
    PrintTitle(stdscr,Xmax, Ymax)

    # Starting Freq Analysis Stuff
    p = subprocess.Popen('chuck chuck_files/FFT.ck 2>&1 > /dev/null', 
            shell=True, stdout = subprocess.PIPE,)
    CurrentFreq = 0
    FreqList = [1,2,3,4]
    CurrentByte = [-1,-1,-1,-1,-1,-1,-1,-1]
    ByteString = ""
    JustCaught = 0
    streak = False
    PrintBit = False
    StartBit = False
    MessageX = 2
    MessageY = 3
    TimeStamp = datetime.datetime.now() - datetime.timedelta(seconds = 2)
    MessageCounter = 0
    InfoBit = False
    BitType = -1
    FileOpen = False
    OpenedFile = 0

    while True:
        stdscr.refresh()
        #Do things
        
        while p.poll() is None:
            output = p.stdout.readline()
            if "Spacer" in output:
                #print ''
                pass
            else:
                NewOut = output.strip().replace('.000000','')
                NewOut = NewOut.replace(')','').replace('%(','').replace(',',' ').replace('*pi','')
                NewOutList = NewOut.split()
                #print NewOutList[1]
                if NewOutList[0] == "19125":
                    #clear the row
                    #draw new row 
                    stdscr.move(Ymax-4,8)
                    stdscr.clrtoeol()
                    stdscr.addstr(Ymax-4,Xmax-1,u'\u2502'.encode(code))
                    Range = Xmax-11
                    ToFill = Range * (float(NewOutList[1])*10)
                    if ToFill > Range :
                        ToFill = Range
                    for x in range (8, int(ToFill)+8):
                        stdscr.addstr(Ymax-4,x,u'\u2588'.encode(code))
                    stdscr.refresh()
                
                if NewOutList[0] == "19500":
                    #clear the row
                    #draw new row 
                    stdscr.move(Ymax-3,8)
                    stdscr.clrtoeol()
                    stdscr.addstr(Ymax-3,Xmax-1,u'\u2502'.encode(code))
                    Range = Xmax-11
                    ToFill = Range * (float(NewOutList[1])*10)
                    if ToFill > Range :
                        ToFill = Range
                    for x in range (8, int(ToFill)+8):
                        stdscr.addstr(Ymax-3,x,u'\u2588'.encode(code))
                    stdscr.refresh()
                
                if NewOutList[0] == "19875":
                    #clear the row
                    #draw new row 
                    stdscr.move(Ymax-2,8)
                    stdscr.clrtoeol()
                    stdscr.addstr(Ymax-2,Xmax-1,u'\u2502'.encode(code))
                    Range = Xmax-11
                    ToFill = Range * (float(NewOutList[1])*10)
                    if ToFill > Range :
                        ToFill = Range
                    for x in range (8, int(ToFill)+8):
                        stdscr.addstr(Ymax-2,x,u'\u2588'.encode(code))
                    stdscr.refresh()

                if float(NewOutList[1]) > .0020:
                    #check current time
                    #compare to previous time
                    #clear buff if greater than X seconds
                    Now = datetime.datetime.now()
                    NowDelta = Now - TimeStamp
                    if NowDelta.seconds > 1:
                        ByteString = ""
                        CurrentByte = ClearByte()
                    TimeStamp = Now

                    FreqList.insert(0,int(NewOutList[0]))
                    FreqList.pop()

                    if CurrentByte.count(-1) == 7 and not InfoBit:
                        BitType = CurrentByte[0]
                        CurrentByte = ClearByte()
                        InfoBit = True
                        if BitType == 1 and not FileOpen:
                            OpenedFile = open("out",'w')
                            #stdscr.addch(1,1,'-')

                    streak = FreqList.count(FreqList[0]) == len(FreqList)
                    if streak:
                        if JustCaught != NewOutList[0]:
                            PrintBit = True
                        JustCaught = NewOutList[0]
                    if PrintBit:
                        if JustCaught == "19125":
                            StartBit = True
                            PrintBit = False
                        elif JustCaught == "19500" and StartBit:
                            PrintBit = False
                            StartBit = False
                            CurrentByte.insert(0,0)
                            CurrentByte.pop()
                        elif JustCaught == "19875" and StartBit:
                            PrintBit = False
                            StartBit = False
                            CurrentByte.insert(0,1)
                            CurrentByte.pop()
                        
                        if CurrentByte.count(-1) == 0:
                            for x in CurrentByte:
                                ByteString += str(x)
                            BinChar = chr(int(ByteString,2))
                            if BinChar == '\0':
                                if BitType == 0:
                                    MessageY += 1
                                    MessageX = 2
                                    InfoBit = False
                                    BitType = -1
                                else:
                                    #stdscr.addch(1,1,'$')
                                    stdscr.refresh()
                                    if OpenedFile:
                                        OpenedFile.close()
                                        OpenedFile = 0
                                        #stdscr.addch(1,1,'+')
                                        stdscr.refresh()
                                    InfoBit = False
                                    BitType = -1
                            else:
                                stdscr.addstr( 2, (Xmax/2)-4, ByteString)
                                if BitType == 0:
                                   stdscr.addch(MessageY, MessageX, BinChar)
                                if BitType == 1:
                                    OpenedFile.write(BinChar)
                                MessageX += 1
                            if MessageX == Xmax-2:
                                MessageY += 1
                                MessageX = 2
                            stdscr.refresh()
                            CurrentByte = ClearByte()
                            ByteString = ""

wrapper(main)
