from tensorpack.dataflow import RandomMixData

from vox.data.wav import WavDataFlow
from vox.preview import Previewer


def main():
    ds = RandomMixData(
        [
            WavDataFlow('~/datasets/birdsong/'),
            WavDataFlow('~/datasets/human-voice-dataset/data/voices')
        ]
    )
    ds.reset_state()
    Previewer(dev_ixs=[0,1]).preview(ds)

main()
