import asyncio
import concurrent.futures

import pyaudio


class Previewer:
    types = {
        'int16':   pyaudio.paInt16,
        'float32': pyaudio.paFloat32,
    }
        
    def __init__(self, dev_ixs=None):
        self.backend = pyaudio.PyAudio()
        if dev_ixs is None:
            dev_ixs = [0]
        self.dev_ixs = dev_ixs

    def play(self, arr, dev_ix):
        stream = self.backend.open(
            output_device_index=dev_ix,
            format=self.types[arr.dtype.name],
            channels=arr.shape[-1],
            rate=44100,
            output=True
        )
        stream.write(arr)
        stream.close()

    async def broadcast(self, arr):
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.dev_ixs)
        ) as executor:
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(
                    executor,
                    self.play, arr, ix
                )
                for ix in self.dev_ixs
            ]
            for _ in await asyncio.gather(*futures):
                pass

    def preview(self, dataflow):
        loop = asyncio.get_event_loop()
        while True:
            for signal, *rest in dataflow.get_data():
                loop.run_until_complete(self.broadcast(signal))
