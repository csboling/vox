import multiprocessing

import numpy as np
from tensorpack.dataflow import RandomChooseData, PrefetchDataZMQ

from vox.data.fsr.FSR import LFSRDataFlow
from vox.data.wav import WavDataFlow
from vox.preview import Previewer


def main():
    ds = RandomChooseData(
        [
            WavDataFlow(
                '~/datasets/omniglot',
                globs=('**/*.mp3',)
            ),
            WavDataFlow(
                '~/datasets/nsynth/nsynth-test/'
            ),
            LFSRDataFlow(
                taps=iter(
                    np.random.randint(1, 15, (100, 5))
                ),
                init=0x1234, 
                nbytes=2*1*44100
            ),
            WavDataFlow('~/datasets/birdsong/'),
        ]
    )
    ds.reset_state()

    Previewer(dev_ixs=[0]).preview(ds)

main()
