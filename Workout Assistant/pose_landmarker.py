import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import cv2 as cv
import math
from flask import Flask, Response, jsonify

app = Flask(__name__)

class PoseLandmarker:

    def __init__(self):
        base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=True)
        self.detector = vision.PoseLandmarker.create_from_options(options)
        self.lm_list = []

    def get_landmark_image_data(self, rgb_image, detection_result):
        pose_landmarks_list = detection_result.pose_landmarks
        annotated_image = np.copy(rgb_image)

        self.lm_list = []

        for idx in range(len(pose_landmarks_list)):
            pose_landmarks = pose_landmarks_list[idx]
            for i, landmark in enumerate(pose_landmarks):
                x = int(landmark.x * annotated_image.shape[1])
                y = int(landmark.y * annotated_image.shape[0])
                cv.putText(annotated_image, str(i), (x, y), cv.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)
                if idx == 0:
                    self.lm_list.append([i, x, y])


            pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            pose_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
            ])
            solutions.drawing_utils.draw_landmarks(
            annotated_image,
            pose_landmarks_proto,
            solutions.pose.POSE_CONNECTIONS,
            solutions.drawing_styles.get_default_pose_landmarks_style())
        return annotated_image
    
    def draw_annotations(self, frame):
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

        detection_result = self.detector.detect(image)
        annotations = self.get_landmark_image_data(image.numpy_view(), detection_result)
        return annotations
    
    # RETURNS CURL EFFICIENCY %
    @app.route('/getCurl')
    def check_curl(self):

        min_angle = 30
        max_angle = 180

        left_arm_percent = -1
        right_arm_percent = -1

        if (len(self.lm_list) >= 16):
            left_arm = [self.lm_list[11],
                        self.lm_list[13],
                        self.lm_list[15]]
            left_arm_percent = self.clamp_value(self.scale_value(self.get_angle_points_deg(left_arm[0], left_arm[1], left_arm[2]),
                                                max_angle,
                                                min_angle,
                                                0,
                                                100), 0, 100)

        if (len(self.lm_list) >= 17):
            right_arm = [self.lm_list[12],
                        self.lm_list[14],
                        self.lm_list[16]]
            right_arm_percent = self.clamp_value(self.scale_value(self.get_angle_points_deg(right_arm[0], right_arm[1], right_arm[2]),
                                                max_angle,
                                                min_angle,
                                                0,
                                                100), 0, 100)
        sum = 0

        if left_arm_percent >= 0:
            sum += left_arm_percent
        if right_arm_percent >= 0:
            sum += right_arm_percent
            response = jsonify({'efficiency': sum / 2})
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        
        response = jsonify({'efficiency': sum})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    # RETURNS SQUAT EFFICIENCY %
    @app.route('/getSquat')
    def check_squat(self):

        min_angle = 70
        max_angle = 180

        left_leg_percent = -1
        right_leg_percent = -1

        if (len(self.lm_list) >= 16):
            left_leg = [self.lm_list[23],
                        self.lm_list[25],
                        self.lm_list[27]]
            left_leg_percent = self.clamp_value(self.scale_value(self.get_angle_points_deg(left_leg[0], left_leg[1], left_leg[2]),
                                                max_angle,
                                                min_angle,
                                                0,
                                                100), 0, 100)

        if (len(self.lm_list) >= 17):
            right_leg = [self.lm_list[24],
                        self.lm_list[26],
                        self.lm_list[28]]
            right_leg_percent = self.clamp_value(self.scale_value(self.get_angle_points_deg(right_leg[0], right_leg[1], right_leg[2]),
                                                max_angle,
                                                min_angle,
                                                0,
                                                100), 0, 100)
        sum = 0

        if left_leg_percent >= 0:
            sum += left_leg_percent
        if right_leg_percent >= 0:
            sum += right_leg_percent
            response = jsonify({'efficiency': sum / 2})
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        
        response = jsonify({'efficiency': sum})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    # RETURNS PULLUP EFFICIENCY %
    @app.route('/getPullup')
    def check_pullup(self):

        min_angle = 15
        max_angle = 180

        left_arm_percent = -1
        right_arm_percent = -1

        if (len(self.lm_list) >= 16):
            left_arm = [self.lm_list[11],
                        self.lm_list[13],
                        self.lm_list[15]]
            left_arm_percent = self.clamp_value(self.scale_value(self.get_angle_points_deg(left_arm[0], left_arm[1], left_arm[2]),
                                                max_angle,
                                                min_angle,
                                                0,
                                                100), 0, 100)

        if (len(self.lm_list) >= 17):
            right_arm = [self.lm_list[12],
                        self.lm_list[14],
                        self.lm_list[16]]
            right_arm_percent = self.clamp_value(self.scale_value(self.get_angle_points_deg(right_arm[0], right_arm[1], right_arm[2]),
                                                max_angle,
                                                min_angle,
                                                0,
                                                100), 0, 100)
        sum = 0

        if left_arm_percent >= 0:
            sum += left_arm_percent
        if right_arm_percent >= 0:
            sum += right_arm_percent
            response = jsonify({'efficiency': sum / 2})
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        
        response = jsonify({'efficiency': sum})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    def clamp_value(self, value, min, max):
        if (value > max):
            value = max
        elif (value < min):
            value = min
        return value
    
    def scale_value(self, value, old_min, old_max, new_min, new_max):
        return ((value - old_min) * (new_max - new_min) / (old_max - old_min)) + new_min
    
    def get_angle_points_deg(self, p1, p2, p3):
        a = self.get_distance(p1, p2)
        b = self.get_distance(p2, p3)
        c = self.get_distance(p1, p3)

        return math.degrees(math.acos((a**2 + b**2 - c**2) / (2 * a * b)))
    
    def get_distance(self, p1, p2):
        return math.sqrt((p2[1] - p1[1])**2 + (p2[2] - p1[2])**2)


def load_frames():

    landmarker = PoseLandmarker()

    capture = cv.VideoCapture(0)
    while True:
        ret, frame = capture.read()

        if not ret: 
            return None

        frame = landmarker.draw_annotations(frame)

        ret, buffer = cv.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/getFeed')
def get_video():
    response = Response(load_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
if __name__ == "__main__":
    app.run(debug=True)