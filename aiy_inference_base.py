from nio import GeneratorBlock
from nio.properties import VersionProperty
from nio.util.discovery import not_discoverable
from nio.util.runner import RunnerStatus
from nio.util.threading import spawn

from .camera import Camera


@not_discoverable
class InferenceBase(GeneratorBlock):

    version = VersionProperty('0.0.1')

    def __init__(self):
        super().__init__()
        self._thread = None

    def configure(self, context):
        super().configure(context)
        self.configure_camera()

    def start(self):
        super().start()
        self._thread = spawn(self.run)

    def stop(self):
        self._thread.join()
        super().stop()

    def configure_camera(self):
        if Camera.configure_camera():
            self.logger.debug('camera configured')
            if self.status.is_set(RunnerStatus.warning):
                self.set_status('ok')
        else:
            # another block has already called Camera.configure_camera()
            self.logger.debug('skipping camera configuration')

    def release_camera(self):
        Camera.get_camera().close()
        self.logger.debug('camera released')

    def reset_camera(self):
        if not self.status.is_set(RunnerStatus.warning):
            self.set_status('warning')
        self.release_camera()
        self.configure_camera()

    def run(self):
        # override and do the things
        raise NotImplementedError
