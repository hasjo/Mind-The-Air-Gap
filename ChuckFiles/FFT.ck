//Get the FFT

//Input
adc => FFT fft => blackhole; 

//Set the sample rate
second / samp => float samplingRate;

//Set the bin size
100 => fft.size;

//Get the first half of the spectrum
complex spectral[fft.size()/2];

//Begin reading data
while ( true ){
    //Grab the sample amount
    fft.size()::samp => now;

    //Calculate the transform
    fft.upchuck();

    //Get the spectral data
    fft.spectrum( spectral );

    //Display spectral data
    for ( 0 => int i; i < fft.size()/2; i++){
        i * samplingRate / fft.size() => float freq;
        if (freq > 19000){
            if (freq < 20000){
                <<< freq, spectral[i]$polar >>>;
            }
        }
    }
    <<< "Spacer" >>>;
}
