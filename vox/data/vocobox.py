from glob import iglob
import os

import madmom
import numpy as np
from scipy.io import wavfile

from vox.data.FSDataFlow import FSDataFlow

class VocoboxDataFlow(FSDataFlow):

    def open_files(self):
        for fname in iglob(
            os.path.join(self.path, '**/*.wav'),
            recursive=True
        ):
            print(fname)
            signal, rate = madmom.audio.signal.load_wave_file(fname)
            yield (rate, signal)

    def get_data(self):
        pass
