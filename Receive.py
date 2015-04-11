import subprocess

p = subprocess.Popen('chuck chuck_files/FFT.ck 2>&1 > /dev/null', shell=True, stdout = subprocess.PIPE,)

while p.poll() is None:
    output = p.stdout.readline()
    if "Spacer" in output:
        print ''
    else:
        print output.strip().replace('.000000','')
