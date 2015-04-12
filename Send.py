import curses
import datetime
import locale
import os
import shlex
import subprocess
import sys
import time


locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


class ChuckConnector(object):
    def __init__(self, interval):
        self.interval = interval
        self._start_chuck()
        time.sleep(1)

    def _clear_chuck(self):
        cmd = 'chuck - 1'
        subprocess.call(shlex.split(cmd))

    def _start_chuck(self):
        chuck_command = shlex.split('chuck --loop')
        self.chuck_process = subprocess.Popen(
            chuck_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def send_bits(self, bits, interval):
        for b in bits:
            self.set_freq(-1)
            time.sleep(self.interval)
            self.set_freq(b)
            time.sleep(self.interval)

    def send_bit(self, bit):
        self.set_freq(-1)
        time.sleep(self.interval)
        self.set_freq(bit)
        time.sleep(self.interval)

    def set_freq(self, freq):
        self._clear_chuck()
        cmd = 'chuck + chuck_files/{fn}'

        if freq == 0:
            cmd = cmd.format(fn='sin_low.ck')
        elif freq == 1:
            cmd = cmd.format(fn='sin_high.ck')
        else:
            cmd = cmd.format(fn='sin_start.ck')
        subprocess.Popen(shlex.split(cmd))

    def send_freq(self, freq, t):
        self.set_freq(freq)
        time.sleep(t)
        self._clear_chuck()

    def send_string(self, s):
        s_bytes = list(ord(b) for b in s)
        for byte in s_bytes:
            for i in xrange(8):
                b = (byte >> i) & 1
                self.send_bit(b)

        self._clear_chuck()
        self.chuck_process.kill()
        self._start_chuck()

    def stop(self):
        self._clear_chuck()
        self.chuck_process.kill()


def print_title(scr, x_max, y_max):
    bottom = 5
    title = 'Ultrasonic Air-Gap Sender'
    title_loc = (x_max/2) - (len(title)/2)
    scr.addstr(1, title_loc, title)

    scr.border()
    scr.addstr(y_max - bottom, x_max - 1, u'\u2524'.encode(code))
    scr.addstr(y_max - bottom, 0, u'\u251c'.encode(code))
    for x in range(1, x_max - 1):
        scr.addstr(y_max - bottom, x, u'\u2500'.encode(code))

    scr.addstr(y_max - bottom+1,2,"19125:")
    scr.addstr(y_max - bottom+2,2,"19500:")
    scr.addstr(y_max - bottom+3,2,"19875:")
    scr.refresh()


def main(screen, argv):
    cc = ChuckConnector(0.02) # 0.02 is good
    u_in = None

    if screen:
        screen.keypad(True)

        options = ['Message', 'File', 'Exit']
        screen.addstr(2, 2, 'Menu')
        for y, o in enumerate(options, 1):
            s = '{i}: {m}'.format(i=y, m=o)
            screen.addstr(y + 2, 2, s)
        size_yz = screen.getmaxyx()
        print_title(screen, size_yz[1], size_yz[0])
        screen.refresh()
        c = screen.getch()
        if c == 1:
            pass
        elif c == 2:
            pass
        elif c == 3:
            pass
        else:
            pass



    else:
        if len(argv) == 2:
            fn = argv[1]

            if not os.path.exists(fn):
                raise RuntimeError('file does not exist')

            f = open(fn)
            data = f.read()
            print 'sending file: ' + fn
            print 'file contents:'
            print data
            start = datetime.datetime.now()
            cc.send_bit(1)
            cc.send_string(data + '\0')
            delta = datetime.datetime.now() - start
            s = 'complete. time: {s}'.format(s=str(delta))
            print s

        else:
            while not u_in == 'quit':
                u_in = raw_input('Message: ') + '\0'
                print 'sending...'
                start = datetime.datetime.now()
                # PUT THIS BACK IN
                # cc.send_bit(0)
                cc.send_string(u_in)
                delta = datetime.datetime.now() - start
                s = 'complete. time: {s}'.format(s=str(delta))
                print s

    cc.stop()


if __name__ == '__main__':
    curses.wrapper(main, sys.argv)
    # main(None, sys.argv)
