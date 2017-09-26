from abc import abstractmethod
import collections
from functools import reduce
import itertools
import math
import operator
import types

import numpy as np
from pydub import AudioSegment
from tensorpack.dataflow import DataFlow

from vox.utils import match_target_amplitude


class FSRDataFlow(DataFlow):
    
    def __init__(self, taps, init, nbytes):
        self.taps = itertools.cycle(taps)
        self.init = init
        self.nbytes = nbytes
        self.bytedepth = 2
        self.mod_mask = (1 << self.bytedepth*8) - 1

    def get_taps(self):
        taps = next(self.taps)
        self.tap_mask = reduce(
            operator.or_,
            map(lambda b: 1 << abs(b - 1), taps)
        )

    @abstractmethod
    def step(self, reg):
        pass

    def get_data(self):
        reg = self.init
        while True:
            out = bytearray()
            self.get_taps()
            for _ in range(self.nbytes):
                out += int(reg & self.mod_mask).to_bytes(
                    self.bytedepth, 
                    byteorder='big'
                )
                reg = self.step(reg)
            frames = np.array(
                match_target_amplitude(
                    AudioSegment(
                        data=out,
                        sample_width=2,
                        frame_rate=44100,
                        channels=1
                    ),
                    -20
                )
                .get_array_of_samples()
            ).reshape((-1, 1))
            yield [frames]


class LFSRDataFlow(FSRDataFlow):
    def step(self, reg):
        return ((reg << 1) | self.feedback(reg)) & self.mod_mask

    def feedback(self, reg):
        tapped_bits = map(int, bin(reg & self.tap_mask)[2:])
        return reduce(
            operator.xor,
            tapped_bits
        )
