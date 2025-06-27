import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time

from libs.pose_processing import extract_landmarks, compute_angles_and_hip_y
from libs.squat_logic import update_squat_state
from libs.drawing_utils import draw_overlay, draw_gauge
from libs.console_output import log_pose_debug, log_squat_started, log_squat_validated

st.set_page_config(page_title="Squat Counter", layout="centered")
st.title("🏋️ Squat Counter")

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

counter = 0
en_squat = False
current_position = "STANDING"

stframe = st.empty()
prev_time = time.time()

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

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time

        draw_overlay(
            image, (right_angle, left_angle), hip_y, counter, current_position, fps
        )
        draw_gauge(image, hip_y)

        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
        )

    stframe.image(image, channels="BGR")

cap.release()
