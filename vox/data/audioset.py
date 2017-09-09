import csv
from itertools import islice
import os

import pafy

from vox.data.wav import WavDataFlow


class AudiosetDataFlow(WavDataFlow):
    base_url = 'https://youtube.com/watch?v={}'

    def __init__(self, csv_file, *args, **kwargs):
        super().__init__(*args, fglob='**/*.{opus,m4a,ogg}', **kwargs)
        self.csv_file = self.resolve_path(csv_file)

    def pre_download(self, limit=500):
        with open(self.csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in islice(iter(reader), limit):
                if row[0][0] == '#':
                    continue
                slug, start, stop, *rest = row
                url = self.base_url.format(slug)
                try:
                    vid = pafy.new(url)
                    aud = vid.getbestaudio()
                    fname = os.path.join(
                        self.path, 
                        '{}.{}'.format(vid.title, aud.extension)
                    )

                    if not os.path.exists(fname):
                        print('fetched {}'.format(aud.download(filepath=fname)))
                    else:
                        print('skip {}'.format(url))
                except (IOError, ValueError):
                    print('could not download {}'.format(url))
                
