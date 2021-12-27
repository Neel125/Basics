from enum import Enum


class FNPStates(Enum):
    """
    FNP states enum class
    """
    IDEAL = 0
    NO_EVENT = 1
    LIFT = 2
    LIFTED = 3
    DROP = 4
    DROPPED = 5
    MAY_DROP = 6
    ALREADY_LIFTED = 7
    IN_DOOR = 8
