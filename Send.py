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


def print_title(scr):
    size_yz = scr.getmaxyx()
    x_max = size_yz[1]
    y_max = size_yz[0]
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

def print_menu(scr, opts, x, y):
    scr.addstr(y, x, 'Menu')
    for d, o in enumerate(opts, 1):
        s = '{i}: {m}'.format(i=d, m=o)
        scr.addstr(d + y, x, s)
    scr.refresh()

def get_input(scr, y, x, s):
    curses.echo()
    curses.curs_set(1)
    scr.addstr(y, x, s)
    scr.refresh()
    u_in = scr.getstr(y + 1, x, 38)
    curses.noecho()
    curses.curs_set(0)
    return u_in


def main(screen, argv):
    cc = ChuckConnector(0.02) # 0.02 is good
    u_in = None
    screen.keypad(True)
    curses.curs_set(0)

    if screen:
        while True:
            screen.clear()
            options = ['Message', 'File', 'Exit']
            print_menu(screen, options, 2, 2)
            print_title(screen)
            c = screen.getch()
            if c == ord('1'):
                while True:
                    screen.clear()
                    print_title(screen)
                    u_in = get_input(screen, 2, 2, 'Enter Message:')
                    screen.addstr(4, 2, 'Sending message...')
                    screen.refresh()

                    start = datetime.datetime.now()
                    cc.send_bit(0)
                    cc.send_string(u_in)
                    delta = datetime.datetime.now() - start
                    s = 'Complete. time: {s}'.format(s=str(delta))
                    screen.addstr(5, 2, s)
                    screen.addstr(7, 2, 'Press "m" to send another message.')
                    screen.addstr(8, 2, 'Any other key returns to menu.')
                    screen.refresh()
                    c = screen.getch()

                    if c != ord('m'):
                        break

            elif c == ord('2'):
                screen.clear()
                print_title(screen)
                fn = get_input(screen, 2, 2, 'Enter Filename:')

                if not os.path.exists(fn):
                    raise RuntimeError('file does not exist')

                f = open(fn)
                data = f.read()
                s = 'Sending file: {fn} ({fs} bytes)'.format(fn=fn, fs=len(data))
                screen.addstr(4, 2, s)
                screen.refresh()
                start = datetime.datetime.now()
                cc.send_bit(1)
                cc.send_string(data + '\0')
                delta = datetime.datetime.now() - start
                s = 'Complete. time: {s}'.format(s=str(delta))
                screen.addstr(5, 2, s)
                screen.addstr(7, 2, 'Press any key to continue...')
                screen.refresh()
                screen.getch()

            elif c == ord('3') or c == ord('q'):
                cc.stop()
                break
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
                cc.send_bit(0)
                cc.send_string(u_in)
                delta = datetime.datetime.now() - start
                s = 'complete. time: {s}'.format(s=str(delta))
                print s

    cc.stop()


if __name__ == '__main__':
    curses.wrapper(main, sys.argv)
    # main(None, sys.argv)
