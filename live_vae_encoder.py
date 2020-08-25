
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

import time
import traceback


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

def encode_to_vector(name):
    print ("encoding file " + name)
    print ("Reloading file as note sequence", flush=True)
    input_midi_file = os.path.expanduser(name)
    input_midi_seq = note_seq.midi_file_to_note_sequence(input_midi_file)

    print ("Encoding to vector", flush=True)
    (_, mu, _) = model.encode([input_midi_seq])
    print(mu[0], flush=True)
    print ("Encode success! Vector above", flush=True)

filePrefix = "test"
currentFile = 0
lastProcessed = -1

while True:
    name = filePrefix + ("%d.mid" % (currentFile))
    nextName = filePrefix + ("%d.mid" % (currentFile + 1))
    if os.path.exists(nextName):
        currentFile += 1
    elif lastProcessed < currentFile:
        lastProcessed = currentFile
        try:
            encode_to_vector(name)
        except Exception:
            traceback.print_exc()
    else:
        time.sleep(.01)