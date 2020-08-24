Some working notes here:
https://docs.google.com/document/d/1oRILt7R_RNo1cY-OAbIfaV8OJJ9dAvy6wCiYU6aUb9A/edit

setup:
Download this model: https://storage.googleapis.com/magentadata/models/music_vae/checkpoints/cat-mel_2bar_big.tar   
`pip install magenta` or check the official docs: https://github.com/magenta/magenta/blob/master/README.md#installation   
the preprocessor needs `mido` as well

`pip install magenta mido` <- will do it

running:
give process_midi.py a monophonic midi file, and it will output
the midi chopped up into 2 bar sections, and with any polyphony removed.   
`python process_midi.py --input transcription_3note.mid --output preprocessed_midi/new_3note_section`

music_vae_generate.py was cannibalized into playing with the raw
melody -> vector generation, so take a look at it and look for the
non-magenta section. to run:

```python music_vae_generate.py \
--config=cat-mel_2bar_big \
--checkpoint_file=cat-mel_2bar_big.tar \
--input_midi_1=transcription.mid \
--input_midi_2=generated/b.mid \
--output_dir=generated```

if you want to use the original MusicVAE it may have been installed
to your path:

```music_vae_generate \
--config=cat-mel_2bar_big \
--checkpoint_file=cat-mel_2bar_big.tar \
--mode=interpolate \
--num_outputs=5 \
--input_midi_1=transcription.mid \
--input_midi_2=generated/b.mid \
--output_dir=generated```


currently:   
osc_client.py/osc_server.py testing OSC with python, not notable   
play.py plays a midi file in case you need an easy way to do that:
`python play.py transcription_3note.mid`



