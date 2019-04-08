import io
from PIL import Image
from aiy.vision.inference import ImageInference
from aiy.vision.models import inaturalist_classification

from nio.signal.base import Signal
from .aiy_inference_base import InferenceBase


class iNaturalist(InferenceBase):

    def __init__(self):
        super().__init__()
        self._running = True

    def stop(self):
        self._running = False
        self.logger.debug('killing child thread ...')
        super().stop()

    def run(self):
        frame_buffer = io.BytesIO()
        self.logger.debug('loading inference model ...')
        model = inaturalist_classification.model(inaturalist_classification.BIRDS)
        with ImageInference(model) as inference:
            while self._running:
                self.camera.capture(frame_buffer, format='jpeg')
                image = Image.open(frame_buffer)
                result = inference.run(image)
                predictions = inaturalist_classification.get_classes(
                    result,
                    top_k=3,
                    threshold=0)
                outgoing_signals = []
                for prediction in predictions:
                    signal_dict = {
                        'label': prediction[0],
                        'confidence': prediction[1],
                    }
                    outgoing_signal = Signal(signal_dict)
                    outgoing_signals.append(outgoing_signal)
                if not self._running:
                    break
                self.notify_signals(outgoing_signals)
        self.release_camera()
