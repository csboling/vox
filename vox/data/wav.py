from glob import glob
import os
import random

# from madmom.audio import signal
from pydub import AudioSegment
import numpy as np
from tensorpack.utils.argtools import memoized

from vox.data.FSDataFlow import FSDataFlow

class WavDataFlow(FSDataFlow):

    def __init__(
            self, *args, 
            globs=('**/*.wav',), 
            sample_len=1000,
            max_seek=1000*60*1,
            find_peaks=False,
            **kwargs
        ):
        super().__init__(*args, **kwargs)
        self.globs = globs
        self.sample_len = sample_len
        self.max_seek = max_seek
        self.find_peaks = find_peaks

    @memoized
    def fnames(self):
        ret = []
        for g in self.globs:
            ret += glob(os.path.join(self.path, g), recursive=True)
        return random.sample(ret, k=len(ret))

    def size(self):
        return len(self.fnames())

    def open_files(self):
        for fname in self.fnames():
            print(fname)
            yield AudioSegment.from_file(fname)

    def get_data(self):
        for seg in self.open_files():
            # if seg.channels > 1:
            #     import pdb; pdb.set_trace()
            limit = min(len(seg), self.max_seek)
            if limit < self.sample_len:
                print('too short for even length clip: {} < {}'.format(limit, self.sample_len))
                continue
            start = random.randint(0, limit - self.sample_len)
            stop = start + self.sample_len
            print('{}:{}/{}'.format(start, stop, len(seg)))
            yield [
                np.array(
                    seg[start:stop].get_array_of_samples()
                ),
            ]
            
