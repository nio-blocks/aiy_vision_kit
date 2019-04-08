from aiy.vision.inference import CameraInference
from aiy.vision.models import face_detection

from nio import Signal
from nio.util.runner import RunnerStatus

from .aiy_inference_base import InferenceBase


class JoyDetection(InferenceBase):

    def _run(self):
        while not self._kill:
            try:
                self.logger.debug('loading inference model ...')
                with CameraInference(face_detection.model()) as inference:
                    self.logger.debug('running inference ...')
                    for result in inference.run():
                        faces = face_detection.get_faces(result)
                        # if faces:
                        #     self.logger.debug(
                        #         'found {} faces'.format(len(faces)))
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
                self.logger.exception('failed to get inference result!')
                if not self.status.is_set(RunnerStatus.warning):
                    self.set_status('warning')
                self._release_camera()
                self._configure_camera()
        self._release_camera()
