from picamera import PiCamera


class Camera:

    _camera = None
    configured = False
    configuring = False

    @classmethod
    def get_camera(cls):
        return cls._camera

    @classmethod
    def set_camera(cls, camera_instance):
        cls._camera = camera_instance

    @classmethod
    def close_camera(cls):
        cls._camera.close()

    @classmethod
    def configure_camera(cls):
        """ Returns False if already configuring/ed, otherwise True."""
        if not (cls.configured or cls.configuring):
            cls.configuring = True
            cls.set_camera(PiCamera())
            cls._camera.sensor_mode = 4
            cls._camera.resolution = (1640, 1232)
            cls._camera.framerate = 15
            cls._camera.hflip = True  # custom
            cls._camera.vflip = True  # custom
            cls.configuring = False
            cls.configured = True
            return True
        else:
            return False
