# this will process a midi file, removing polyphony
# and splitting into 2 bar sections

import argparse
import mido

class MVAEsMidiProcessor:
  mid2 = None
  lastNoteOnMsg = None
  timeSinceLastMsg = 0
  totalTime = 0
  numSongs = 0
  track = None
  outputFileBaseName = ""
  def __init__(self, outputFileBaseName):
    self.mid2 = mido.MidiFile()
    self.track = mido.MidiTrack()
    self.mid2.tracks.append(self.track)
    self.outputFileBaseName = outputFileBaseName
    # print(mid)

  def processMessage(self, msg):
    if msg.type == "note_on":
      if self.lastNoteOnMsg:
        self.timeSinceLastMsg += msg.time

        # # The following lines restrict notes to a single
        # # octave, but so far this has been unecessary
        # while self.lastNoteOnMsg.note > 66:
        #   self.lastNoteOnMsg.note -= 12
        # while self.lastNoteOnMsg.note < 54:
        #   self.lastNoteOnMsg.note += 12

        # We rewrite note lengths so that there are no rests
        # by keeping track of the time since the last on message
        # and writing note_on and note_off in pairs using that time
        tickTime = int(mido.second2tick(self.timeSinceLastMsg, 400, 500000))
        if tickTime == 0: return
        self.lastNoteOnMsg.time = 0
        self.totalTime += tickTime
        self.track.append(self.lastNoteOnMsg)
        self.track.append(mido.Message('note_off', note=self.lastNoteOnMsg.note, velocity=self.lastNoteOnMsg.velocity, time=tickTime))

        # If we're past 2 measures, write a new file
        if self.totalTime > 400 * 8:
          self.mid2.save(self.outputFileBaseName + ('%d.mid' % self.numSongs))
          self.numSongs += 1
          self.mid2 = mido.MidiFile()
          self.track = mido.MidiTrack()
          self.mid2.tracks.append(self.track)
          self.totalTime = 0

      self.lastNoteOnMsg = msg
      self.timeSinceLastMsg = 0
    else:
      # print(msg)
      self.timeSinceLastMsg += msg.time


if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument("--input",
      help="input file")
  parser.add_argument("--output",
      help="base name for the output")
  args = parser.parse_args()

  mid = mido.MidiFile(args.input)
  processor = MVAEsMidiProcessor(args.output)
  for msg in mid:
    processor.processMessage(msg)

