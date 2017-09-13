from functools import reduce
from itertools import cycle, islice
from glob import glob
import os
import random
import time

# from madmom.audio import signal
import numpy as np
from pydub import AudioSegment
from tensorpack.utils.argtools import memoized

from vox.data.FSDataFlow import FSDataFlow

class WavDataFlow(FSDataFlow):

    def __init__(
            self, *args, 
            globs=('**/*.wav',), 
            sample_len=1000,
            max_seek=1000*60*1,
            find_peaks=True,
            blend_count=1,
            limit=None,
            **kwargs
        ):
        super().__init__(*args, **kwargs)
        self.globs = globs
        self.sample_len = sample_len
        self.max_seek = max_seek
        self.find_peaks = find_peaks
        self.blend_count = blend_count
        self.limit = limit

    @memoized
    def fnames(self):
        ret = []
        for g in islice(iter(self.globs), self.limit):
            ret += glob(os.path.join(self.path, g), recursive=True)
        return random.sample(ret, k=len(ret))

    def size(self):
        return len(self.fnames())

    def open_files(self):
        for fname in self.fnames():
            print(fname)
            yield AudioSegment.from_file(fname)

    def get_offset(self, arr):
            start = 0
            if self.find_peaks:
                peaks = [
                    ix for ix, aff
                    in enumerate(arr[..., 0] > (np.max(arr) / 10))
                    if aff
                ]
                if len(peaks):
                    return random.choice(peaks)
            limit = min(arr.shape[0], self.max_seek)
            if limit < self.sample_len:
                return 0
            return random.randint(0, limit - self.sample_len)

    def get_blended(self):
        g = cycle(self.open_files())
        return iter(
            lambda: reduce(
                lambda mixed, seg: mixed.overlay(
                    seg, 
                    position=random.randint(0, len(mixed))
                ),
                islice(g, random.randint(1, self.blend_count))
            ),
            None
        )


    samples_per_ms = 44100 / 1000
            
    def get_data(self):
        for seg in self.get_blended():
            print()
            print('{} ch @ {} Hz'.format(seg.channels, seg.frame_rate))
            frames = (
                seg
                .set_frame_rate(44100)
                .fade_in(100)
                .fade_out(100)
                .get_array_of_samples()
            )
            arr = np.array(frames).reshape(-1, seg.channels)
            print('seg: {}, arr: {}'.format(len(seg), arr.shape) )
            start = self.get_offset(arr)
            stop = start + int(self.sample_len * self.samples_per_ms)
            if stop > arr.shape[0]:
                stop -= start
                start = 0

            print('{}:{} ({}/{})'.format(start, stop, stop - start, arr.shape[0]))
            yield [
                arr[start:stop],
            ]
            
