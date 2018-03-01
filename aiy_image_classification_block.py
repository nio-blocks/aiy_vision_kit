from picamera import PiCamera

from aiy.vision.inference import CameraInference
from aiy.vision.models import image_classification

from nio import GeneratorBlock
from nio.properties import VersionProperty, IntProperty
from nio.util.threading import spawn
from nio.signal.base import Signal


class ImageClassification(GeneratorBlock):

    version = VersionProperty('0.0.1')
    num_top_predictions = IntProperty(
        title='Return Top k Predictions',
        default=10)

    def __init__(self):
        super().__init__()
        self.camera = None
        self._thread = None
        self._kill = False

    def configure(self, context):
        super().configure(context)
        self.camera = PiCamera()
        self.camera.sensor_mode = 4
        self.camera.resolution = (1640, 1232)
        self.camera.framerate = 15
        self.logger.debug('camera configured')

    def start(self):
        super().start()
        self._thread = spawn(self.gobabygo)

    def stop(self):
        super().stop()
        self._kill = True
        self.logger.debug('killing secondary thread')
        self._thread.join()

    def gobabygo(self):
        self.logger.debug('loading inference model')
        with CameraInference(image_classification.model()) as inference:
            for result in inference.run():
                self.logger.debug('running inference...')
                objects = image_classification.get_classes(
                    result, max_num_objects=self.num_top_predictions())
                out = []
                for obj in objects:
                    sig = {
                        'label': obj[0].split('/')[0],
                        'confidence': obj[1]}
                    out.append(Signal(sig))
                if not self._kill:
                    self.notify_signals(out)
                else:
                    break
            self.camera.close()
            self.logger.debug('camera released')
