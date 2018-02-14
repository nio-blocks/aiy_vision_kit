import io
from PIL import Image

from picamera import PiCamera

from aiy.vision.inference import ImageInference
from aiy.vision.models import object_detection

from nio.block.base import Block
from nio.properties import VersionProperty
from nio.util.threading import spawn
from nio.signal.base import Signal


class ObjectDetection(Block):

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
        with ImageInference(object_detection.model()) as inference:
            while not self._kill:
                foo = io.BytesIO()
                self.logger.debug('capturing frame')
                self.camera.capture(foo, format='jpeg')
                image = Image.open(foo)
                self.logger.debug('cropping image')
                image_center, offset = self._crop_center(image)
                self.logger.debug('running inference')
                result = inference.run(image_center)
                self.logger.debug('getting results')
                objects = object_detection.get_objects(result, 0.3, offset)
                self.logger.debug([str(obj) for obj in objects])
                #top_score = max([score for _, score in classes])
                #top_prediction = [(obj, score) for obj, score in classes if score == top_score][0]
                #self.notify_signals([Signal({'prediction': top_prediction[0], 'confidence': top_prediction[1]})])
                if self._kill:
                    break
            self.camera.close()
            self.logger.debug('camera released')

    def _crop_center(self, image):
        width, height = image.size
        size = min(width, height)
        x, y = (width - size) /2, (height - size) /2
        return image.crop((x, y, x + size, y + size)), (x, y)
