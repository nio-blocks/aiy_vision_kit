# AIYImageClassifier

Loads the image classification model included in the official SD card image and continuously performs inferences. For every frame of video processed, a list of signals is emitted with `label` and `score` attributes. The signals are ordered from the highest `score` to the lowest, and the number of signals in the list is determined by **Return Top k Predictions**.

## Properties

 * **Return Top k Predictions** (advanced) The number of signals (predictions) to notify for every inference, default `5`

## Commands

None
