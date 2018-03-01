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
                classes = image_classification.get_classes(result,  max_num_objects=10)
                if not self._kill:
                    self.notify_signals([Signal({'predictions': classes})])
                else:
                    break
            self.camera.close()
            self.logger.debug('camera released')
