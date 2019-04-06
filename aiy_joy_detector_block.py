from picamera import PiCamera

from aiy.vision.inference import CameraInference
from aiy.vision.models import face_detection

from nio import GeneratorBlock
from nio.properties import VersionProperty
from nio.util.threading import spawn
from nio.signal.base import Signal


class JoyDetection(GeneratorBlock):

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
        self._thread = spawn(self._run)

    def stop(self):
        super().stop()
        self._kill = True
        self.logger.debug('killing secondary thread')
        self._thread.join()

    def _run(self):
        while not self._kill
            try:
                self.logger.debug('loading inference model')
                with CameraInference(face_detection.model()) as inference:
                    for result in inference.run():
                        self.logger.debug('running inference...')
                        faces = face_detection.get_faces(result)
                        self.logger.debug('found {} faces'.format(len(faces)))
                        out = []
                        for face in faces:
                            sig = {
                                'bounding_box': face.bounding_box,
                                'face_score': face.face_score,
                                'joy_score': face.joy_score,
                            }
                            out.append(Signal(sig))
                        if not self._kill:
                            self.notify_signals(out)
                        else:
                            break
            except:
                self.logger.exception('something has gone wrong!')
        self.camera.close()
        self.logger.debug('camera released')
