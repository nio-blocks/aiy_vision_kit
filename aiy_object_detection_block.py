from io import BytesIO

from PIL import Image
from picamera import PiCamera

from aiy.vision.inference import CameraInference
from aiy.vision.models import object_detection

from nio import GeneratorBlock
from nio.properties import VersionProperty, FloatProperty
from nio.util.threading import spawn
from nio.signal.base import Signal


class ObjectDetection(GeneratorBlock):

    version = VersionProperty('0.0.1')
    min_confidence = FloatProperty(title='Minimum Confidence', default=0.3)

    def __init__(self):
        super().__init__()
        self.frame_buffer = BytesIO()
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
        with CameraInference(object_detection.model()) as inference:
            self.logger.debug('running inference loop...')
            for result in inference.run():
                self.frame_buffer.truncate(0)
                self.frame_buffer.seek(0)
                objects = object_detection.get_objects(
                    result, self.min_confidence())
                if objects:
                    self.logger.debug('capturing represtantive frame')
                    self.camera.capture(frame_buffer, format='jpeg')
                    self.frame_buffer.seek(0)
                    self.logger.debug('found {} objects'.format(len(objects)))
                out = []
                for obj in objects:
                    sig = {
                        'kind': obj._LABELS[obj.kind],
                        'bounding_box': obj.bounding_box,
                        'confidence': obj.score,
                        'image': Image.open(self.frame_buffer).convert('RGB')}
                    out.append(Signal(sig))
                if not self._kill:
                    self.notify_signals(out)
                else:
                    break
            self.camera.close()
            self.frame_buffer.close()
            self.logger.debug('camera released')
