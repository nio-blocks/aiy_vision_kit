from threading import Event
from unittest.mock import MagicMock, Mock, patch

from nio import Signal
from nio.testing.block_test_case import NIOBlockTestCase

# mock modules which can't be installed on other platforms
# before importing block classes
import sys
sys.modules['aiy'] = Mock()
sys.modules['aiy.leds'] = Mock()
sys.modules['aiy.vision'] = Mock()
sys.modules['aiy.vision.inference'] = MagicMock()  # used in a context manager
sys.modules['aiy.vision.models'] = Mock()
sys.modules['picamera'] = Mock()
# import block classes
from ..aiy_camera_block import AIYCamera
from ..aiy_inference_base import InferenceBase


class SimpleInferenceBlock(InferenceBase):

    def __init__(self):
        super().__init__()
        self.stop_event = Event()

    def run(self):
        self.stop_event.wait()
        self.release_camera()

    def stop(self):
        self.stop_event.set()
        super().stop()

@patch(AIYCamera.__module__ + '.Image')
class testAIYCamera(NIOBlockTestCase):

    # create a ref to a dummy camera object
    dummy_camera = Mock()
    sys.modules['picamera'].PiCamera.return_value = dummy_camera

    def test_shared_camera(self, mock_Image):
        # create two blocks that would use the same PiCamera
        camera_block = AIYCamera()
        inference_block = SimpleInferenceBlock()

        # confgure blocks
        camera_config = {
            'enrich': {'exclude_existing': False},
        }
        self.configure_block(camera_block, camera_config)
        self.configure_block(inference_block, {})
        # assert only one call to Camera.create_camera
        self.assertEqual(sys.modules['picamera'].PiCamera.call_count, 1)
        # assert settings for loaded models
        self.assertEqual(self.dummy_camera.sensor_mode, 4)
        self.assertEqual(self.dummy_camera.resolution, (1640, 1232))
        self.assertEqual(self.dummy_camera.framerate, 15)

        # start the blocks
        camera_block.start()
        inference_block.start()

        # capture an image
        camera_block.process_signals([
            Signal({
                'pi': 3.14,
            }),
        ])
        self.assert_num_signals_notified(1)
        self.assert_last_signal_list_notified([
            Signal({
                'image': mock_Image.open.return_value,
                'pi': 3.14,
            }),
        ])

        # stop the blocks
        camera_block.stop()
        inference_block.stop()
        # assert only one call to Camera.camera.close
        self.assertEqual(self.dummy_camera.close.call_count, 1)
