from abc import abstractmethod
from array import array
from functools import reduce
import math
import operator

import numpy as np
from pydub import AudioSegment
from tensorpack.dataflow import DataFlow


class FSRDataFlow(DataFlow):
    
    def __init__(self, taps, init, nbytes):
        self.taps = taps
        self.bytedepth = int(math.ceil(taps[0] / 8))
        self.mod_mask = (1 << max(taps)) - 1
        self.tap_mask = reduce(
            operator.or_,
            map(lambda b: 1 << abs(b - 1), taps)
        )

        self.init = init
        self.nbytes = nbytes

    @abstractmethod
    def step(self, reg):
        pass

    def get_data(self):
        reg = self.init
        while True:
            out = bytearray()
            for _ in range(self.nbytes):
                out += (reg & self.mod_mask).to_bytes(
                    self.bytedepth, 
                    byteorder='big'
                )
                reg = self.step(reg)
            frames = np.array(
                AudioSegment(
                    data=out,
                    sample_width=2,
                    frame_rate=44100,
                    channels=1
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
