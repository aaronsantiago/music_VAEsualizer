# this will process a midi file, removing polyphony
# and splitting into 2 bar sections

import argparse
import mido

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument("--input",
      help="input file")
  parser.add_argument("--output",
      help="base name for the output")
  args = parser.parse_args()

  mid = mido.MidiFile(args.input)


  mid2 = mido.MidiFile()
  track = mido.MidiTrack()
  mid2.tracks.append(track)
  # print(mid)
  lastNoteOnMsg = None
  timeSinceLastMsg = 0
  totalTime = 0
  numSongs = 0
  for msg in mid:
    if msg.type == "note_on":
      if lastNoteOnMsg:
        timeSinceLastMsg += msg.time

        # # The following lines restrict notes to a single
        # # octave, but so far this has been unecessary
        # while lastNoteOnMsg.note > 66:
        #   lastNoteOnMsg.note -= 12
        # while lastNoteOnMsg.note < 54:
        #   lastNoteOnMsg.note += 12

        # We rewrite note lengths so that there are no rests
        # by keeping track of the time since the last on message
        # and writing note_on and note_off in pairs using that time
        tickTime = int(mido.second2tick(timeSinceLastMsg, 400, 500000))
        if tickTime == 0: continue
        lastNoteOnMsg.time = 0
        totalTime += tickTime
        track.append(lastNoteOnMsg)
        track.append(mido.Message('note_off', note=lastNoteOnMsg.note, velocity=lastNoteOnMsg.velocity, time=tickTime))

        # If we're past 2 measures, write a new file
        if totalTime > 400 * 8:
          mid2.save(args.output + ('%d.mid' % numSongs))
          numSongs += 1
          mid2 = mido.MidiFile()
          track = mido.MidiTrack()
          mid2.tracks.append(track)
          totalTime = 0

      lastNoteOnMsg = msg
      timeSinceLastMsg = 0
    else:
      # print(msg)
      timeSinceLastMsg += msg.time
