try:
    ModuleNotFoundError  # added in py3.6
except:
    # make it an alias of ImportError
    ModuleNotFoundError = ImportError
try:
    from aiy.vision.inference import CameraInference
    from aiy.vision.models import face_detection
except ModuleNotFoundError:
    # not available on all platforms
    pass

from nio import Signal
from nio.properties import VersionProperty
from .aiy_inference_base import InferenceBase


class AIYJoyDetector(InferenceBase):

    version = VersionProperty('0.1.0')

    def start(self):
        self._running = True
        super().start()

    def stop(self):
        self._running = False
        self.logger.debug('stopping child thread ...')
        super().stop()

    def run(self):
        while self._running:
            try:
                self.logger.debug('loading inference model ...')
                with CameraInference(face_detection.model()) as inference:
                    self.logger.debug('running inference ...')
                    for result in inference.run():
                        faces = face_detection.get_faces(result)
                        if faces:
                            self.logger.debug(
                                'found {} faces'.format(len(faces)))
                        outgoing_signals = []
                        for face in faces:
                            signal_dict = {
                                'bounding_box': face.bounding_box,
                                'face_score': face.face_score,
                                'joy_score': face.joy_score,
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
