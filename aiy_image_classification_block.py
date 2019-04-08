from picamera import PiCamera
from aiy.vision.inference import CameraInference
from aiy.vision.models import image_classification

from nio.properties import FloatProperty, IntProperty, VersionProperty
from nio import Signal
from .aiy_inference_base import InferenceBase


class ImageClassification(InferenceBase):

    threshold = FloatProperty(title='Minimum Score', default=0.0)
    top_k_predictions = IntProperty(title='Return Top k Predictions', default=3)

    version = VersionProperty('0.1.0')

    def __init__(self):
        super().__init__()
        self._running = True

    def stop(self):
        self._running = False
        self.logger.debug('killing child thread ...')
        super().stop()

    def run(self):
        while self._running:
            try:
                self.logger.debug('loading inference model ...')
                with CameraInference(image_classification.model()) as inference:
                    self.logger.debug('running inference ...')
                    for result in inference.run():
                        predictions = image_classification.get_classes(
                            result,
                            top_k=self.top_k_predictions(),
                            threshold=self.threshold())
                        outgoing_signals = []
                        for prediction in predictions:
                            signal_dict = {
                                'label': prediction[0],
                                'score': prediction[1],
                            }
                            outgoing_signal = Signal(signal_dict)
                            outgoing_signals.append(outgoing_signal)
                        if not self._running:
                            break
                        self.notify_signals(outgoing_signals)
            except:
                self.logger.exception('failed to get inference result!')
                self.reset_camera()
        self.release_camera()
