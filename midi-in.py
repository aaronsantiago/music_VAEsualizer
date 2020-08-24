import mido
import asyncio
from metronome import Metronome
import pygame

# pygame mixer config
freq = 44100  # audio CD quality
bitsize = -16   # unsigned 16 bit
channels = 2  # 1 is mono, 2 is stereo
buffer = 1024   # number of samples
pygame.mixer.init(freq, bitsize, channels, buffer)
click_sound = pygame.mixer.Sound("click.wav")

# metronome callback
async def do_beat():
    pygame.mixer.Sound.play(click_sound)


# from https://stackoverflow.com/questions/56277440/how-can-i-integrate-python-mido-and-asyncio
def make_stream():
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()
    def callback(message):
        loop.call_soon_threadsafe(queue.put_nowait, message)
    async def stream():
        while True:
            yield await queue.get()
    return callback, stream()
async def print_messages():
    # create a callback/stream pair and pass callback to mido
    cb, stream = make_stream()
    mido.open_input('VirtualBus Bus 1', callback=cb)

    # print messages as they come just by reading from stream
    async for message in stream:
        print(message)

# create the metronome
callbacks = [do_beat]
tempo = 120
metronome = Metronome(tempo, callbacks)


# https://docs.python.org/3/library/asyncio-task.html#running-tasks-concurrently 
async def main():
    # Schedule three calls *concurrently*:
    await asyncio.gather(
        metronome.start(),
        print_messages(),
    )

asyncio.run(main())