import streamlit as st
import cv2
import numpy as np

from libs.pose_init import get_pose_objects
from libs.camera import init_camera
from libs.timer_utils import FPSTimer
from libs.pose_processing import extract_landmarks, compute_angles_and_hip_y
from libs.squat_logic import update_squat_state
from libs.drawing_utils import draw_overlay, draw_gauge
from libs.con_output import log_pose_debug, log_squat_started, log_squat_validated

st.set_page_config(page_title="Squat Counter", layout="centered")
st.title("🏋️ Squat Counter")

mp_pose, pose, mp_drawing = get_pose_objects()
cap = init_camera()
fps_timer = FPSTimer()

counter = 0
en_squat = False
current_position = "STANDING"

stframe = st.empty()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        st.error("❌ Unable to read from the webcam...")
        break

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.pose_landmarks:
        lm_dict = extract_landmarks(results.pose_landmarks.landmark)
        right_angle, left_angle, hip_y = compute_angles_and_hip_y(lm_dict)

        log_pose_debug(right_angle, left_angle, hip_y)

        en_squat, current_position, validated = update_squat_state(
            right_angle, left_angle, hip_y, en_squat
        )
        if validated and current_position == "STANDING":
            counter += 1
            log_squat_validated(counter)
        elif validated:
            log_squat_started()

        fps = fps_timer.update()

        draw_overlay(
            image, (right_angle, left_angle), hip_y, counter, current_position, fps
        )
        draw_gauge(image, hip_y)

        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
        )

    stframe.image(image, channels="BGR")

cap.release()
