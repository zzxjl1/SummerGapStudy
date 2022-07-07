import threading
import sounddevice as sd
import queue
import time


pcm_queue = queue.Queue(maxsize=2)


def add_to_pcm_queue(pcm_data):
    if pcm_queue.full():
        # pcm_queue.queue.clear()
        pcm_queue.get_nowait()
    pcm_queue.put_nowait(pcm_data)


def callback_client(outdata, frames, time, status):
    if not pcm_queue.empty():
        data = pcm_queue.get_nowait()
        outdata[:] = data


def run():
    with sd.OutputStream(channels=1,
                         samplerate=8000,
                         blocksize=1024*5,
                         dtype='int16', callback=callback_client):
        while True:
            print("audio debug thread running ...") 
            time.sleep(10)



threading.Thread(target=run).start()
