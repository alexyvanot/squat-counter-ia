import mediapipe as mp

def get_pose_objects():
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils
    return mp_pose, pose, mp_drawing
