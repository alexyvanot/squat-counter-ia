import cv2
from libs.config import SQUAT_HIP_MIN, STAND_HIP_MAX


def draw_overlay(image, angles, hip_y, counter, position, fps):
    right_angle, left_angle = angles
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
        f"Position: {position}",
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


def draw_gauge(image, hip_y):
    gauge_top, gauge_bottom = 50, 430
    gauge_left, gauge_width = 600, 20
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
