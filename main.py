import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import sys
import time
from squat_utils import calculate_angle

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

SQUAT_THRESHOLD = 100
STAND_THRESHOLD = 150
SQUAT_HIP_MIN = 0.70
STAND_HIP_MAX = 0.60

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

        if (
            right_angle < SQUAT_THRESHOLD
            and left_angle < SQUAT_THRESHOLD
            and not en_squat
            and hip_y > SQUAT_HIP_MIN
        ):
            en_squat = True
            current_position = "IN SQUAT"
            print("\n[⏬] Squat position detected (squat started)")
        elif (
            right_angle > STAND_THRESHOLD
            and left_angle > STAND_THRESHOLD
            and en_squat
            and hip_y < STAND_HIP_MAX
        ):
            en_squat = False
            counter += 1
            current_position = "STANDING"
            print(f"\n[✅] Squat validated! Current total: {counter}")
        elif en_squat:
            current_position = "IN SQUAT"
        else:
            current_position = "STANDING"

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time

        cv2.putText(
            image,
            f"Right: {int(right_angle)}°  Left: {int(left_angle)}°",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            image,
            f"hip_y: {hip_y:.3f}",
            (10, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (150, 255, 255),
            2,
        )
        cv2.putText(
            image,
            f"Count: {counter}",
            (10, 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 0, 0),
            2,
        )
        cv2.putText(
            image,
            f"Position: {current_position}",
            (10, 115),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2,
        )
        cv2.putText(
            image,
            f"{int(fps)} FPS",
            (500, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
        )

        gauge_top = 50
        gauge_bottom = 430
        gauge_left = 600
        gauge_width = 20
        height = gauge_bottom - gauge_top

        gauge_y = int(gauge_top + hip_y * height)
        squat_limit_y = int(gauge_top + SQUAT_HIP_MIN * height)
        stand_limit_y = int(gauge_top + STAND_HIP_MAX * height)

        cv2.rectangle(
            image,
            (gauge_left, gauge_top),
            (gauge_left + gauge_width, gauge_bottom),
            (200, 200, 200),
            2,
        )
        cv2.rectangle(
            image,
            (gauge_left + 1, squat_limit_y),
            (gauge_left + gauge_width - 1, gauge_bottom),
            (0, 0, 255),
            -1,
        )
        cv2.rectangle(
            image,
            (gauge_left + 1, gauge_top),
            (gauge_left + gauge_width - 1, stand_limit_y),
            (0, 255, 0),
            -1,
        )
        cv2.rectangle(
            image,
            (gauge_left + 1, stand_limit_y),
            (gauge_left + gauge_width - 1, squat_limit_y),
            (128, 128, 128),
            -1,
        )
        cv2.arrowedLine(
            image,
            (gauge_left - 10, gauge_y),
            (gauge_left, gauge_y),
            (0, 255, 255),
            2,
            tipLength=0.4,
        )

        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
        )

    stframe.image(image, channels="BGR")

cap.release()
