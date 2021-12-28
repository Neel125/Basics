"""
This file create the forklift model to save the all data of the forklift object
"""


class ForkliftModel:
    """
    Forklift model class to save all data of the current forklift
    """
    def __init__(self, p_id, camera_type):
        self.id = p_id
        self.camera_type = camera_type
        self.tracked_paths = []
        self.distances = []
        self.bbox = []
        self.frame_buffer = 0
        self.timestamp = None
        self.is_in_region = None
    
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
