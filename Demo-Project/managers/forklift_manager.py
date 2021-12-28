"""
This file manages the all forklift objects like create, remove and manage old forklifts, etc...
"""
from models.pallet import PalletModel
from models.forklift import ForkliftModel


class ForkliftManager:
    """
    Forklift manager class to create, remove and manage all forklift objects
    """
    def __init__(self, fnp_db):
        self.tracked_forklifts = []
        self.current_forklifts = []
        self.fnp_db = fnp_db

    def create_new_forklift(self, logger, camera_type, april_tag_id, tracking_id, x1, y1, x2, y2, ts,
                            fnp_manager):
        """
        create new forklift object and append to the list
        :param logger: logger object
        :param camera_type: camera name
        :param april_tag_id: april tag id to save identify the forklift uniquely
        :param tracking_id: forklift tracking id
        :param x1: co-ordinates of the bbox
        :param y1: co-ordinates of the bbox
        :param x2: co-ordinates of the bbox
        :param y2: co-ordinates of the bbox
        :param ts: message time to reuse for mate/unmate events
        :param fnp_manager: FNP Manager class object
        :return:
        """
        forklift = is_tracking_id_new(tracking_id, self.tracked_forklifts, april_tag_id)
        forklift_db_data = {
            "forklift_id": tracking_id,
            "current_camera": camera_type,
            "april_id": april_tag_id,
            "is_lifted": "",
            "lifted_pallet": "",
            "dropped_pallet": "",
            "mate_location": "",
            "unmate_location": "",
            "eld": "",
            "pallet_id": "",
            "is_pallet": "",
            "pallet": ""
        }
        if forklift is None:
            """
            If forklift is none then current tracking id is not available in the tracked list and create 
            new forklift object.
            """
            forklift = ForkliftModel(tracking_id, april_tag_id, camera_type)
            forklift.append_tracked_data(x1, y1, x2, y2)
            self.append_new_forklift(forklift)

            if april_tag_id != "U":
                self.assign_forklift_db_data_to_object(logger, forklift, april_tag_id, forklift_db_data,
                                                       tracking_id, camera_type)
        else:
            """
            Add center points of the current forklift to its tracked path list
            """
            forklift.append_tracked_data(x1, y1, x2, y2)
            if len(forklift.tracked_paths) > 15:
                forklift.tracked_paths.pop(0)
            if len(forklift.distances) > 15:
                forklift.distances.pop(0)
            if len(forklift.bbox) > 15:
                forklift.bbox.pop(0)
            logger.info("OLD FORKLIFT ID AND TRCKING ID %s %s", forklift.id, tracking_id)
            if forklift.id != tracking_id:
                logger.info("assigning new forklift data on the april tag")
                self.assign_new_forlift_to_old_on_april_tag_detection(logger, tracking_id, forklift.id)
                old_forklift_id = forklift.id
                forklift.id = tracking_id
                fnp_manager.find_and_assign_forklift_id_to_fnp(old_forklift_id)
                logger.info("AFTER TRCKING ID %s %s", forklift.id, tracking_id)
            if april_tag_id != "U":
                self.assign_forklift_db_data_to_object(logger, forklift, april_tag_id, forklift_db_data,
                                                       tracking_id, camera_type)
        forklift.frame_buffer = 0
        forklift.timestamp = ts
        if forklift.april_tag_id == "U" and april_tag_id != "U":
            forklift.april_tag_id = april_tag_id
        self.current_forklifts.append(tracking_id)

    def get_forklift_with_april_tag(self, april_tag):
        """
        return forklift with matched april tag
        :param april_tag: april tag id
        :return: matched forklift of none
        """
        for forklift in self.tracked_forklifts:
            if forklift.april_tag_id == april_tag:
                return forklift
        return None

    def append_new_forklift(self, forklift):
        self.tracked_forklifts.append(forklift)

    def remove_forklift(self, forklift):
        self.tracked_forklifts.remove(forklift)

    def get_forklift_object(self, id: str):
        """
        Get forklift object using id
        :param id: pallet id
        :return: matched object of the tracked forklift points list
        """
        for forklift in self.tracked_forklifts:
            if forklift.id == id:
                return forklift
        return None

    def assign_forklift_db_data_to_object(self, logger, forklift, april_tag_id, forklift_db_data,
                                          tracking_id, camera_type):
        """
        This function assign the all db data to forklift object
        :param logger:
        :param forklift:
        :param april_tag_id:
        :param forklift_db_data:
        :param tracking_id:
        :param camera_type:
        :return:
        """
        forklift_data = self.fnp_db.fetch_forklift_with_april_tag(april_tag_id)
        logger.info("In creating forklift")
        logger.info("forklift data %s", forklift_data)
        if len(forklift_data) > 0:
            forklift_data[0]["forklift_id"] = tracking_id
            forklift_data[0]["current_camera"] = camera_type
            forklift_data[0]["current_location"] = forklift.bbox[-1]
            self.fnp_db.update_or_insert_forklift(forklift_data[0], logger)
            forklift.db_id = forklift_data[0]["_id"]
            if forklift_data[0]["is_lifted"]:
                forklift.has_pallet = forklift_data[0]["is_lifted"]
            # forklift.lifted_pallet = forklift_data[0]["lifted_pallet"]
            logger.info("forklift is lifted in db %s", forklift_data[0]["is_lifted"])
            logger.info("forklift is lifted in object %s", forklift.has_pallet)
            if forklift.has_pallet and forklift_data[0]["is_lifted"]:
                forklift.is_mate_done = True
        else:
            forklift_db_data["current_location"] = forklift.bbox[-1]
            logger.info("Insert new forklift %s", forklift_db_data)
            forklift.db_id = self.fnp_db.insert_new_forklift(None, forklift_db_data)
