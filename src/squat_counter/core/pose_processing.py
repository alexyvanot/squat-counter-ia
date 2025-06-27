import mediapipe as mp
from ..core.squat_utils import calculate_angle

mp_pose = mp.solutions.pose


def extract_landmarks(landmarks):
    return {
        "left_hip": landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        "right_hip": landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        "left_knee": landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
        "right_knee": landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
        "left_ankle": landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value],
        "right_ankle": landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value],
    }


def compute_angles_and_hip_y(lm_dict):
    right_angle = calculate_angle(
        [lm_dict["right_hip"].x, lm_dict["right_hip"].y],
        [lm_dict["right_knee"].x, lm_dict["right_knee"].y],
        [lm_dict["right_ankle"].x, lm_dict["right_ankle"].y],
    )
    left_angle = calculate_angle(
        [lm_dict["left_hip"].x, lm_dict["left_hip"].y],
        [lm_dict["left_knee"].x, lm_dict["left_knee"].y],
        [lm_dict["left_ankle"].x, lm_dict["left_ankle"].y],
    )
    hip_y = (lm_dict["left_hip"].y + lm_dict["right_hip"].y) / 2
    return right_angle, left_angle, hip_y
