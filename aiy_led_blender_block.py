import math
from aiy.leds import Leds

from nio import TerminatorBlock
from nio.properties import VersionProperty, Property


class LEDBlender(TerminatorBlock):

    color_a = Property(title='Color A', default='{{ (255, 70, 0) }}')
    color_b = Property(title='Color B', default='{{ (0, 0, 64) }}')
    alpha = Property(title='Alpha', default='{{ $joy_score }}')
    version = VersionProperty('0.0.1')

    def __init__(self):
        super().__init__()
        self._leds = Leds()

    def process_signals(self, signals):
        for signal in signals:
            a = self.color_a(signal)
            b = self.color_b(signal)
            x = self.alpha(signal)
            if x == -1:
               self._leds.update(Leds.rgb_off())
            else:
                self._leds.update(Leds.rgb_on(self._blend(a, b, x)))

    def stop(self):
        self._leds.update(Leds.rgb_off())
        super().stop()

    def _blend(self, a, b, x):
        return tuple([math.ceil(x * a[i] + (1.0 - x) * b[i]) for i in range(3)])
