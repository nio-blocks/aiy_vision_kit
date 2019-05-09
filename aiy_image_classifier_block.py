try:
    ModuleNotFoundError  # added in py3.6
except:
    # make it an alias of ImportError
    ModuleNotFoundError = ImportError
try:
    from aiy.vision.inference import CameraInference
    from aiy.vision.models import image_classification
except ModuleNotFoundError:
    # not available on all platforms
    pass

from nio.properties import FloatProperty, IntProperty, VersionProperty
from nio import Signal

from .aiy_inference_base import InferenceBase


class AIYImageClassifier(InferenceBase):

    top_k_predictions = IntProperty(
        title='Return Top k Predictions',
        default=5,
        advanced=True)
    version = VersionProperty('0.1.0')

    def start(self):
        self._running = True
        super().start()

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
                            threshold=0)
                        outgoing_signals = []
                        for label, score in predictions:
                            signal_dict = {
                                'label': label,
                                'score': score,
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
