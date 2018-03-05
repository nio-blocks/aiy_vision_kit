import base64
import io
from PIL import Image

from picamera import PiCamera

from aiy.vision.inference import ImageInference
from aiy.vision.models import object_detection

from nio import GeneratorBlock
from nio.properties import VersionProperty
from nio.util.threading import spawn
from nio.signal.base import Signal


class ObjectDetection(GeneratorBlock):

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
        with ImageInference(object_detection.model()) as inference:
            while not self._kill:
                frame_buffer = io.BytesIO()
                self.logger.debug('capturing frame')
                self.camera.capture(frame_buffer, format='jpeg')
                image = Image.open(frame_buffer)
                image_center, offset = self._crop_center(image)
                self.logger.debug('running inference')
                result = inference.run(image_center)
                self.logger.debug('getting results')
                objects = object_detection.get_objects(result, 0.3, offset)
                out = []
                for obj in objects:
                    self.logger.debug(obj)
                    sig = {
                        'kind': obj._LABELS[obj.kind],
                        'score': obj.score,
                        'bounding_box': obj.bounding_box,
                        'frame': base64.b64encode(frame_buffer.getvalue()).decode('utf-8')}
                    out.append(Signal(sig))
                self.logger.debug('found {} objects'.format(len(out)))
                if not self._kill:
                    self.notify_signals(out)
                else:
                    break
            self.camera.close()
            self.logger.debug('camera released')

    def _crop_center(self, image):
        self.logger.debug('cropping image')
        width, height = image.size
        size = min(width, height)
        x, y = (width - size) /2, (height - size) /2
        return image.crop((x, y, x + size, y + size)), (x, y)
