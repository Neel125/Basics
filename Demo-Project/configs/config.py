"""
This file manages some constant variables
"""
frame_buffer_threshold_fnp = 75
frame_buffer_threshold_pallet = 60
frame_buffer_threshold_forklift = 75
fnp_buffer = 8
mate_threshold = 170
unmate_threshold = 600
unmate_threshold_max = 1400
pallet_presence_count = 12
forklift_presence_count = 12
missing_pallet_threshold = 2
pallet_inside_door_threshold = 5
max_forklift_area = 1200000           # Only for mezz camera
max_fnp_area = 1200000                # Only for mezz camera 180000
overlap_area_threshold = 20
bbox_cover_by_polygon_thershold = 2   # TODO: Check for small pallets in side PW
fnp_detection_threshold = 2
fnp_detection_threshold_max = 6
forklift_has_pallet_count = 4
forklift_has_pallet_count_max = 10
fnp_detection_mate_threshold = 1
max_region_count = 15
overlap_area_forklift_threshold = 8
overlap_area_fnp_threshold = 8
overlap_area_at_door_threshold = 50
overlap_area_mate_fnp_threshold = 15
fnp_not_detection_count = 40