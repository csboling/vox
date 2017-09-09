import pyaudio


class Previewer:
    types = {
        'int16':   pyaudio.paInt16,
        'float32': pyaudio.paFloat32,
    }

    def preview(self, dataflow):
        p = pyaudio.PyAudio()
        for rate, signal in dataflow.open_files():
            stream = p.open(
                output_device_index=0,
                format=self.types[signal.dtype.name],
                channels=signal.shape[-1],
                rate=rate,
                output=True
            )
            stream.write(signal)
            stream.close()
