from ..init.config_init import SQUAT_THRESHOLD, STAND_THRESHOLD, SQUAT_HIP_MIN, STAND_HIP_MAX


def update_squat_state(right_angle, left_angle, hip_y, en_squat):
    if (
        right_angle < SQUAT_THRESHOLD
        and left_angle < SQUAT_THRESHOLD
        and not en_squat
        and hip_y > SQUAT_HIP_MIN
    ):
        return True, "IN SQUAT", True
    elif (
        right_angle > STAND_THRESHOLD
        and left_angle > STAND_THRESHOLD
        and en_squat
        and hip_y < STAND_HIP_MAX
    ):
        return False, "STANDING", True
    elif en_squat:
        return True, "IN SQUAT", False
    else:
        return False, "STANDING", False
