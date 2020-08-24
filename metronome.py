# ripped from http://thomasruble.com/blog/make-a-metronome-with-python-asyncio/

import asyncio
import time
from typing import Callable, Any, List, Awaitable

CallBack = Callable[[None], Awaitable[Any]]
CallBacks = List[CallBack]

class Metronome:
  def __init__(self, tempo, callbacks):
    self.tempo = tempo
    self.callbacks = callbacks

  async def start(self):
    offset = 0

    while True:
      sleep_time = max(0, (60 / self.tempo - offset))
      await asyncio.sleep(sleep_time)

      # start timer
      t0 = time.time()

      for callback in self.callbacks:
        await callback()

      t1 = time.time()

      # calculate offset
      offset = t1 - t0