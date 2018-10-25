# -*- coding: utf-8 -*-

import threading

import cv2
import pyaudio
from ffmpy import FFmpeg
import time
import wave

#fourcc = cv2.VideoWriter_fourcc(*'XVID')
fourcc = cv2.cv.FOURCC(*'XVID')
fps = 30.0

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 0.5
SAVE_AUDIO_FILE = '/udisk/aout.wav'
key = ''
flag = 0

class Get_Video_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.cap = cv2.VideoCapture(4)
        self.save_video = cv2.VideoWriter('/udisk/vout.avi', fourcc, fps, (640, 480))

    def run(self):
        global flag
        while self.cap.isOpened():
            rst, frame = self.cap.read()
            self.save_video.write(frame)
            cv2.imshow('frame', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        self.save_video.release()
        cv2.destroyAllWindows()
        flag = 1

class Get_Audio_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.wf = wave.open(SAVE_AUDIO_FILE, 'wb')

    def run(self):
        global flag
        self.stream = self.pa.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        self.wf.setnchannels(CHANNELS)
        self.wf.setsampwidth(self.pa.get_sample_size(FORMAT))
        self.wf.setframerate(RATE)

        while self.stream.is_active():
            print 'recording'
            frames = []
            for i in range(0, int(RATE/ CHUNK * RECORD_SECONDS)):
                data = self.stream.read(CHUNK)
                frames.append(data)
            self.wf.writeframes(b''.join(frames))
            if flag == 1:
                break
        print 'end'

        self.wf.close()
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

if __name__ == '__main__':
    p1 = Get_Video_Thread()
    p2 = Get_Audio_Thread()
    p1.start()
    p2.start()
    while True:
        time.sleep(1)
        if flag == 1:
            break

    ff = FFmpeg(
        inputs={'vout.avi': None, 'aout.wav': None},
        outputs={'rst.avi': '-c:v h264 -c:a ac3'}
    )

    print ff.cmd
    ff.run()



