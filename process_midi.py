# this will process a midi file, removing polyphony
# and splitting into 2 bar sections

import argparse
import mido

class MVAEsMidiProcessor:
  lastNoteOnMsg = None
  timeSinceLastMsg = 0
  totalTime = 0
  numSongs = 0
  track = None
  autoWrite = True
  outputFileBaseName = ""
  currentMsgQueue = []
  currentNote = -1
  writtenUpTo = 0
  def __init__(self, outputFileBaseName):
    self.outputFileBaseName = outputFileBaseName
    # print(mid)

  def processMessage(self, msg):
    self.totalTime += msg.time
    if msg.type == "note_on":
      self.currentNote = msg.note
      # We rewrite note lengths so that there are no rests
      # by keeping track of the time since the last on message
      # and writing note_on and note_off in pairs using that time
      if self.lastNoteOnMsg:
        self.currentMsgQueue.append(mido.Message('note_off',
            note=self.lastNoteOnMsg.note,
            velocity=self.lastNoteOnMsg.velocity,
            time=self.timeSinceLastMsg + msg.time))
        msg.time = 0
      else:
        msg.time += self.timeSinceLastMsg
      self.currentMsgQueue.append(msg)
        # self.track.append(self.lastNoteOnMsg)
        # self.track.append(mido.Message('note_off', note=self.lastNoteOnMsg.note, velocity=self.lastNoteOnMsg.velocity, time=tickTime))
      self.lastNoteOnMsg = msg
      self.timeSinceLastMsg = 0
    elif msg.type == "note_off" and msg.note == self.currentNote:
      msg.time += self.timeSinceLastMsg
      self.currentMsgQueue.append(msg)
      self.timeSinceLastMsg = 0
      self.currentNote = -1
      self.lastNoteOnMsg = None
    else:
      # print(msg)
      self.timeSinceLastMsg += msg.time

    print(self.totalTime)
    # If we're past 2 measures, write a new file
    if self.totalTime - self.writtenUpTo > 8 / (120/60) and self.autoWrite:
      self.writeCurrentMidi(self.writtenUpTo)
      self.writtenUpTo += 8 / (120/60)
      # self.totalTime = 0

  def writeCurrentMidi(self, startWritingAt):
    mid2 = mido.MidiFile()
    track = mido.MidiTrack()
    mid2.tracks.append(track)

    # startWritingAt = 0
    # playhead = 0
    # for msg in self.currentMsgQueue:
    #   playhead += msg.time
    #   # if the entirety of the next 8 bar section is available,
    #   # record that one instead of the current one.
    #   if playhead > startWritingAt + (8 / (120/60)) * 2:
    #     startWritingAt += (8 / (120/60))

    playhead = 0
    started = False
    accumulatedTimeFromBeginningOfRecording = 0
    current_note_on = False
    for msg in self.currentMsgQueue:
      playhead += msg.time
      write = False
      if playhead > startWritingAt:
        if started:
          write = True
        elif msg.type == "note_on":
          write = True
      if write:
        # Place the first message at the correct time in the
        # midi file
        if not started:
          msg.time = playhead - startWritingAt

        leave = False
        # hope the next message is note_off
        if playhead > startWritingAt + (8 / (120/60)):
          if not current_note_on: break
          msg.time -= playhead - (startWritingAt + (8 / (120/60)))
          leave = True
        tickTime = int(mido.second2tick(msg.time, 480, 500000))
        track.append(mido.Message(msg.type,
            note=msg.note,
            velocity=msg.velocity,
            time=tickTime))
        if leave:
          break
        started = True
        if msg.type == "note_on":
          current_note_on = True
        else:
          current_note_on = False

    mid2.save(self.outputFileBaseName + ('%d.mid' % self.numSongs))
    self.numSongs += 1

  def getLastMidiName(self):
    return self.outputFileBaseName + ('%d.mid' % (self.numSongs - 1))


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

