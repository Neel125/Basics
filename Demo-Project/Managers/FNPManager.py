"""
This file manages the all FNP objects like create, remove, manage old FNPs, assign the Pallet and Forklift to FNP etc...
"""
from Models.FNPModel import FNPModel
from Enums.FNPStates import FNPStates
from utils import *
import config
import numpy as np
import math


class FNPManager:
    """
    FNP manager class to create, track and remnove the FNps. Also, it manages the old FNPs and assign the old FNP data
    to the new FNP.
    """
    def __init__(self, pallet_manager, forklift_manager, camera_type, logger, staging_location):
        self.tracked_fnps = []
        self.current_fnps = []
        self.pallet_manager = pallet_manager
        self.forklift_manager = forklift_manager
        self.logger = logger
        self.camera_type = camera_type
        self.staging_location = staging_location

    def create_new_fnp(self, camera_type, tracking_id, april_tag_id, x1, y1, x2, y2, ts):
        """
        create new FNP object and append to the list
        :param camera_type: camera name
        :param tracking_id: tracking id of the current object
        :param april_tag_id: april tag id to uniquley identify the FNP objects
        :param x1: co-ordinates of the bbox
        :param y1: co-ordinates of the bbox
        :param x2: co-ordinates of the bbox
        :param y2: co-ordinates of the bbox
        :param ts: message time to reuse for mate/unmate events
        :return:
        """
        fnp = is_tracking_id_new(tracking_id, self.tracked_fnps, None)
        if fnp is None:
            """
            If fnp is none then current tracking id is not available in the tracked list and create 
            new fnp object.
            """
            self.logger.info("******** Creating New FNP *********")
            fnp = FNPModel(tracking_id, camera_type)
            fnp.append_tracked_data(x1, y1, x2, y2)
            fnp.status = FNPStates.NO_EVENT

            # # assign pallet and forklift id to current fnp which has pallet and forklift inside
            self.assign_forklift_id_to_fnp(fnp, x1, y1, x2, y2)
            self.tracked_fnps.append(fnp)
        else:
            """
            Add center points of the current forklift to its tracked path list
            """
            self.logger.info("******** FNP is available ********* %s %s %s %s %s", x1, y1, x2, y2,fnp.id)
            fnp.append_tracked_data(x1, y1, x2, y2)
            # fnp.last_Drop_pallet_center = ((x1 + x2) // 2, (y1 + y2) // 2)
            if len(fnp.tracked_paths) > 5:
                fnp.tracked_paths.pop(0)
            if len(fnp.distances) > 5:
                fnp.distances.pop(0)
            if len(fnp.bbox) > 5:
                fnp.bbox.pop(0)
        fnp.detection_count += 1
        self.logger.info("=====>>> FNP detection count <<<===== %s %s", fnp.detection_count, fnp.status)
        if config.fnp_detection_threshold < fnp.detection_count < config.fnp_detection_threshold_max \
                and fnp.status == FNPStates.NO_EVENT:
            # assign pallet and forklift id to current fnp which has pallet and forklift inside
            self.assign_pallet_id_to_fnp(fnp, x1, y1, x2, y2)
            # check and assign new fnp is same as old fnp
            if not self.assign_old_fnp_id_to_same_fnp(fnp):
                """
                If forklift has alreay lifted pallet then change fnp status to ALREADY LIFTED 
                """
                self.check_pallet_is_already_lifted_by_forklift(fnp)
        fnp.frame_buffer = 0
        fnp.timestamp = ts
        self.current_fnps.append(fnp.id)
        # check fnp has new pallet and forklift
        self.check_pallet_in_fnp(fnp)
        self.check_forklift_in_fnp(fnp)

    def check_pallet_is_already_lifted_by_forklift(self, fnp):
        """
        CASE: Already lifted by FNP
        if fnp is new and pallet/forklift is already available then check pallet and forklift points length
        if pallet and forklift length reached to threshold count then status will be No-event else status
        will be Already lifted.
        """
        try:
            pallet = self.pallet_manager.get_pallet_object(fnp.pallet_id)
            forklift = self.forklift_manager.get_forklift_object(fnp.forklift_id)
            pallet_length = len(pallet.distances)
            forklift_length = len(forklift.distances)
            self.logger.info("===>>>> pallet length %s %s", pallet_length, forklift_length)
            if pallet_length >= config.pallet_presence_count and \
                    forklift_length >= config.forklift_presence_count:
                # status no event
                fnp.status = FNPStates.NO_EVENT
            else:
                # status already lifted
                if not fnp.is_inside_door and pallet and forklift:
                    fnp.status = FNPStates.ALREADY_LIFTED
        except Exception as e:
            # status already lifted
            if not fnp.is_inside_door and pallet and forklift:
                fnp.status = FNPStates.ALREADY_LIFTED
            self.logger.info("error in already check %s", e)

    def current_pallet_forklift_is_inside_or_not(self, x1: int, y1: int, x2: int, y2: int, cx: int, cy: int):
        """
        check current pallet forklift is inside or not
        :param x1: bbox coordinates
        :param y1: bbox coordinates
        :param x2: bbox coordinates
        :param y2: bbox coordinates
        :param cx: center-x of object
        :param cy: center-y of object
        :return: bool
        """
        if x1 < cx < x2 and y1 < cy < y2:
            return True
        else:
            return False

    def assign_pallet_id_to_fnp(self, fnp, x1: int, y1: int, x2: int, y2: int):
        """
        Assign pallets id to the fnp object which are inside fnp object
        :param fnp: fnp objects
        :param x1: top x co-ordinates
        :param y1: top y co-ordinates
        :param x2: bottom x co-ordinates
        :param y2: bottom y co-ordinates
        :return:
        """
        pallets_inside_fnp = []
        forklift = self.forklift_manager.get_forklift_object(fnp.forklift_id)
        for pallet in self.pallet_manager.tracked_pallets:
            if len(pallet.distances) > 0:
                if pallet.distances[-1] is not None:
                    if self.current_pallet_forklift_is_inside_or_not(x1, y1, x2, y2, pallet.distances[-1][0],
                                                                     pallet.distances[-1][1]):
                        self.logger.info("Pallet inside the FNP %s", pallet.id)
                        pallets_inside_fnp.append(pallet)

        self.logger.info("Pallet length %s", len(pallets_inside_fnp))
        if len(pallets_inside_fnp) > 1 and forklift:
            """
            If multiple pallet detected in current FNP then calculate forklift line distance to the pallet center 
            points and which pallet has mininum distance then assign that pallet id to the FNP.
            """
            distance = []
            # forklift_cx, forklift_cy = forklift.distances[-1]
            for pallet in pallets_inside_fnp:
                self.logger.info("***** Testing the FNP %s", pallet.id)
                location, is_inside = self.staging_location.is_pallet_inside_polygon(self.logger, pallet,
                                                                                     self.camera_type)
                self.logger.info("LOCATION %s %s", location, is_inside)
                if is_inside:
                    if len(forklift.distances) >= 2:
                        if forklift.distances[-1] and forklift.distances[-2]:
                            p1 = np.asarray(forklift.distances[-1])
                            p2 = np.asarray(forklift.distances[-2])
                            p3 = np.asarray(pallet.distances[-1])
                            d = get_point_distance_to_line(p1, p2, p3)
                            self.logger.info("distance of the pallet to line %s %s", d, pallet.id)
                            distance.append(d)
                        else:
                            self.logger.info("filtering the list %s", forklift.distances)
                            last_points = list(filter(lambda x: x is not None, forklift.distances))
                            if len(last_points) >= 2:
                                p1 = np.asarray(last_points[-1])
                                p2 = np.asarray(last_points[-2])
                                p3 = np.asarray(pallet.distances[-1])
                                d = get_point_distance_to_line(p1, p2, p3)
                                self.logger.info("distance of the pallet to line %s %s", d, pallet.id)
                                distance.append(d)
                            else:
                                p1 = np.asarray(last_points[-1])
                                p2 = np.asarray(last_points[-1])
                                p3 = np.asarray(pallet.distances[-1])
                                d = get_point_distance_to_line(p1, p2, p3)
                                self.logger.info("distance of the pallet to line %s %s", d, pallet.id)
                                distance.append(d)
                    else:
                        self.logger.info("forklift.distances < 2 %s", forklift.distances)
                        if forklift.distances[-1]:
                            p1 = np.asarray(forklift.distances[-1])
                            p2 = np.asarray(forklift.distances[-1])
                            p3 = np.asarray(pallet.distances[-1])
                            d = get_point_distance_to_line(p1, p2, p3)
                            self.logger.info("distance of the pallet to line %s %s", d, pallet.id)
                            distance.append(d)
                else:
                    distance.append(math.inf)
            if len(distance) > 0:
                self.logger.info("%s", distance)
                min_value = min(distance)
                self.logger.info("MIN VALUE %s %s", min_value, min_value != math.inf)
                if min_value != math.inf:
                    min_value = distance.index(min_value)
                    # fnp.old_pallet_id = fnp.pallet_id
                    if fnp.pallet_id != pallets_inside_fnp[min_value].id:
                        fnp.old_pallet_id = fnp.pallet_id
                    fnp.pallet_id = pallets_inside_fnp[min_value].id
                    self.logger.info("assigned pallte id to fnp %s", fnp.pallet_id)
                else:
                    self.logger.info("IN ELSE")
                    fnp.pallet_id = None
            else:
                fnp.pallet_id = None
        elif len(pallets_inside_fnp) == 1:
            """
            If only one pallet is detected then assign same pallet id for that FNP
            """
            print("here", pallets_inside_fnp[0], fnp.old_pallet_id, fnp.pallet_id)
            # self.logger.info("***** Testing the FNP %s", pallets_inside_fnp[0].id)
            location, is_inside = self.staging_location.is_pallet_inside_polygon(self.logger, pallets_inside_fnp[0],
                                                                                 self.camera_type)
            self.logger.info("LOCATION %s %s", location, is_inside)
            if is_inside:
            # fnp.old_pallet_id = fnp.pallet_id
                if fnp.pallet_id != pallets_inside_fnp[0].id:
                    fnp.old_pallet_id = fnp.pallet_id
                fnp.pallet_id = pallets_inside_fnp[0].id
        else:
            """
            If not detected any pallet in FNP then assign None
            """
            if fnp.old_pallet_id is None:
                """Old pallet id is none then assign the current pallet id"""
                fnp.old_pallet_id = fnp.pallet_id

    def assign_forklift_id_to_fnp(self, fnp: FNPObject, x1: int, y1: int, x2: int, y2: int):
        """
        Assign forklift id to the fnp object which are inside fnp object
        :param fnp: fnp objects
        :param x1: top x co-ordinates
        :param y1: top y co-ordinates
        :param x2: bottom x co-ordinates
        :param y2: bottom y co-ordinates
        :return:
        """
        forklifts_inside_fnp = []
        for forklift in self.forklift_manager.tracked_forklifts:
            # self.logger.info("FORKLIFTS %s", forklift.id)
            if len(forklift.distances) > 0:
                if forklift.distances[-1] is not None:
                    # self.logger.info("CENTER POINTS %s", forklift.distances[-1])
                    if self.current_pallet_forklift_is_inside_or_not(x1, y1, x2, y2, forklift.distances[-1][0],
                                                                     forklift.distances[-1][1]):
                        forklifts_inside_fnp.append(forklift)

        self.logger.info("FORKLIFT LENGTH FOR FNP assignment %s", len(forklifts_inside_fnp))
        if len(forklifts_inside_fnp) > 1:
            """
            If multiple forklift detected in current FNP then calculate max area cover by forklift 
            for that FNP and assign forklift id which has max area for that FNP.
            """
            area = []
            for current_forklift in forklifts_inside_fnp:
                current_forklift_box = current_forklift.bbox[-1]
                start = (max(current_forklift_box[0], x1), max(y1, current_forklift_box[1]))
                end = (min(x2, current_forklift_box[2]), min(current_forklift_box[3], y2))
                current_area = ((end[0] - start[0]) * (end[1] - start[1])) ^ 2
                area.append(current_area)
            max_value = max(area)
            max_index = area.index(max_value)
            if fnp.forklift_id != forklifts_inside_fnp[max_index].id:
                fnp.old_forklift_id = fnp.forklift_id
            fnp.forklift_id = forklifts_inside_fnp[max_index].id
            fnp.april_tag_id = forklifts_inside_fnp[max_index].april_tag_id
        elif len(forklifts_inside_fnp) == 1:
            """
            If only one forklift is detected then assign same forklift id for that FNP
            """
            # fnp.old_forklift_id = fnp.forklift_id
            if fnp.forklift_id != forklifts_inside_fnp[0].id:
                fnp.old_forklift_id = fnp.forklift_id
            fnp.forklift_id = forklifts_inside_fnp[0].id
            fnp.april_tag_id = forklifts_inside_fnp[0].april_tag_id
            self.logger.info("fnp.forklift_id =  %s", fnp.forklift_id)
        else:
            """
            If not detected any forklift in FNP then assign None
            """
            if fnp.old_forklift_id is None:
                """Old forklift id is none then assign the current forklift id"""
                fnp.old_forklift_id = fnp.forklift_id
            # fnp.forklift_id = None

    def assign_old_fnp_id_to_same_fnp(self, current_fnp: FNPModel) -> bool:
        """
        If fnp object is lost by occulsion but avalible in the current frame then we assign the old fnp id to
        that fnp. Also assign status, distances, bbox
        :param current_fnp:
        :return:
        """
        index = 0
        while index < len(self.tracked_fnps):
            fnp = self.tracked_fnps[index]
            if current_fnp.pallet_id and current_fnp.forklift_id:
                if (fnp.id != current_fnp.id) and (fnp.pallet_id == current_fnp.pallet_id
                                                   or fnp.forklift_id == current_fnp.forklift_id or
                                                   fnp.april_tag_id == current_fnp.april_tag_id):
                    """
                    If the same pallet and forklift are avalible in the previous fnp then assign that values 
                    to the new fnp.
                    """
                    if self.check_old_pallet_is_on_same_location(fnp.pallet_id, current_fnp.pallet_id):
                        self.logger.info("Matched forklift and pallet %s %s", fnp.pallet_id, fnp.forklift_id)
                        self.logger.info("Current forklift and pallet %s %s", current_fnp.pallet_id, current_fnp.forklift_id)
                        current_fnp.old_id = fnp.id
                        current_fnp.status = fnp.status
                        current_fnp.distances = fnp.distances
                        temp_bbox_array = fnp.bbox+current_fnp.bbox
                        current_fnp.bbox = temp_bbox_array
                        current_fnp.old_pallet_id = fnp.pallet_id
                        current_fnp.old_forklift_id = fnp.forklift_id
                        current_fnp.detection_count = fnp.detection_count
                        current_fnp.detect_in_region_count = fnp.detect_in_region_count
                        self.logger.info("============= OLD TO NEW FNP ==============")
                        self.logger.info("Old fnp id %s, New FNP id %s", current_fnp.old_id, current_fnp.id)
                        self.logger.info("Old FNP status %s, New fnp status %s", fnp.status, current_fnp.status)
                        # remove old FNP
                        self.tracked_fnps.remove(fnp)
                        self.logger.info("=====***** Removed FNP %s %s", len(self.tracked_fnps), fnp.id)
                        return True
                    else:
                        index += 1
                else:
                    index += 1
            else:
                index += 1
        return False

    def check_old_pallet_is_on_same_location(self, old_pallet_id, new_pallet_id):
        """
        IF forklift tracking and april id are same for new FNP then check pallet center points to identify
        new FNP is different than old one.
        """
        old_pallet = self.pallet_manager.get_pallet_object(old_pallet_id)
        current_pallet = self.pallet_manager.get_pallet_object(new_pallet_id)
        if current_pallet and old_pallet:
            new_x1, new_y1, new_x2, new_y2 = current_pallet.bbox[-1]
            old_cx, old_cy = list(filter(lambda x: x is not None, old_pallet.distances))[-1]
            if new_x1 < old_cx < new_x2 and new_y1 < old_cy < new_y2:
                return True
            else:
                return False
        return False

    def check_pallet_in_fnp(self, fnp: FNPModel):
        """
        Checking new forklift is losted or not. If forklift is losted then re-assign the forklift id
        :param fnp: FNP object
        :return:
        """
        self.logger.info("***************** Checking Pallet id is Same *******************")
        self.logger.info("fnp pallet ids %s %s", fnp.old_pallet_id, fnp.pallet_id)
        # get old and new pallet objects
        old_pallet = self.pallet_manager.get_pallet_object(fnp.old_pallet_id)
        current_pallet = self.pallet_manager.get_pallet_object(fnp.pallet_id)
        if old_pallet and current_pallet and old_pallet.id != current_pallet.id:
            # assign old data to new pallet
            self.logger.info("Assigning the OLD Pallet Data to New Pallet")
            self.assign_old_pallet_data(fnp, old_pallet, current_pallet)

    def assign_old_pallet_data(self, fnp, old_pallet, current_pallet):
        """
        Assign old pallet data to the new pallet
        :param fnp:
        :param old_pallet:
        :param current_pallet:
        :return:
        """
        fnp.pallet_id = current_pallet.id
        fnp.old_pallet_id = None
        # if current_pallet.old_pallet_id is None:
        current_pallet.tracked_paths = old_pallet.tracked_paths
        current_pallet.distances = old_pallet.distances + current_pallet.distances[-1:]
        current_pallet.bbox = old_pallet.bbox + current_pallet.bbox[-1:]
        current_pallet.old_pallet_id = old_pallet.id
        current_pallet.current_mate_location = old_pallet.current_mate_location
        if old_pallet.current_unmate_location is not None:
            current_pallet.current_unmate_location = old_pallet.current_unmate_location
        current_pallet.eld = old_pallet.eld
        current_pallet.db_id = old_pallet.db_id                   # TODO: stacked pallet
        current_pallet.db_id_journey = old_pallet.db_id_journey   # TODO: stacked pallet
        # old_pallet.db_id = None              # TODO: commented for stacked pallet
        # old_pallet.db_id_journey = None      # TODO: commented for stacked pallet
        self.pallet_manager.old_pallets.append(old_pallet)    # TODO: commented for stacked pallet
        self.logger.info("current pallet id %s", current_pallet.id)
        self.logger.info("old pallet id %s", old_pallet.id)
        self.logger.info("current pallet old ids %s", current_pallet.old_pallet_id)
        self.logger.info("current pallet ELD %s", current_pallet.eld)
        self.logger.info("current pallet Mate Location %s", current_pallet.current_mate_location)
        self.pallet_manager.remove_pallet(old_pallet)    # TODO: commented for stacked pallet

    def check_forklift_in_fnp(self, fnp: FNPModel):
        """
        Checking new forklift is losted or not. If forklift is losted then re-assign the forklift id
        :param fnp: FNP object
        """
        self.logger.info("***************** Checking Forklift id is Same *******************")
        self.logger.info("fnp forklift ids %s %s", fnp.old_forklift_id, fnp.forklift_id)
        # get old and new forklift objects
        old_forklift = self.forklift_manager.get_forklift_object(fnp.old_forklift_id)
        current_forklift = self.forklift_manager.get_forklift_object(fnp.forklift_id)
        if old_forklift and current_forklift and old_forklift.id != current_forklift.id and not fnp.is_forklift_data_updated:
            # assign old data to new forklift
            current_forklift.tracked_paths = old_forklift.tracked_paths
            current_forklift.distances = old_forklift.distances + current_forklift.distances[-1:]
            current_forklift.bbox = old_forklift.bbox + current_forklift.bbox[-1:]
            # current_forklift.april_tag_id = old_forklift.april_tag_id
            current_forklift.old_forklift_id = old_forklift.id
            current_forklift.has_pallet = old_forklift.has_pallet
            current_forklift.lifted_pallet = old_forklift.lifted_pallet
            current_forklift.dropped_pallet = old_forklift.dropped_pallet
            current_forklift.is_mate_done = old_forklift.is_mate_done
            current_forklift.is_unmate_done = old_forklift.is_unmate_done
            current_forklift.pallet_inside_count = old_forklift.pallet_inside_count
            current_forklift.detection_count = old_forklift.detection_count
            current_forklift.not_detected_fnp = old_forklift.not_detected_fnp
            self.logger.info("current forklift id %s", current_forklift.id)
            self.logger.info("old forklift id %s", old_forklift.id)
            self.logger.info("current forklift old ids %s", current_forklift.old_forklift_id)
            self.logger.info("forklift april tags %s %s", current_forklift.april_tag_id, old_forklift.april_tag_id)
            self.logger.info("forklift pallet status %s %s", current_forklift.has_pallet, old_forklift.has_pallet)
            self.logger.info("forklift lifted pallets %s %s", current_forklift.lifted_pallet,
                             old_forklift.lifted_pallet)
            self.logger.info("forklift droppped pallets %s %s", current_forklift.dropped_pallet,
                             old_forklift.dropped_pallet)
            self.logger.info("FORKLIFT DETECTION COUNT %s %s", current_forklift.detection_count,
                             old_forklift.detection_count)
            fnp.is_forklift_data_updated = True
            # self.forklift_manager.remove_forklift(old_forklift)

    def append_new_fnp(self, fnp):
        self.tracked_fnps.append(fnp)

    def remove_fnp(self, fnp):
        self.tracked_fnps.remove(fnp)

    def verify_pallets_inside_fnp(self, fnp: FNPModel, x1: int, y1: int, x2: int, y2: int):
        """
        verify and check the new pallets inside the FNP and assign new pallet id to FNP
        :param fnp: fnp objects
        :param x1: top x co-ordinates
        :param y1: top y co-ordinates
        :param x2: bottom x co-ordinates
        :param y2: bottom y co-ordinates
        :return:
        """
        pallet = self.pallet_manager.get_pallet_object(fnp.pallet_id)
        # if pallet and pallet.distances[-1] is not None:
        if pallet:
            self.logger.info("==> Checking pallet is same or not inside the FNP")
            fnp_x1, fnp_y1, fnp_x2, fnp_y2 = fnp.bbox[-1]
            try:
                is_same_pallet_inside_fnp = \
                    self.current_pallet_forklift_is_inside_or_not(fnp_x1, fnp_y1, fnp_x2, fnp_y2,
                                                                  pallet.distances[-1][0],
                                                                  pallet.distances[-1][1])
                self.logger.info("same pallet is inside the FNP %s", is_same_pallet_inside_fnp)
                if not is_same_pallet_inside_fnp:
                    pallet.not_in_fnp += 1
                    self.logger.info("Same pallet is not inside count %s", pallet.not_in_fnp)
                    if pallet.not_in_fnp > config.missing_pallet_threshold:
                        self.assign_pallet_id_to_fnp(fnp, x1, y1, x2, y2)
                        self.check_pallet_in_fnp(fnp)
            except Exception as e:
                pallet.not_in_fnp += 1
                self.logger.info("Error in check pallet is inside fnp or not %s", e)
                self.logger.info("Pallet not in frame count %s", pallet.not_in_fnp)
                if pallet.not_in_fnp > config.missing_pallet_threshold:
                    self.assign_pallet_id_to_fnp(fnp, x1, y1, x2, y2)
                    self.check_pallet_in_fnp(fnp)
        else:
            self.assign_pallet_id_to_fnp(fnp, x1, y1, x2, y2)
            self.check_pallet_in_fnp(fnp)
