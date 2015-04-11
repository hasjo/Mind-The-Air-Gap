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

    while True:
        stdscr.refresh()
        #Do things
        
        while p.poll() is None:
            output = p.stdout.readline()
            if "Spacer" in output:
                #print ''
                pass

wrapper(main)
