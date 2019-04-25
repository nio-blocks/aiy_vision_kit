from unittest.mock import MagicMock, Mock

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
# block classes
from ..aiy_camera_block import AIYCamera
from ..aiy_nature_explorer_block import NatureExplorer


class testTheThings(NIOBlockTestCase):

    # create a ref to a dummy camera object
    dummy_camera = Mock()
    sys.modules['picamera'].PiCamera.return_value = dummy_camera

    def test_thing_one(self):
        # create two blocks that would use the same PiCamera
        camera_block = AIYCamera()
        camera_config = {}
        inference_block = NatureExplorer()
        inference_config = {}

        # confgure blocks and assert shared camera object
        self.configure_block(camera_block, camera_config)
        self.configure_block(inference_block, inference_config)
        self.assertEqual(sys.modules['picamera'].PiCamera.call_count, 1)
        self.assertEqual(self.dummy_camera.sensor_mode, 4)
        self.assertEqual(self.dummy_camera.resolution, (1640, 1232))
        self.assertEqual(self.dummy_camera.framerate, 15)
        self.assertTrue(self.dummy_camera.hflip)  # custom
        self.assertTrue(self.dummy_camera.vflip)  # custom

        # start the blocks
        camera_block.start()
        inference_block.start()

        # stop the blocks
        camera_block.stop()
        inference_block.stop()
