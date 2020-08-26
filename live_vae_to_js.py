import eel
import sys
import live_vae_encoder

import numpy

eel.init('web')
eel.start('index.html', block=False)

last = None

def recv_vector(latent):
    print ("received new vector")
    global last
    if last is not None:
        dist = numpy.linalg.norm(last - latent)
        last = latent
        print(dist)
        eel.moveDot(float(dist))
    last = latent

live_vae_encoder.begin_infinite_polling(recv_vector, eel.sleep)