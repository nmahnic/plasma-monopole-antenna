"""
Animation Constants.
"""

class AnimationConstants:
    """
    Define values to be used when generating
    animation.
    """

    def __init__(self) -> None:
        """
        Initializer.

        Attributes:
        dots_per_inches [int]: dots per inches
        animation_interval [int]: minimum time between
            each frame, in milliseconds.
        """
        self.dots_per_inches = 150
        self.animation_interval = 15
