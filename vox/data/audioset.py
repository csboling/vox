import collections
import csv
from itertools import islice
import os

import pafy

from vox.data.wav import WavDataFlow


class AudiosetDataFlow(WavDataFlow):
    base_url = 'https://youtube.com/watch?v={}'

    def __init__(self, csv_file, *args, **kwargs):
        super().__init__(
            *args, 
            globs=(
                '**/*.m4a',
                '**/*.ogg',
            ), 
            **kwargs
        )
        self.csv_file = self.resolve_path(csv_file)

    @staticmethod
    def consume(iterator, n):
        if n is None:
            collections.deque(iterator, maxlen=0)
        else:
            next(islice(iterator, n, n), None)

    def pre_download(self, limit=500):
        with open(self.csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            n = 0
            g = iter(reader)
            self.consume(g, 4000)
            for ix, row in enumerate(g):
                if row[0][0] == '#':
                    continue
                slug, start, stop, *rest = row
                url = self.base_url.format(slug)
                try:
                    vid = pafy.new(url)
                    dur = ''.join(vid.duration.split(':'))
                    if dur[:3] != '000':
                        print('skip {}@{}: too long'.format(ix, url))
                        continue
                    aud = vid.getbestaudio()
                    if aud.extension == 'opus':
                        print('skip {}@{}: slow format'.format(ix, url))
                        continue

                    fname = os.path.join(
                        self.path, 
                        '{}.{}'.format(vid.title, aud.extension)
                    )

                    if not os.path.exists(fname):
                        print('fetched {} (#{} / {}): {}'.format(
                            ix, n, limit,
                            aud.download(filepath=fname)
                        ))
                        if n > limit:
                            break
                        else:
                            n += 1
                    else:
                        print('skip {}@{}: already fetched'.format(ix, url))
                except Exception as e:
                    print('could not download {}@{}: {}'.format(ix, url, str(e)))
                
