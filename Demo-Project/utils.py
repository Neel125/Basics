"""
This file contains the common function to use in the all projects
"""
from Enums.PalletPositions import PalletPosition
import math
import numpy as np


def get_pallet_poistions(logger, pallet: object, forklift: object):
    """
    Calculate the angle between the pallet and forklift center points to decide the pallet
    is on which side to forklift.
    :param pallet: pallet object
    :param forklift: forklift object
    :return: pallet position index
    """
    pallet_cx, pallet_cy = pallet.distances[-1]
    forklift_cx, forklift_cy = forklift.distances[-1]
    # calculate angle between pallet and forklift center points
    angle = math.atan2(forklift_cy - pallet_cy, forklift_cx - pallet_cx)
    angle_in_degree = math.degrees(angle)
    logger.info("orignial angle before change %s", angle_in_degree)
    if angle_in_degree < 0:
        angle_in_degree = 360 - abs(angle_in_degree)
    # print("angle", angle_in_degree)
    # get the position of pallet accroding to the forklift
    if 0 <= angle_in_degree < 46 or 316 <= angle_in_degree <= 360:
        """pallet is on left side"""
        # print("""pallet is on left side""")
        return PalletPosition.LEFT, angle_in_degree
    elif 46 <= angle_in_degree < 136:
        """pallet is on top side"""
        # print("""pallet is on top side""")
        return PalletPosition.TOP, angle_in_degree
    elif 136 <= angle_in_degree < 226:
        """pallet is on right side"""
        # print("""pallet is on right side""")
        return PalletPosition.RIGHT, angle_in_degree
    elif 226 <= angle_in_degree < 316:
        """pallet is on bottom side"""
        # print("""pallet is on bottom side""")
        return PalletPosition.BOTTOM, angle_in_degree


def is_tracking_id_new(tracing_id, tracked_points, april_tag_id=None) -> object:
    """
    check is current object id is already detected or not
    :param tracing_id: tracking id of the current object
    :param tracked_points: tracked points list
    :return: matched object of the tracked points list
    """
    for element in tracked_points:
        if april_tag_id is not None and april_tag_id != "U":
            if element.april_tag_id == april_tag_id:
                return element
        if element.id == tracing_id:
            return element
    return None


def get_distance(p1: tuple, p2: tuple) -> float:
    """
    calculate euclidean distance of the two points
    :param p1: points 1
    :param p2: points 2
    :return: euclidean distance of the two points
    """
    return math.sqrt(sum([(a - b) ** 2 for a, b in zip(p1, p2)]))


def get_point_distance_to_line(p1: np.array, p2: np.array, p3: np.array) -> float:
    """
    calculate pallet center point distance to line of tracked forklift center points
    :param p1: line points 1
    :param p2: line points 2
    :param p3: pallet center points
    :return: pallet center point ditance to the line of forklift's last points
    """
    return np.linalg.norm(np.cross(p2 - p1, p1 - p3)) / np.linalg.norm(p2 - p1)


def pallet_forklift_edge_distance(logger, pallet: object, forklift: object):
    """
    calculate the distance of the pallet and forklift to check mate/unmate
    :param pallet: pallet object
    :param forklift: forklift object
    :return: distance of the pallet and forklift edges
    """
    # co-ordinates of the pallet and forklift
    pallet_x1, pallet_y1, pallet_x2, pallet_y2 = pallet.bbox[-1]
    forklift_x1, forklift_y1, forklift_x2, forklift_y2 = forklift.bbox[-1]
    dist = 10000000  # max distance
    # get the position of pallet accroding to the forklift
    pallet_position, angle_of_pallet_forklift = get_pallet_poistions(logger, pallet, forklift)
    logger.info("Angle between the Pallet and Forklift %s", angle_of_pallet_forklift)
    logger.info("Pallet positions %s", pallet_position)
    # calculate the distance of pallet and forklift from edges
    if pallet_position == PalletPosition.LEFT:
        """pallet is on left side"""
        dist = forklift_x1 - pallet_x2
    elif pallet_position == PalletPosition.TOP:
        """pallet is on top side"""
        dist = forklift_y1 - pallet_y2
    elif pallet_position == PalletPosition.RIGHT:
        """pallet is on right side"""
        dist = pallet_x1 - forklift_x2
    elif pallet_position == PalletPosition.BOTTOM:
        """pallet is on bottom side"""
        dist = pallet_y1 - forklift_y2
    logger.info("===> Pallet and Forklift edges distance %s <===", dist)
    return dist
