import cv2
import numpy as np
from cv2 import aruco

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

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global perspective_matrix
        if perspective_matrix is not None:
            # 入力座標を浮動小数点型に変換
            input_point = np.array([[[float(x), float(y)]]], dtype=np.float32)
            toio_coord = cv2.perspectiveTransform(input_point, perspective_matrix)[0][0]
            print(f"クリックした座標 (toio座標系): (x: {toio_coord[0]:.0f}, y: {toio_coord[1]:.0f})")
        else:
            print("マットが検出されていません。toio座標系に変換できません。")

def main():
    global perspective_matrix
    perspective_matrix = None
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cap.set(cv2.CAP_PROP_EXPOSURE, -1)

    cv2.namedWindow("Camera")
    cv2.setMouseCallback("Camera", mouse_callback)

    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters()
    parameters.adaptiveThreshWinSizeMin = 3
    parameters.adaptiveThreshWinSizeMax = 23
    parameters.adaptiveThreshWinSizeStep = 10
    parameters.adaptiveThreshConstant = 7
    parameters.minMarkerPerimeterRate = 0.03
    parameters.maxMarkerPerimeterRate = 0.3
    parameters.polygonalApproxAccuracyRate = 0.03
    parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX

    mat_tl, mat_tr, mat_br, mat_bl = (98, 142), (402, 142), (402, 358), (98, 358)
    mat_corners_real = np.float32([mat_tl, mat_tr, mat_br, mat_bl])

    corner_marker_ids = set([0, 1, 2, 3])

    while True:
        ret, frame = cap.read()
        if not ret:
            print("フレームの取得に失敗しました")
            break

        preprocessed = preprocess_image(frame)
        corners, ids, rejected = aruco.detectMarkers(preprocessed, dictionary, parameters=parameters)

        if ids is not None:
            mat_corners = []
            for i, id in enumerate(ids):
                if id[0] in corner_marker_ids:
                    mat_corners.append(get_mat_corner(corners[i], id[0]))

            if len(mat_corners) == 4:
                mat_corners = np.float32(mat_corners)
                mat_corners = order_points(mat_corners)
                perspective_matrix = cv2.getPerspectiveTransform(mat_corners, mat_corners_real)

                for corner in mat_corners:
                    cv2.circle(frame, tuple(corner.astype(int)), 5, (0, 255, 0), -1)

            aruco.drawDetectedMarkers(frame, corners, ids)

        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()