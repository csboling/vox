import multiprocessing

from tensorpack.dataflow import RandomChooseData, PrefetchDataZMQ

from vox.data.audioset import AudiosetDataFlow
from vox.data.wav import WavDataFlow
from vox.preview import Previewer


def main():
    # audioset = AudiosetDataFlow(
    #     path='~/datasets/audioset/short-clips',
    #     csv_file='~/datasets/audioset/balanced_train_segments.csv'
    # )
    ds = RandomChooseData(
        [
            WavDataFlow(
                '~/datasets/omniglot', 
                globs=('**/*.mp3',)
            ),
            WavDataFlow(
                '~/datasets/VCTK'
            ),
            # audioset,
            WavDataFlow('~/datasets/birdsong/'),
            WavDataFlow('~/datasets/human-voice-dataset/data/voices'),
        ]
    )
    ds.reset_state()
    # audioset.pre_download()

    Previewer(dev_ixs=[0]).preview(ds)

main()
