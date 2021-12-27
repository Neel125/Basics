"""
This file create the FNP model to save the all data of the FNP object
"""


class FNPModel:
    """
    FNP model class to save all data of the current FNP object
    """
    def __init__(self, fnp_id, camera_type):
        self.id = fnp_id
        self.camera_type = camera_type
        self.tracked_paths = []
        self.forklift_id = None
        self.pallet_id = None
        self.distances = []
        self.old_id = None
        self.status = None
        self.frame_buffer = 0
        self.bbox = []

    def append_tracked_data(self, x1: int, y1: int, x2: int, y2: int):
        """
        append tracked points
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :return:
        """
        self.tracked_paths.append(((x1 + x2) // 2, (y1 + y2) // 2))
        self.bbox.append([x1, y1, x2, y2])
        self.distances.append(((x1 + x2) // 2, (y1 + y2) // 2))
