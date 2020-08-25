
# magenta imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

from magenta.models.music_vae import configs
from magenta.models.music_vae import TrainedModel
import note_seq
import numpy as np
import tensorflow.compat.v1 as tf
# end magenta imports

import mido
import asyncio
import time
from metronome import Metronome
import pygame
from process_midi import MVAEsMidiProcessor as MProcessor


#########################################################################################
# BEGIN MAGENTA CODE HERE -----------------------------------------------------------
#########################################################################################
print ("setting up magenta model")
config = configs.CONFIG_MAP["cat-mel_2bar_big"]
config.data_converter.max_tensors_per_item = None

checkpoint_dir_or_path = \
        os.path.expanduser("cat-mel_2bar_big.tar")
print ("loading model")
model = TrainedModel(config, batch_size=min(8, 5),
                     checkpoint_dir_or_path=checkpoint_dir_or_path)
print ("loading model success!")

#########################################################################################
# END MAGENTA CODE HERE -----------------------------------------------------------
#########################################################################################

print ("Setting up pygame mixer")
# pygame mixer config
freq = 44100  # audio CD quality
bitsize = -16   # unsigned 16 bit
channels = 2  # 1 is mono, 2 is stereo
buffer = 1024   # number of samples
pygame.mixer.init(freq, bitsize, channels, buffer)
measure_sound = pygame.mixer.Sound("measure.wav")
click_sound = pygame.mixer.Sound("click.wav")

current_beat = 0
sounds = [measure_sound, click_sound,click_sound,click_sound, click_sound,click_sound,click_sound,click_sound]

print ("Setting up midi processing system")
midiProcessor = MProcessor("test")
midiProcessor.autoWrite = False
latestFileToProcess = ""
# metronome callback
async def do_beat():
    global current_beat, midiProcessor
    pygame.mixer.Sound.play(sounds[current_beat % len(sounds)])
    current_beat += 1
    if current_beat % 8 == 0 and current_beat > 0:
        print ("Writing last 8 beats to file")
        midiProcessor.writeCurrentMidi()
        latestFileToProcess = midiProcessor.getLastMidiName()

    if current_beat % 8 == 1 and current_beat > 1:
        print ("Reloading file as note sequence")
        input_midi_file = os.path.expanduser(midiProcessor.getLastMidiName())
        input_midi_seq = note_seq.midi_file_to_note_sequence(input_midi_file)

        print ("Encoding to vector")
        (_, mu, _) = model.encode([input_midi_seq])
        print(mu[0])
        print ("Encode success! Vector above")

lastMessageTime = time.time()
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
    global lastMessageTime
    # create a callback/stream pair and pass callback to mido
    cb, stream = make_stream()
    mido.open_input('VirtualBus Bus 1', callback=cb)

    # print messages as they come just by reading from stream
    async for message in stream:
        thisMessageTime = time.time()
        message.time = thisMessageTime - lastMessageTime
        lastMessageTime = thisMessageTime
        print(message)
        midiProcessor.processMessage(message)

# create the metronome
callbacks = [do_beat]
tempo = 120
metronome = Metronome(tempo, callbacks)


print ("Starting midi input")
# https://docs.python.org/3/library/asyncio-task.html#running-tasks-concurrently 
async def main():
    # Schedule three calls *concurrently*:
    await asyncio.gather(
        metronome.start(),
        print_messages(),
    )

asyncio.run(main())