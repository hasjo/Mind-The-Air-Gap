package com.ultras0nic.mindtheairgap;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import com.ultras0nic.fft.Complex;
import com.ultras0nic.fft.RealDoubleFFT;

import org.jtransforms.fft.DoubleFFT_1D;

import java.util.ArrayList;
import java.util.Arrays;


/**
 * A placeholder fragment containing a simple view.
 */
public class TransferFragment extends android.support.v4.app.Fragment {

    private int frequency = 44100;
    private int channelConfiguration = AudioFormat.CHANNEL_IN_MONO;
    private int audioEncoding = AudioFormat.ENCODING_PCM_16BIT;
    private int blockSize = 512;

    static final int HEIGHT = 400;
    static final int WIDTH = 1024;


    private Button mButton;
    private boolean started = false;

    private RecordAudio recordTask;

    private TextView textView;
    private ImageView imageView;
    private Bitmap bitmap;
    private Canvas canvas;
    private Paint paint;


    //Data variables used when handling sample processing
    ArrayList<Character> transmissionBuffer = new ArrayList<Character>(Arrays.asList('n', 'n','n', 'n'));
    Character currentCharacter = 'n';
    boolean readyForBit = false;
    char[] fakeByte = new char[8];
    int fakeByteIndex = 0;

    //2048:888,906,923
    //512:222,226,231
    //256:111,113,115
    //128:55,57,58
    private int STARTINDEX = 222;
    private int ZEROINDEX = 226;
    private int ONEINDEX = 231;


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        //Get the current fragment context
        View rootView = inflater.inflate(R.layout.transfer_fragment, container, false);
        mButton = (Button)rootView.findViewById(R.id.button);

        //Display some ugly text representation of data
        textView = (TextView)rootView.findViewById(R.id.TEXT_STATUS_ID);

        //Do some crazy things to make a graphical output
        imageView = (ImageView) rootView.findViewById(R.id.imageView);
        bitmap = Bitmap.createBitmap((int) WIDTH, (int) HEIGHT,
                Bitmap.Config.ARGB_8888);
        canvas = new Canvas(bitmap);
        paint = new Paint();
        paint.setColor(Color.GREEN);
        //paint.setStrokeWidth(4);
        imageView.setImageBitmap(bitmap);

        //Attach listener to fire listening events
        mButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (started) {
                    started = false;
                    mButton.setText("Start");
                    recordTask.cancel(true);
                    //Reinitialize processing variables
                    textView.setText("");
                    transmissionBuffer = new ArrayList<Character>(Arrays.asList('n', 'n','n', 'n'));
                    currentCharacter = 'n';
                    readyForBit = false;
                    fakeByte = new char[8];
                    fakeByteIndex = 0;
                } else {
                    started = true;
                    mButton.setText("Stop");
                    recordTask = new RecordAudio();
                    recordTask.execute();
                }
            }
        });
        return rootView;
    }

    //Handles creation of audio recorder and reading of data
    private class RecordAudio extends AsyncTask<Void, double[], Void> {
        @Override
        protected Void doInBackground(Void... params) {
            try {
                //Set up audio recorder
                int bufferSize = AudioRecord.getMinBufferSize(frequency,
                        channelConfiguration, audioEncoding);
                AudioRecord audioRecord = new AudioRecord(
                        MediaRecorder.AudioSource.DEFAULT, frequency,
                        channelConfiguration, audioEncoding, bufferSize);

                //Buffer for audiorecorder and input for fft
                short[] buffer = new short[blockSize];
                double[] toTransform = new double[blockSize*2];
                DoubleFFT_1D transform = new DoubleFFT_1D(blockSize);

                audioRecord.startRecording();
                while (started) {
                    //Get the desired number of samples (blockSize)
                    int bufferReadResult = audioRecord.read(buffer, 0, blockSize);

                    for (int i = 0; i < blockSize; i++) {
                        //toTransform[i] = (double) buffer[i] / 32768.0; // signed 16 bit
                        toTransform[2*i] = (double) buffer[i] * 30 / 32768.0;
                        toTransform[2*i + 1] = 0.0;
                    }

                    transform.complexForward(toTransform);
                    publishProgress(toTransform);
                }
                audioRecord.stop();
            } catch (Throwable t) {
                Log.e("AudioRecord", "Recording Failed");
            }
            return null;
        }

        @Override
        protected void onProgressUpdate(double[]... toTransform) {

            //Get the magnitudes for each of the frequencies we are interested in
            int startMagnitude = (int)getMagnitude(toTransform[0][2 * STARTINDEX], toTransform[0][2 * STARTINDEX + 1]);
            int zeroMagnitude = (int)getMagnitude(toTransform[0][2 * ZEROINDEX], toTransform[0][2 * ZEROINDEX + 1]);
            int oneMagnitude = (int)getMagnitude(toTransform[0][2 * ONEINDEX], toTransform[0][2 * ONEINDEX + 1]);

            /*
            int sample1 = (int)getMagnitude(toTransform[0][2 * 50], toTransform[0][2 * 50 + 1]);
            int sample2 = (int)getMagnitude(toTransform[0][2 * 51], toTransform[0][2 * 51 + 1]);
            int sample3 = (int)getMagnitude(toTransform[0][2 * 52], toTransform[0][2 * 52 + 1]);
            int sample4 = (int)getMagnitude(toTransform[0][2 * 53], toTransform[0][2 * 53 + 1]);
            int average = (sample1 + sample2 + sample3 + sample4)/4;*/

            //Start bit found to be Point 222, at 19125khz
            if(startMagnitude  > 50){// && (startMagnitude > (zeroMagnitude+2) && startMagnitude > (oneMagnitude+2))) {
                transmissionBuffer.add('s');
                transmissionBuffer.remove(0);
            }
            //Zero bit found to be Point 226, at 19500khz
            else if(zeroMagnitude  > 50){// && (zeroMagnitude > (startMagnitude+2) && zeroMagnitude > (oneMagnitude+2))) {
                transmissionBuffer.add('0');
                transmissionBuffer.remove(0);
            }
            //One bit found to be Point 231, at 19875khz
            else if(oneMagnitude  > 40){// && (oneMagnitude > (startMagnitude+2) && oneMagnitude > (zeroMagnitude+2))) {
                transmissionBuffer.add('1');
                transmissionBuffer.remove(0);
            }

            if(transmissionBuffer.get(0) == transmissionBuffer.get(1))
            {
                if(transmissionBuffer.get(0) != currentCharacter) {
                    //We have now detected a new frequency, handle that somehow
                    currentCharacter = transmissionBuffer.get(0);
                    if (currentCharacter == 's'){
                        readyForBit = true;
                    }else if(readyForBit) {
                        readyForBit = false;
                        fakeByte[fakeByteIndex] = currentCharacter;
                        if (fakeByteIndex != 7){
                            fakeByteIndex++;
                        }else {
                            fakeByteIndex = 0;
                            String newline = System.getProperty("line.separator");
                            String reverse = new StringBuffer(new String(fakeByte)).reverse().toString();
                            Byte byteRead = (byte)(int)Integer.valueOf(reverse, 2);
                            if((char) (byteRead & 0xFF) == '\0')
                                textView.append(newline);
                            else
                                textView.append((char) (byteRead & 0xFF)+"");
                        }
                    }
                }
            }


            int max = 0;
            int maxPoint = 0;

            //Output data in the form of a graph
            canvas.drawColor(Color.BLACK);
            for (int i = 0; i < toTransform[0].length/4; i++) {
                int x = i;
                int magnitude = (int) getMagnitude(toTransform[0][2 * i], toTransform[0][2 * i + 1]);
                int downy = (int) (HEIGHT - magnitude);
                int upy = HEIGHT;
                canvas.drawLine(x*4, downy, x*4, upy, paint);
                if(magnitude > max)
                {
                    max = magnitude;
                    maxPoint = i;
                }
            }
            imageView.invalidate();
            /*Log.i("TransferFragment", "New Sample");
            if(getMagnitude(toTransform[0][2 * STARTINDEX], toTransform[0][2 * STARTINDEX + 1]) > 10)
                Log.i("TransferFragment", "Point " + STARTINDEX + ": " + getMagnitude(toTransform[0][2 * STARTINDEX], toTransform[0][2 * STARTINDEX + 1]));
            if(getMagnitude(toTransform[0][2 * ZEROINDEX], toTransform[0][2 * ZEROINDEX + 1]) > 10)
                Log.i("TransferFragment", "Point " + ZEROINDEX + ": " + getMagnitude(toTransform[0][2 * ZEROINDEX], toTransform[0][2 * ZEROINDEX + 1]));
            if(getMagnitude(toTransform[0][2 * ONEINDEX], toTransform[0][2 * ONEINDEX + 1]) > 10)
                Log.i("TransferFragment", "Point " + ONEINDEX + ": " + getMagnitude(toTransform[0][2 * ONEINDEX], toTransform[0][2 * ONEINDEX + 1]));
            */
            //Log.i("TransferFragment", "Point " + ONEINDEX + ": " + getMagnitude(toTransform[0][2 * ONEINDEX], toTransform[0][2 * ONEINDEX + 1]));
            //Log.i("TransferFragment", "Point " + maxPoint + " : " + max);
        }
    }

    public int getMagnitude(double im, double real)
    {
        return (int)Math.sqrt((im*im) + (real*real));
    }

}