from functools import reduce
from itertools import cycle, islice
from glob import glob
import os
import random
import time

import numpy as np
from pydub import AudioSegment
from tensorpack.utils.argtools import memoized

from vox.data.FSDataFlow import FSDataFlow
from vox.utils import match_target_amplitude


class WavDataFlow(FSDataFlow):

    def __init__(
            self, *args, 
            globs=('**/*.wav',), 
            offset=0,
            sample_len=1000,
            max_seek=1000*60*1,
            find_peaks=True,
            blend_count=1,
            limit=None,
            max_file_size=10485760,
            **kwargs
        ):
        super().__init__(*args, **kwargs)
        if isinstance(globs, str):
            self.globs = (globs,)
        else:
            self.globs = globs
        self.offset = offset
        self.sample_len = sample_len
        self.max_seek = max_seek
        self.find_peaks = find_peaks
        self.blend_count = blend_count
        self.limit = limit
        self.max_file_size = max_file_size

    @memoized
    def fnames(self):
        ret = []
        for g in islice(iter(self.globs), self.limit):
            fullglob = os.path.join(self.path, g)
            print(fullglob)
            ret += glob(fullglob, recursive=True)
        return random.sample(ret, k=len(ret))

    def size(self):
        return len(self.fnames())

    def open_files(self):
        for fname in self.fnames():
            if os.stat(fname).st_size > self.max_file_size:
                print('skip {} (too large)'.format(fname))
                continue
            print(fname)
            yield AudioSegment.from_file(fname)[self.offset:]

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
        for seg in cycle(self.open_files()): # self.get_blended():
            print()
            print('{} ch @ {} Hz'.format(seg.channels, seg.frame_rate))
            frames = (
                match_target_amplitude(seg, -20)
                .set_frame_rate(44100)
                .fade_in(100)
                .fade_out(100)
                .get_array_of_samples()
            )
            arr = np.array(frames).reshape(-1, seg.channels)
            print('{} ms, arr: {}'.format(len(seg), arr.shape) )
            start = self.get_offset(arr)
            stop = start + int(self.sample_len * self.samples_per_ms)
            if stop > arr.shape[0]:
                stop -= start
                start = 0

            print('{}:{} ({}/{})'.format(start, stop, stop - start, arr.shape[0]))
            yield [
                arr[start:stop],
            ]
            
