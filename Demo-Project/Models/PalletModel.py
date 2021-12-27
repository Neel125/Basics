"""
This file create the pallet model to save the all data of the pallet object
"""


class PalletModel:
    """
    Pallet model class to save all data of the current pallet
    """
    def __init__(self, p_id, camera_type):
        self.id = p_id
        self.camera_type = camera_type
        self.tracked_paths = []
        self.distances = []
        self.bbox = []
        self.frame_buffer = 0
        self.old_pallet_id = None
        self.current_mate_location = None
        self.current_unmate_location = None

    def append_tracked_data(self, x1: int, y1: int, x2: int, y2: int):
        """
        append the tracked data to its corresponding lists
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :return:
        """
        self.tracked_paths.append(((x1 + x2) // 2, (y1 + y2) // 2))
        self.bbox.append([x1, y1, x2, y2])
        self.distances.append(((x1 + x2) // 2, (y1 + y2) // 2))
