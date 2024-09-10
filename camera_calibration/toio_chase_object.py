import asyncio
import cv2
import numpy as np
from cv2 import aruco
from toio import *
import sys
import ctypes
import time
from collections import deque
import math

def init_com():
    if sys.platform == "win32":
        ctypes.windll.ole32.CoInitializeEx(None, 0)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary

def get_mat_corner(corners, marker_id):
    if marker_id == 0:  # 左上
        return corners[0][0]
    elif marker_id == 1:  # 右上
        return corners[0][1]
    elif marker_id == 2:  # 左下
        return corners[0][3]
    elif marker_id == 3:  # 右下
        return corners[0][2]

def rotation_vector_to_euler(rvec):
    R, _ = cv2.Rodrigues(rvec)
    sy = np.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
    singular = sy < 1e-6
    if not singular:
        x = np.arctan2(R[2,1] , R[2,2])
        y = np.arctan2(-R[2,0], sy)
        z = np.arctan2(R[1,0], R[0,0])
    else:
        x = np.arctan2(-R[1,2], R[1,1])
        y = np.arctan2(-R[2,0], sy)
        z = 0
    return np.array([x, y, z])

def notification_handler(payload: bytearray):
    id_info = IdInformation.is_my_data(payload)
    print(f"Notification received: {str(id_info)}")

async def move_toio(cube, x, y, angle):
    print(f"Moving toio to position: ({x}, {y}, {angle}°)")
    try:
        await cube.api.motor.motor_control_target(
            timeout=5,
            movement_type=MovementType.Linear,
            speed=Speed(
                max=100, speed_change_type=SpeedChangeType.AccelerationAndDeceleration
            ),
            target=TargetPosition(
                cube_location=CubeLocation(point=Point(x=x, y=y), angle=angle),
                rotation_option=RotationOption.AbsoluteOptimal,
            ),
        )
        print("Movement command sent successfully")
    except Exception as e:
        print(f"Error moving toio: {e}")

def adjust_toio_angle(marker_angle):
    return marker_angle  # マーカーと同じ角度を返す

def calculate_toio_position(marker_x, marker_y, marker_angle, distance=40):
    marker_angle_rad = math.radians(marker_angle)
    dx = -distance * math.cos(marker_angle_rad)  # マイナスをつけて後ろに移動
    dy = -distance * math.sin(marker_angle_rad)  # マイナスをつけて後ろに移動
    toio_x = marker_x + dx
    toio_y = marker_y + dy
    return int(toio_x), int(toio_y)

async def main():
    init_com()

    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cap.set(cv2.CAP_PROP_EXPOSURE, -1)

    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    marker_size = 0.05

    camera_matrix = np.load("mtx.npy")
    dist_coeffs = np.load("dist.npy")

    mat_tl, mat_tr, mat_br, mat_bl = (98, 142), (402, 142), (402, 358), (98, 358)
    mat_corners_real = np.float32([mat_tl, mat_tr, mat_br, mat_bl])

    corner_marker_ids = set([0, 1, 2, 3])
    target_marker_id = 5  # ターゲットマーカーIDを4に設定

    parameters = aruco.DetectorParameters()
    parameters.adaptiveThreshWinSizeMin = 3
    parameters.adaptiveThreshWinSizeMax = 23
    parameters.adaptiveThreshWinSizeStep = 10
    parameters.adaptiveThreshConstant = 7
    parameters.minMarkerPerimeterRate = 0.03
    parameters.maxMarkerPerimeterRate = 0.3
    parameters.polygonalApproxAccuracyRate = 0.03
    parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX

    prev_frame_time = 0
    new_frame_time = 0

    marker_positions = {}
    history_length = 10
    marker_presence = {}

    try:
        async with ToioCoreCube() as cube:
            print("Connected to toio")
            await cube.api.motor.register_notification_handler(notification_handler)
            
            last_position = None
            last_angle = None
            last_move_time = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break

                preprocessed = preprocess_image(frame)

                new_frame_time = time.time()
                fps = int(1/(new_frame_time-prev_frame_time))
                prev_frame_time = new_frame_time

                corners, ids, rejected = aruco.detectMarkers(preprocessed, dictionary, parameters=parameters)

                if ids is not None:
                    mat_corners = []
                    for i, id in enumerate(ids):
                        if id[0] in corner_marker_ids:
                            mat_corners.append(get_mat_corner(corners[i], id[0]))

                        marker_presence[id[0]] = time.time()

                    if len(mat_corners) == 4:
                        mat_corners = np.float32(mat_corners)
                        mat_corners = order_points(mat_corners)
                        
                        perspective_matrix = cv2.getPerspectiveTransform(mat_corners, mat_corners_real)

                        for i in range(len(ids)):
                            if ids[i][0] not in corner_marker_ids:
                                rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners[i], marker_size, camera_matrix, dist_coeffs)
                                
                                euler_angles = rotation_vector_to_euler(rvec)
                                yaw_degree = np.degrees(euler_angles[2])
                                marker_angle = (yaw_degree - 90) % 360 
                                toio_angle = adjust_toio_angle(marker_angle)
                                print(toio_angle)
                                
                                marker_center = corners[i][0].mean(axis=0)
                                marker_toio = cv2.perspectiveTransform(np.array([[marker_center]]), perspective_matrix)[0][0]
                                
                                if ids[i][0] not in marker_positions:
                                    marker_positions[ids[i][0]] = deque(maxlen=history_length)
                                marker_positions[ids[i][0]].append(marker_toio)
                                
                                avg_position = np.mean(marker_positions[ids[i][0]], axis=0)
                                
                                cv2.putText(frame, f"ID: {ids[i][0]}, X: {avg_position[0]:.0f}, Y: {avg_position[1]:.0f}, Marker Angle: {marker_angle:.0f}°, Toio Angle: {toio_angle:.0f}°", 
                                            (10, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                
                                print(f"Marker ID {ids[i][0]}: X = {avg_position[0]:.0f}, Y = {avg_position[1]:.0f}, Marker Angle = {marker_angle:.0f}°, Toio Angle = {toio_angle:.0f}°")

                                if ids[i][0] == target_marker_id:
                                    toio_x, toio_y = calculate_toio_position(avg_position[0], avg_position[1], marker_angle, distance=35)
                                    target_position = (toio_x, toio_y)
                                    target_angle = int(toio_angle)
                                    current_time = asyncio.get_event_loop().time()
                                    
                                    position_threshold = 5
                                    angle_threshold = 5
                                    position_changed = (last_position is None or 
                                                        abs(target_position[0] - last_position[0]) > position_threshold or 
                                                        abs(target_position[1] - last_position[1]) > position_threshold)
                                    angle_changed = (last_angle is None or 
                                                     abs(target_angle - last_angle) > angle_threshold)
                                    
                                    if position_changed or angle_changed:
                                        print(f"Marker position or angle changed. Toio target: {target_position}, {target_angle}°")
                                        last_position = target_position
                                        last_angle = target_angle
                                        last_move_time = current_time + 3  # 3秒後に移動
                                    
                                    if current_time >= last_move_time:
                                        print(f"Moving toio to position {target_position}, angle {target_angle}°")
                                        await move_toio(cube, target_position[0], target_position[1], target_angle)
                                        last_move_time = current_time + 3  # 次の移動まで3秒待つ

                        aruco.drawDetectedMarkers(frame, corners, ids)

                        for corner in mat_corners:
                            cv2.circle(frame, tuple(corner.astype(int)), 5, (0, 255, 0), -1)

                current_time = time.time()
                for marker_id, last_seen in list(marker_presence.items()):
                    if current_time - last_seen > 2.0:
                        cv2.putText(frame, f"Lost Marker ID: {marker_id}", (10, 160 + 30 * marker_id), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                cv2.putText(frame, f"FPS: {fps}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                num_markers = 0 if ids is None else len(ids)
                cv2.putText(frame, f"Detected Markers: {num_markers}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                cv2.putText(frame, f"Rejected Candidates: {len(rejected)}", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                cv2.imshow('Detected Markers and Mat', frame)
                cv2.imshow('Preprocessed Image', preprocessed)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(main())