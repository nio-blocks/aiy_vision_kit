from picamera import PiCamera


class Camera:

    camera = None
    configured = False
    configuring = False

    @classmethod
    def close_camera(cls):
        """ Returns False if camera is already closed, otherwise True."""
        if cls.camera is not None:
            cls.camera.close()
            cls.camera = None
            cls.configured = False
            return True
        else:
            return False

    @classmethod
    def configure_camera(cls):
        """ Returns False if already configuring/ed, otherwise True."""
        if not (cls.configured or cls.configuring):
            cls.configuring = True
            cls.camera = cls.create_camera()
            cls.configuring = False
            cls.configured = True
            return True
        else:
            return False

    @staticmethod
    def create_camera():
        camera = PiCamera()
        camera.sensor_mode = 4
        camera.resolution = (1640, 1232)
        camera.framerate = 15
        camera.hflip = True  # custom
        camera.vflip = True  # custom
        return camera
