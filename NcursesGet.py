import subprocess
import curses
from curses import wrapper

def ClearByte():
        return [-1,-1,-1,-1,-1,-1,-1,-1]

def PrintTitle(stdscr,Xmax):
    Title = "Ultras0nic Air-Gap Bridger"
    Xloc = (Xmax/2) - (len(Title)/2)
    stdscr.addstr(1,Xloc,Title)

def main(stdscr):
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(False)
    stdscr.nodelay(True)
    ScreenSize = stdscr.getmaxyx()
    Ymax = ScreenSize[0]
    Xmax = ScreenSize[1]
    stdscr.border()
    PrintTitle(stdscr,Xmax)

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
    MessageY = 2

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

                if float(NewOutList[1]) > .0020:
                    FreqList.insert(0,int(NewOutList[0]))
                    FreqList.pop()
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
                            stdscr.addstr( 2, (Xmax/2)-4, ByteString)
                            stdscr.addch(MessageY, MessageX, BinChar)
                            MessageX += 1
                            if MessageX == Xmax-2:
                                MessageY += 1
                                MessageX == 2
                            stdscr.refresh()
                            CurrentByte = ClearByte()
                            ByteString = ""
wrapper(main)
