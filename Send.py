import curses
import datetime
import os
import shlex
import subprocess
import sys
import time


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


def main(screen, argv):
    cc = ChuckConnector(0.15) # 0.02 is good
    u_in = None

    if screen:
        screen.nodelay(True)

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
    # curses.wrapper(main)
    main(None, sys.argv)
