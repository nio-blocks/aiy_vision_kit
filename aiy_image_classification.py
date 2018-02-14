from picamera import PiCamera

from aiy.vision.inference import CameraInference
from aiy.vision.models import image_classification

from nio.block.base import Block
from nio.properties import VersionProperty
from nio.util.threading import spawn
from nio.signal.base import Signal


class ImageClassification(Block):

    version = VersionProperty('0.0.1')

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
        self.camera.framerate = 30
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
                classes = image_classification.get_classes(result)
                self.logger.debug('returned {} classes'.format(len(classes)))
                top_score = max([score for _, score in classes])
                top_prediction = [(obj, score) for obj, score in classes if score == top_score][0]
                self.notify_signals([Signal({'prediction': top_prediction[0], 'confidence': top_prediction[1]})])
                if self._kill:
                    break
            self.camera.close()
            self.logger.debug('camera released')
