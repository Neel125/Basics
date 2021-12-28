from models.pallet import PalletModel
from datetime import timedelta
from utils import *
from configs import config
import math


class PalletManager:
    """
    Pallet manager class to create, remove, manage all pallets objects, check new pallets are on same locations
    """
    def __init__(self, forklift_db, staging_location, camera_type):
        self.tracked_pallets = []
        self.current_pallets = []
        self.forklift_db = forklift_db
        self.camera_type = camera_type
        self.staging_location = staging_location
        self.old_pallets = []

    def create_new_pallet(self, logger, camera_type, tracking_id, x1, y1, x2, y2, ts):
        """
        create new pallet object and append to the list
        :param logger: logger object
        :param camera_type: camera name
        :param tracking_id: pallet tracking id
        :param x1: co-ordinates of the bbox
        :param y1: co-ordinates of the bbox
        :param x2: co-ordinates of the bbox
        :param y2: co-ordinates of the bbox
        :param ts: message time to reuse for mate/unmate events
        :return: 
        """
        pallet = is_tracking_id_new(tracking_id, self.tracked_pallets)
        if pallet is None:
            """
            If pallet is none then current tracking id is not available in the tracked list and create 
            new pallet object.
            """
            pallet = PalletModel(tracking_id, camera_type)
            pallet.append_tracked_data(x1, y1, x2, y2)
            # check if new pallet is detected on the same location
            old_pallet = self.check_new_pallet_on_same_location(logger, pallet.distances[-1][0],
                                                                pallet.distances[-1][1])
            if old_pallet:
                location, is_inside_polygon = self.staging_location.is_pallet_inside_polygon(logger, old_pallet,
                                                                                             camera_type)
                if is_inside_polygon:
                    logger.info("INSIDE ROI FOR RE-ASSIGN THE PALLET DATA FOR SAME LOCATION")
                    self.assign_old_pallet_data(logger, old_pallet, pallet)
            self.append_new_pallet(pallet)
        else:
            """
            Add center points of the current pallet to its tracked path list
            """
            pallet.append_tracked_data(x1, y1, x2, y2)
            if len(pallet.tracked_paths) > 15:
                pallet.tracked_paths.pop(0)
            if len(pallet.distances) > 15:
                pallet.distances.pop(0)
            if len(pallet.bbox) > 15:
                pallet.bbox.pop(0)
        pallet.frame_buffer = 0
        pallet.timestamp = ts - timedelta(hours=5)
        self.current_pallets.append(tracking_id)

    def append_new_pallet(self, pallet):
        self.tracked_pallets.append(pallet)

    def remove_pallet(self, pallet):
        self.tracked_pallets.remove(pallet)

    def get_pallet_object(self, id: str):
        """
        Get pallet object using its tracking id
        :param id: pallet id
        :return: matched pallet object with given tracking id
        """
        for pallet in self.tracked_pallets:
            if pallet.id == id:
                return pallet
        return None

    def check_new_pallet_on_same_location(self, logger, new_pallet_cx, new_pallet_cy):
        """
        :param logger: logger object
        :param new_pallet_cx: 
        :param new_pallet_cy:
        """
        pallets = []
        for pallet in self.tracked_pallets:
            x1, y1, x2, y2 = pallet.bbox[-1]
            if x1 < new_pallet_cx < x2 and y1 < new_pallet_cy < y2:
                pallets.append(pallet)

        logger.info("NEW PALLET LENGTH FOR re-assign data %s", len(pallets))
        if len(pallets) == 1:
            return pallets[0]
        elif len(pallets) > 1:
            # find the minimum distance to all pallet's center points which are inside the new pallets
            min_distance = math.inf
            final_pallet = None
            for pallet in pallets:
                x1, y1, x2, y2 = pallet.bbox[-1]
                temp_center = [(x1 + x2) // 2, (y1 + y2) // 2]
                temp_distance = abs(temp_center[1] - new_pallet_cy) + abs(temp_center[0] - new_pallet_cx)
                if temp_distance < min_distance:
                    min_distance = temp_distance
                    final_pallet = pallet
            logger.info("MIN DISTANCE FOR FINAL PALLET %s", min_distance)
            if final_pallet:
                logger.info("ID %s", final_pallet.id)
                return final_pallet
            else:
                return None
        else:
            return None

    def assign_old_pallet_data(self, logger, old_pallet, current_pallet):
        """
        Assign the old pallet data to new pallet data
        :param old_pallet:
        :param current_pallet:
        """
        current_pallet.tracked_paths = old_pallet.tracked_paths
        current_pallet.distances = old_pallet.distances + current_pallet.distances[-1:]
        current_pallet.bbox = old_pallet.bbox + current_pallet.bbox[-1:]
        current_pallet.old_pallet_id = old_pallet.id
        current_pallet.current_mate_location = old_pallet.current_mate_location
        current_pallet.current_unmate_location = old_pallet.current_unmate_location
        current_pallet.eld = old_pallet.eld
        current_pallet.db_id = old_pallet.db_id
        current_pallet.db_id_journey = old_pallet.db_id_journey
        current_pallet.mate_time = old_pallet.mate_time
        current_pallet.unmate_time = old_pallet.unmate_time
        current_pallet.inside_door_count = old_pallet.inside_door_count
        current_pallet.not_in_fnp = old_pallet.not_in_fnp
        # logger.info("pallet current ELD location %s", current_pallet.eld)
        # logger.info("pallet old eld location %s", old_pallet.eld)
        # logger.info("pallet old DB ID %s %s", old_pallet.db_id, old_pallet.id)
        # logger.info("pallet DB ID %s %s", current_pallet.db_id, current_pallet.id)

    def remove_old_pallets(self):
        """
        remove the old pallets
        :return: 
        """
        for old_pallet in self.old_pallets:
            if old_pallet.id not in self.current_pallets:
                old_pallet.distances.append(None)
                old_pallet.frame_buffer += 1
            if old_pallet.frame_buffer > config.frame_buffer_threshold_pallet:
                self.old_pallets.remove(old_pallet)

    def iterate_over_pallets(self, logger):
        """
        Iterate over the all tracked pallet objects
        :param logger: logger object
        """
        pallet_index = 0
        while pallet_index < len(self.tracked_pallets):
            pallet = self.tracked_pallets[pallet_index]
            if pallet.id not in self.current_pallets:
                """
                If pallet id is not detected in current frame then we add none for that distances list
                and increase the frame buffer. 
                """
                pallet.distances.append(None)
                pallet.frame_buffer += 1
            if pallet.frame_buffer > config.frame_buffer_threshold_pallet:
                """
                If frame buffer is reached to threshold limit then remove the pallet object 
                from tracked forklift object list.
                """
                print("removing pallet", pallet.id, pallet.frame_buffer)
                logger.info("removing pallet %s %s", pallet.id, pallet.frame_buffer)
                self.remove_pallet(pallet)
            else:
                pallet_index += 1
