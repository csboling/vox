from glob import iglob
import os
import random

# from madmom.audio import signal
from pydub import AudioSegment
import numpy as np
from tensorpack.utils.argtools import memoized

from vox.data.FSDataFlow import FSDataFlow

class WavDataFlow(FSDataFlow):

    def __init__(self, *args, ext='wav', **kwargs):
        super().__init__(*args, **kwargs)
        self.ext = ext

    @memoized
    def fnames(self):
        return list(iglob(
            os.path.join(
                self.path, 
                '**/*.{}'.format(self.ext)
            ),
            recursive=True
        ))

    def size(self):
        return len(self.fnames())

    def open_files(self):
        for fname in self.fnames():
            print(fname)
            yield AudioSegment.from_file(fname)

    def get_data(self):
        for seg in self.open_files():
            window = 500
            offset = random.randint(0, len(seg) - window)
            yield [
                np.array(
                    seg[offset:offset+window].get_array_of_samples()
                ),
            ]
            
