import multiprocessing

from tensorpack.dataflow import RandomChooseData, PrefetchDataZMQ

from vox.data.audioset import AudiosetDataFlow
from vox.data.fsr.FSR import LFSRDataFlow
from vox.data.wav import WavDataFlow
from vox.preview import Previewer


def main():
    # audioset = AudiosetDataFlow(
    #     path='~/datasets/audioset/short-clips',
    #     csv_file='~/datasets/audioset/balanced_train_segments.csv'
    # )
    ds = RandomChooseData(
        [
            # WavDataFlow(
            #     '~/datasets/omniglot',
            #     globs=('**/*.mp3',)
            # ),
            # WavDataFlow(
            #     '~/datasets/nsynth/nsynth-test'
            # ),
            # WavDataFlow(
            #     '~/datasets/VCTK/VCTK-Corpus/wav48'
            # ), 
            # WavDataFlow(
            #     '~/datasets/ENST-drums-dataset',
            #     globs='drummer_*/*.wav'
            # ),
            LFSRDataFlow(
                taps=[15,14,13,12], 
                init=0x1234, 
                nbytes=2*1*44100
            ),
            # # audioset,
            # WavDataFlow('~/datasets/herps/', globs='*.mp3', offset=3000),
            # # WavDataFlow('~/datasets/jamendo/train/', globs='*.ogg'),
            # WavDataFlow('~/datasets/birdsong/'),
            # # WavDataFlow('~/datasets/human-voice-dataset/data/voices'),
        ]
    )
    ds.reset_state()
    # audioset.pre_download()

    Previewer(dev_ixs=[0]).preview(ds)

main()
