from aiy.toneplayer import TonePlayer

from nio import TerminatorBlock
from nio.properties import VersionProperty, Property


class VisionKitBuzzer(TerminatorBlock):

    sound = Property(title="Sound")
    version = VersionProperty('0.0.1')

    def __init__(self):
        super().__init__()
        self._tone_player = TonePlayer(gpio=22, bpm=10)

    def process_signals(self, signals):
        for signal in signals:
            sound = self.sound(signal)
            self._tone_player.play(*sound)
