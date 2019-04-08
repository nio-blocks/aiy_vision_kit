from picamera import PiCamera

from aiy.leds import Leds
from aiy.vision.inference import CameraInference

from nio import GeneratorBlock
from nio.properties import IntProperty, VersionProperty
from nio.util.discovery import not_discoverable
from nio.util.runner import RunnerStatus
from nio.util.threading import spawn
from nio.signal.base import Signal


@not_discoverable
class InferenceBase(GeneratorBlock):

    privacy_led_brightness = IntProperty(
        title='Privacy LED Brightness (0-255)',
        default=255,
        advanced=True)
    version = VersionProperty('0.0.1')

    def __init__(self):
        super().__init__()
        self.camera = None
        self._leds = Leds()
        self._kill = False
        self._thread = None

    def configure(self, context):
        super().configure(context)
        self._configure_camera()

    def start(self):
        super().start()
        self._thread = spawn(self._run)

    def stop(self):
        super().stop()
        self._kill = True
        self.logger.debug('killing secondary thread ...')
        self._thread.join()

    def _configure_camera(self):
        try:
            self.camera = PiCamera()
            self.camera.sensor_mode = 4
            self.camera.resolution = (1640, 1232)
            self.camera.framerate = 15
            brightness = self.privacy_led_brightness()
            if brightness > 0:
                self._leds.update(Leds.privacy_on(brightness=brightness))
            self.logger.debug('camera configured')
            if self.status.is_set(RunnerStatus.warning):
                self.set_status('ok')
        except:
            self.logger.exception('failed to configure camera!')

    def _release_camera(self):
        try:
            self.camera.close()
            self._leds.update(Leds.privacy_off())
            self.logger.debug('camera released')
        except:
            self.logger.exception('failed to close camera!')

    def _run(self):
        # override and do the things
        raise NotImplementedError
