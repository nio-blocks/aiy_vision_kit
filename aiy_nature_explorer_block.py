from enum import Enum
try:
    from aiy.vision.inference import CameraInference
    from aiy.vision.models import inaturalist_classification
except (ModuleNotFoundError, ImportError):
    # not available on all platforms
    pass

from nio import Signal
from nio.properties import FloatProperty, IntProperty, SelectProperty, \
    VersionProperty
from .aiy_inference_base import InferenceBase


class Models(Enum):

    try:
        birds = inaturalist_classification.BIRDS
        insects = inaturalist_classification.INSECTS
        plants = inaturalist_classification.PLANTS
    except NameError:
        # not available on all platforms
        # define default value to allow it to load
        birds = None


class AIYNatureExplorer(InferenceBase):

    model = SelectProperty(
        Models,
        title='Classifier Model',
        default=Models.birds)

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
                self.logger.debug(
                    'loading {} model ...'.format(self.model().name))
                model = inaturalist_classification.model(self.model().value)
                with CameraInference(model) as inference:
                    self.logger.debug('running inference ...')
                    for result in inference.run():
                        predictions = inaturalist_classification.get_classes(
                            result,
                            top_k=self.top_k_predictions())
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
