import sys

def log_pose_debug(right_angle, left_angle, hip_y):
    angle = min(right_angle, left_angle)
    sys.stdout.write(
        f"\r[📊] angles G:{int(left_angle)}° D:{int(right_angle)}° → min:{int(angle)}° | hip_y: {hip_y:.3f}        "
    )
    sys.stdout.flush()


def log_squat_started():
    print("\n[⏬] Squat position detected (squat started)")


def log_squat_validated(counter):
    print(f"\n[✅] Squat validated! Current total: {counter}")
