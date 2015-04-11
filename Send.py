import shlex
import subprocess
import time


class ChuckConnector(object):
    def __init__(self, interval):
        chuck_command = shlex.split('chuck --loop')
        self.chuck_process = subprocess.Popen(chuck_command)
        self.interval = interval
        time.sleep(1)

    def _clear_chuck(self):
        cmd = 'chuck - 1'
        subprocess.call(shlex.split(cmd))

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
        print freq
        self._clear_chuck()
        cmd = 'chuck + chuck_files/{fn}'

        if freq == 0:
            print 'setting low'
            cmd = cmd.format(fn='sin_low.ck')
        elif freq == 1:
            print 'setting high'
            cmd = cmd.format(fn='sin_high.ck')
        else:
            print 'setting start'
            cmd = cmd.format(fn='sin_start.ck')
        print 'chuck command: ' + cmd
        subprocess.call(shlex.split(cmd))

    def send_string(self, s):
        s_bytes = list(ord(b) for b in s)
        for byte in s_bytes:
            for i in xrange(8):
                send_bit((b >> i) & 1)

    def stop(self):
        self._clear_chuck()
        self.chuck_process.kill()


def main():
    cc = ChuckConnector(.1)
    bits = [0, 1, 0, 1, 0, 1, 0, 1]
    cc.send_bits(bits, .5)
    cc.stop()


if __name__ == '__main__':
    main()
