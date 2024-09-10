import cv2
import numpy as np
from cv2 import aruco
import time
from collections import deque
import math

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

def calculate_angle(corners):
    # マーカーの上辺の中点と下辺の中点を計算
    top_mid = (corners[0][0] + corners[1][0]) / 2, (corners[0][1] + corners[1][1]) / 2
    bottom_mid = (corners[2][0] + corners[3][0]) / 2, (corners[2][1] + corners[3][1]) / 2
    
    # 角度を計算（ラジアン）
    angle = math.atan2(bottom_mid[1] - top_mid[1], bottom_mid[0] - top_mid[0])
    
    # ラジアンから度に変換し、toioの座標系に合わせて調整
    angle_deg = (angle * 180 / math.pi + 90) % 360
    
    return angle_deg

def main():
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cap.set(cv2.CAP_PROP_EXPOSURE, -1)

    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    marker_size = 0.05  # 実際のサイズに合わせて調整が必要かもしれません

    camera_matrix = np.load("mtx.npy")
    dist_coeffs = np.load("dist.npy")

    mat_corners_real = np.float32([(402, 142), (98, 142), (402, 358), (98, 358)])  # 右上、左上、右下、左下
    corner_marker_ids = {1: 0, 0: 1, 3: 2, 2: 3}  # マーカーIDと位置の対応

    parameters = aruco.DetectorParameters()
    parameters.adaptiveThreshWinSizeMin = 3
    parameters.adaptiveThreshWinSizeMax = 23
    parameters.adaptiveThreshWinSizeStep = 10
    parameters.adaptiveThreshConstant = 7
    parameters.minMarkerPerimeterRate = 0.03
    parameters.maxMarkerPerimeterRate = 0.3
    parameters.polygonalApproxAccuracyRate = 0.03
    parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX

    marker_positions = {}
    history_length = 10
    marker_presence = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        preprocessed = preprocess_image(frame)
        corners, ids, rejected = aruco.detectMarkers(preprocessed, dictionary, parameters=parameters)

        if ids is not None:
            mat_corners = np.zeros((4, 2), dtype=np.float32)
            for i, id in enumerate(ids):
                if id[0] in corner_marker_ids:
                    mat_corners[corner_marker_ids[id[0]]] = corners[i][0].mean(axis=0)
                marker_presence[id[0]] = time.time()

            if np.all(mat_corners):
                perspective_matrix = cv2.getPerspectiveTransform(mat_corners, mat_corners_real)

                for i in range(len(ids)):
                    if ids[i][0] not in corner_marker_ids:
                        rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners[i], marker_size, camera_matrix, dist_coeffs)
                        
                        marker_center = corners[i][0].mean(axis=0)
                        marker_toio = cv2.perspectiveTransform(np.array([[marker_center]]), perspective_matrix)[0][0]
                        
                        angle = calculate_angle(corners[i][0])
                        
                        if ids[i][0] not in marker_positions:
                            marker_positions[ids[i][0]] = deque(maxlen=history_length)
                        marker_positions[ids[i][0]].append((marker_toio, angle))
                        
                        avg_position, avg_angle = np.mean(marker_positions[ids[i][0]], axis=0)
                        
                        cv2.putText(frame, f"ID: {ids[i][0]}, X: {avg_position[0]:.0f}, Y: {avg_position[1]:.0f}, Angle: {avg_angle:.0f}", 
                                    (10, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        print(f"Marker ID {ids[i][0]}: X = {avg_position[0]:.0f}, Y = {avg_position[1]:.0f}, Angle = {avg_angle:.0f}")

                aruco.drawDetectedMarkers(frame, corners, ids)

                for corner in mat_corners:
                    cv2.circle(frame, tuple(corner.astype(int)), 5, (0, 255, 0), -1)

        current_time = time.time()
        for marker_id, last_seen in list(marker_presence.items()):
            if current_time - last_seen > 2.0:
                cv2.putText(frame, f"Lost Marker ID: {marker_id}", (10, 160 + 30 * marker_id), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.putText(frame, f"FPS: {int(1/(time.time()-current_time))}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        num_markers = 0 if ids is None else len(ids)
        cv2.putText(frame, f"Detected Markers: {num_markers}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(frame, f"Rejected Candidates: {len(rejected)}", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow('Detected Markers and Mat', frame)
        cv2.imshow('Preprocessed Image', preprocessed)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()