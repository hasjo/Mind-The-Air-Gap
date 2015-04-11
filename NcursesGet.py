import curses
from curses import wrapper

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
    while True:
        stdscr.refresh()
        #Do things
        

wrapper(main)
