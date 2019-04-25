from io import BytesIO
from PIL import Image

from nio import Block, Signal
from nio.block.mixins import EnrichSignals
from nio.properties import StringProperty, VersionProperty
from nio.util.runner import RunnerStatus

from .camera import Camera


class AIYCamera(EnrichSignals, Block):

    output_attr = StringProperty(
        title='Outoging Signal Attribute',
        default='image',
        advanced=True,
    )

    version = VersionProperty('0.0.1')

    def __init__(self):
        super().__init__()
        self._frame_buffer = BytesIO()

    def configure(self, context):
        super().configure(context)
        self.configure_camera()

    def process_signals(self, signals):
        self._frame_buffer.truncate(0)
        self._frame_buffer.seek(0)
        Camera.camera.capture(
            self._frame_buffer,
            format='jpeg')
        frame = Image.open(self._frame_buffer)
        output_signals = []
        for signal in signals:
            signal_dict = {self.output_attr(signal): frame}
            output_signal = self.get_output_signal(signal_dict, signal)
            output_signals.append(output_signal)
        self.notify_signals(output_signals)

    def configure_camera(self):
        if Camera.configure_camera():
            self.logger.debug('camera configured')
            if self.status.is_set(RunnerStatus.warning):
                self.set_status('ok')
        else:
            # another block has already called Camera.configure_camera()
            self.logger.debug('skipping camera configuration')
