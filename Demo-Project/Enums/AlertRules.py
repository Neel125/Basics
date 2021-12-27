from enum import Enum


class AlertRule(Enum):
    NO_ALERT = "No Alert"
    UNEXPECTED_MOVE = "Unexpected Move"
    OFF_CAMERA_MATE = "Off-Camera Mate"
    OFF_CAMERA_UNMATE = "Off-Camera Unmate"
    NO_ELD = "ELD not assigned"
    WRONG_ELD = "Wrong ELD assigned"
    UNKNOWN_LOAD = "Unknown Load"
    STACKED_PALLET_SAME_ELD = "Stacked Pallet Same ELD"
    STACKED_PALLET_DIFFERENT_ELD = "Stacked Pallet Different ELD"
