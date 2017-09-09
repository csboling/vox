from vox.data.vocobox import VocoboxDataFlow
from vox.preview import Previewer


def main():
    Previewer().preview(
        # TIMITDataFlow('~/datasets/TIMIT/data/lisa/data/timit/raw/TIMIT/TRAIN')
        VocoboxDataFlow('~/datasets/human-voice-dataset/data/voices/martin/notes/exports/stereo')
    )

main()
