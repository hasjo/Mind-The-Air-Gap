SinOsc s => Gain g => dac;

1 => g.gain;
19850 => s.freq;

while (true) {
    1::second => now;
}
