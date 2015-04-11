import subprocess
import time


class ChuckConnector(object):
    def __init__(self):
        pass

    def set_freq(self, freq):
        pass

    def start(self):
        pass

    def stop(self):
        pass


def main():
    cc = ChuckConnector()
    cc.start()
    cc.set_freq(440)
    time.sleep(1)    
    cc.stop()


if __name__ == '__main__':
    main()
