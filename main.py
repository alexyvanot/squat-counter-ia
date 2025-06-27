import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import sys
import time

from libs.squat_utils import calculate_angle
from libs.squat_logic import update_squat_state
from libs.drawing_utils import draw_overlay, draw_gauge

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
        lm = results.pose_landmarks.landmark

        right_angle = calculate_angle(
            [
                lm[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                lm[mp_pose.PoseLandmark.RIGHT_HIP.value].y,
            ],
            [
                lm[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                lm[mp_pose.PoseLandmark.RIGHT_KNEE.value].y,
            ],
            [
                lm[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                lm[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y,
            ],
        )
        left_angle = calculate_angle(
            [
                lm[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                lm[mp_pose.PoseLandmark.LEFT_HIP.value].y,
            ],
            [
                lm[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                lm[mp_pose.PoseLandmark.LEFT_KNEE.value].y,
            ],
            [
                lm[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                lm[mp_pose.PoseLandmark.LEFT_ANKLE.value].y,
            ],
        )

        angle = min(right_angle, left_angle)
        hip_y = (
            lm[mp_pose.PoseLandmark.LEFT_HIP.value].y
            + lm[mp_pose.PoseLandmark.RIGHT_HIP.value].y
        ) / 2

        sys.stdout.write(
            f"\r[DEBUG] angles G:{int(left_angle)}° D:{int(right_angle)}° → min:{int(angle)}° | hip_y: {hip_y:.3f}        "
        )
        sys.stdout.flush()

        en_squat, current_position, validated = update_squat_state(
            right_angle, left_angle, hip_y, en_squat
        )
        if validated and current_position == "STANDING":
            counter += 1
            print(f"\n[✅] Squat validated! Current total: {counter}")
        elif validated:
            print("\n[⏬] Squat position detected (squat started)")

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
