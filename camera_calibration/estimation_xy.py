#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import cv2
from cv2 import aruco
import os

def main():
    cap = cv2.VideoCapture(1)  # カメラのインデックスを適切に設定してください
    
    # マーカーの辞書選択（4x4マーカー用）
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

    # キャリブレーションデータの読み込み
    current_dir = os.path.dirname(os.path.abspath(__file__))
    camera_matrix = np.load(os.path.join(current_dir, "mtx.npy"))
    dist_coeffs = np.load(os.path.join(current_dir, "dist.npy"))

    # マーカーサイズ（メートル単位）
    marker_size = 0.05  # 例: 5cm = 0.05m

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # グレースケールに変換
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # マーカーの検出
        corners, ids, rejected = aruco.detectMarkers(gray, dictionary)

        if ids is not None:
            # マーカーごとに処理
            for i in range(len(ids)):
                # マーカーの姿勢推定
                rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners[i], marker_size, camera_matrix, dist_coeffs)

                # 回転ベクトルと並進ベクトルを取得
                rvec = rvec[0][0]
                tvec = tvec[0][0]

                # マーカーの中心座標（カメラ座標系）
                marker_center = tvec

                # 画像上にマーカーの軸を描画
                cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvec, tvec, 0.03)

                # マーカーのIDと3D座標を表示
                text = f"ID: {ids[i][0]}, X: {marker_center[0]:.2f}, Y: {marker_center[1]:.2f}, Z: {marker_center[2]:.2f}"
                cv2.putText(frame, text, (10, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                print(f"Marker ID {ids[i][0]}: X = {marker_center[0]:.2f}, Y = {marker_center[1]:.2f}, Z = {marker_center[2]:.2f}")

            # 検出されたマーカーを描画
            aruco.drawDetectedMarkers(frame, corners, ids)

        cv2.imshow('Detected Markers', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()