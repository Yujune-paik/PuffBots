import cv2
import numpy as np
from cv2 import aruco
import time
from collections import deque

class ARPositionTracker:
    def __init__(self):
        self.cap = cv2.VideoCapture(1)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)

        self.dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

        self.mat_tl, self.mat_tr, self.mat_br, self.mat_bl = (98, 142), (402, 142), (402, 358), (98, 358)
        self.mat_corners_real = np.float32([self.mat_tl, self.mat_tr, self.mat_br, self.mat_bl])

        self.corner_marker_ids = set([0, 1, 2, 3])

        self.parameters = aruco.DetectorParameters()
        self.parameters.adaptiveThreshWinSizeMin = 3
        self.parameters.adaptiveThreshWinSizeMax = 23
        self.parameters.adaptiveThreshWinSizeStep = 10
        self.parameters.adaptiveThreshConstant = 7
        self.parameters.minMarkerPerimeterRate = 0.03
        self.parameters.maxMarkerPerimeterRate = 0.3
        self.parameters.polygonalApproxAccuracyRate = 0.05
        self.parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX

        self.marker_positions = {}

    def order_points(self, pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    def enhance_image(self, image):
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        enhanced_lab = cv2.merge((cl,a,b))
        enhanced_image = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        return enhanced_image

    def detect_and_update_markers(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame")
            return

        enhanced_frame = self.enhance_image(frame)
        gray = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = aruco.detectMarkers(gray, self.dictionary, parameters=self.parameters)

        if ids is not None:
            mat_corners = []
            for i, id in enumerate(ids):
                if id[0] in self.corner_marker_ids:
                    mat_corners.append(corners[i][0].mean(axis=0))

            if len(mat_corners) == 4:
                mat_corners = np.float32(mat_corners)
                mat_corners = self.order_points(mat_corners)

                perspective_matrix = cv2.getPerspectiveTransform(mat_corners, self.mat_corners_real)

                for i in range(len(ids)):
                    if ids[i][0] not in self.corner_marker_ids:
                        marker_center = corners[i][0].mean(axis=0)
                        marker_toio = cv2.perspectiveTransform(np.array([[marker_center]]), perspective_matrix)[0][0]
                        self.marker_positions[ids[i][0]] = (int(marker_toio[0]), int(marker_toio[1]))

    def ar_position(self, id_number):
        self.detect_and_update_markers()
        return self.marker_positions.get(id_number, None)

    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()

# グローバルなインスタンスを作成
tracker = ARPositionTracker()

def ar_position(id_number):
    return tracker.ar_position(id_number)

if __name__ == '__main__':
    try:
        while True:
            for id in range(4, 10):  # 例として、ID 4から9までをチェック
                position = ar_position(id)
                if position:
                    print(f"Marker ID {id}: X = {position[0]}, Y = {position[1]}")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        tracker.close()