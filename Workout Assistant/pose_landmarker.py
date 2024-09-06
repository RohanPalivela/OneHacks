import os
import io
import json
import base64
import google.generativeai as genai
from utils import gemini_vision, extract_curly_braces
from PIL import Image

import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import cv2 as cv
import math
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

genai.configure(api_key="AIzaSyB28qrLxCiUBnC5OeQ4Tnl8QDB6GwR4yeo")

multimodal_model = genai.GenerativeModel("models/gemini-1.5-flash")
res = ""

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})  # Replace with your React app's URL

@app.route('/predict', methods=['POST'])
def predict():
    # Get data from the React app
    breakfast_str = request.form.get('breakfast')
    if breakfast_str:
        # Decode the base64 string
        breakfast = base64.b64decode(breakfast_str.split(',')[1])
        breakfast = Image.open(io.BytesIO(breakfast))

    lunch_str = request.form.get('lunch')
    if lunch_str:
        # Decode the base64 string
        lunch = base64.b64decode(lunch_str.split(',')[1])
        lunch = Image.open(io.BytesIO(lunch))
    
    dinner_str = request.form.get('dinner')
    if dinner_str:
        # Decode the base64 string
        dinner = base64.b64decode(dinner_str.split(',')[1])
        dinner = Image.open(io.BytesIO(dinner))
    
    age = request.form.get('age')
    sex = request.form.get('sex')
    goals = request.form.get('goals')
    weight = request.form.get('weight')
    height = request.form.get('height')
    length = request.form.get('length')

    context = f"""
    User Information:
    Age: {age}
    Sex: {sex}
    Weight (in pounds): {weight}
    Height (in inches): {height}
    Goal: {goals}
    """

    instructions = "Never make up facts, and if you are not 100% sure, \
    be transparent in stating when you are not sure"

    assignment_1 = """ROLE: You are an expert food identifier

    Based on the 3 images provided of breakfast, lunch and dinner, identify a list of foods found in the image.
    Include:
    1 - the number of pieces of food (e.g. 2 slices of bacon)
    2 - how the piece of food was cooked (e.g. fried, baked, grilled, steamed)

    **Example Output Format for identifying foods**
    Breakfast: 2 fried eggs, 1 pancake, 1 tablespoon of maple syrup on the pancake, and a cup of milk.
    Lunch: 2 thinly sliced pieces of grilled chicken, 1 tablespoon of terikayi glaze, orange slices, and steamed multigrain rice
    ...and so on

    Output format:
    Breakfast: <The foods found in the image>
    Lunch: <The foods found in the image>
    Dinner: <The foods found in the image>
    """

    constraints = """
    If the image uploaded is NOT food, then respond with "Food not found"
    """

    contents_1 = [
        instructions,
        "Breakfast:",
        breakfast,
        "Lunch:",
        lunch,
        "Dinner:",
        dinner,
        assignment_1,
        constraints
    ]

    response_1 = gemini_vision(contents_1, multimodal_model)

    role_diet = """
    ROLE: You are a nutrition expert and professional dietitian helping individuals improve their eating habits to achieve better fitness.
    """

    diets = """
    List of Diet Plans:
    - Mediterranean Diet
    Description: Emphasizes fruits, vegetables, whole grains, and healthy fats.
    Outcome: Heart health, weight loss, longevity.
    - DASH Diet (Dietary Approaches to Stop Hypertension)
    Description: Focuses on reducing sodium and increasing nutrient-rich foods.
    Outcome: Lower blood pressure, improve heart health.
    - Keto (Ketogenic) Diet
    Description: High-fat, low-carb, moderate-protein diet.
    Outcome: Rapid weight loss, improved insulin sensitivity.
    - Paleo Diet
    Description: Focuses on eating foods similar to early humans: meat, fish, fruits, vegetables, nuts.
    Outcome: Weight loss, reduced inflammation.
    - Vegan Diet
    Description: Excludes all animal products, focusing on plant-based foods.
    Outcome: Weight loss, improved heart health, ethical/environmental benefits.
    - Whole30
    Description: 30-day program eliminating sugar, grains, dairy, and legumes.
    Outcome: Reset metabolism, identify food sensitivities.
    - Intermittent Fasting
    Description: Cycling between eating and fasting periods.
    Outcome: Weight loss, improved metabolism, longevity.
    - Low-Carb Diet
    Description: Reduces carbohydrate intake, focuses on proteins and fats.
    Outcome: Weight loss, improved blood sugar control.
    - Flexitarian Diet
    Description: Primarily plant-based with occasional meat consumption.
    Outcome: Weight loss, improved overall health, flexibility.
    - MIND Diet (Mediterranean-DASH Intervention for Neurodegenerative Delay)
    Description: Combines Mediterranean and DASH diets, focusing on brain-healthy foods.
    Outcome: Improve brain function, reduce Alzheimer’s risk.
    """

    assignment_2 = """
    ASSIGNMENT:
    Your task is to perform the following actions:
    1 - Create a list of suggestions to improve the overall healthiness of the meal. If a meal is balanced (e.g., includes a variety of vegetables, lean protein, whole grains, and healthy fats), and the caloric content aligns with healthy eating goals, output "Good meal, no suggestions" for that meal.
    2 - Calculate the number of calories and nutritional values (total fat, cholesterol, sodium, carbohydrate, protein) from the user's meal, breaking down each component individually.
    3 - Rate the User's diet on a scale from 1 - 10
    4 - Output a json object that contains the following keys: breakfast, lunch, dinner, and rating.

    When creating a list of suggestions, first critique the meal yourself, think about constructive feedback on what could be improved, and THEN suggest healthier alternatives or adjustments to align with the User's Goal.
    Consider the following in your analysis:
    - Nutrient density (vitamins, minerals, fiber, etc.)
    - Balance between macronutrients (carbohydrates, proteins, fats)
    - Preparation methods (grilled vs. fried, etc.)
    - Incorporation of whole foods vs. processed foods
    - Portion control
    - Personalize suggestions based on the User's Age, Sex, Weight, Height, and Goal.

    When suggesting alternatives, ensure that they are practical, easy to implement, and tasty.
    Offer tips on cooking methods, ingredient substitutions, and any other advice that would help the user transition to healthier eating habits.
    Use the list of different types of diet plans to influence the output, but don't mention the diet plans explicitly. Keep in mind the risks of each diet plan with the user's age & sex when forming the output.

    **IMPORTANT: Ensure the suggestions directly reflect the meal descriptions given. Do not mention ingredients or foods not listed in the meal descriptions.

    If a meal is balanced (e.g., includes a variety of vegetables, lean protein, whole grains, and healthy fats), and the caloric content aligns with healthy eating goals, output "Good meal, no suggestions" for that meal.

    For calorie calculation (THIS IS AN ESTIMATE, DOES NOT BE BE TRULY ACCURATE):
    - Estimate the caloric content for each meal component separately, and sum them for a total caloric value.
    - Use established nutritional databases or algorithms to ensure accuracy. Be transparent about any limitations or uncertainties in calorie estimates.
    - Clearly state the total number of calories for each meal and provide a daily total.
    IMPORTANT - IF YOU CANNOT COME UP WITH A NUMBER OF CALORIES ("I am not sure how to estimate the protein content for this meal"), JUST PUT AN INTEGER, IT DOESN'T MATTER IF YOU KNOW THE COOKING METHODS, JUST GUESS!!

    **IMPORTANT: Ensure the output is in json format

    Use the following STRICT format for the output:
    breakfast:
    - Suggestion: <List of Suggestions to Improve formatted as a list>
    - Calories: <The number of calories formatted as an integer>
    - Nutrition: <total fat, cholesterol, sodium, carbohydrate, protein formatted as integers>
    lunch:
    - Suggestion: <List of Suggestions to Improve formatted as a list>
    - Calories: <The number of calories formatted as an integer>
    - Nutrition: <total fat, cholesterol, sodium, carbohydrate, protein formatted as integers>
    dinner:
    - Suggestion: <List of Suggestions to Improve formatted as a list>
    - Calories: <The number of calories formatted as an integer>
    - Nutrition: <total fat, cholesterol, sodium, carbohydrate, protein formatted as integers>
    rating: <rating of User's diet, formatted as an integer>
    Output JSON: <json with breakfast, lunch, dinner, and rating>



    **EXAMPLE Output Format**
    {
    "breakfast": {
    "Suggestions": [
        "Add a leafy green vegetable to your salad, such as lettuce, spinach, or arugula, to increase the fiber content and overall nutritional value.",
        "Swap 1/2 of the portion of hummus with plain Greek yogurt to reduce fat and calorie content.",
        "Use air-popped popcorn or whole-wheat crackers as an alternative to almonds to reduce calorie and fat intake.",
        "Substitute red onion with a vegetable source that provides more nutrients, like bell peppers or carrots.",
        "Grill the chicken instead of frying to make it leaner and reduce fat intake.",
        "To add a whole grain component, accompany your meal with a slice of whole-wheat or rye bread."
    ],
    "Calories": 826,
    "Nutrition": {
    "total fat": 56,
    "cholesterol": 586,
    "sodium": 1846,
    "carbohydrate": 67,
    "protein": 56
    }
    ... and so on
    }
    """

    contents_2 = [
        instructions,
        role_diet,
        context,
        diets,
        "MEALS:",
        response_1,
        assignment_2,
        constraints
    ]

    response_2 = gemini_vision(contents_2, multimodal_model)
    
    res = response_2

    try:
        response_json = json.loads(extract_curly_braces(response_2))
    except json.JSONDecodeError as e:
        print(f"JSON decoding failed: {e}")
        return jsonify({'error': 'Failed to parse response as JSON'}), 500
    
    return jsonify(response_json)


@app.route('/workout', methods=['POST'])
def workout():
    age = request.form.get('age')
    sex = request.form.get('sex')
    goals = request.form.get('goals')
    weight = request.form.get('weight')
    height = request.form.get('height')
    length = request.form.get('length')

    role_workout = """
    ROLE: You are a workout expert and professional fitness trainer helping individuals improve achieve better fitness based on what they've eaten and their goals.
    """

    assignment_3 = """
    Recommend a workout plan based on the "Meals caloric information" that the user ate today (IGNORE the suggestions)
    Personalize suggestions based on the User's Age, Sex, Weight, Height, and Goal.

    Recommend 5 specific workouts.

    Use the following format for the output (MUST BE A JSON!!!:
    warm_up:
    - Duration: <length of time in minutes as a double>
    - Exercises: <a list of exercises with a name, duration>
    main_workout:
    - Duration: <length of time in minutes as a double>
    - Exercises: <a list of exercises with a name (String), sets (integer), reps_per_set (integer), duration (double), calories burned (integer)>
    cool_down:
    - Duration: <length of time in minutes as a double>
    - Exercises: <a list of exercises with a name, duration>
    Output JSON: <json with warm_up, main_workout, and cool_down>



    **EXAMPLE Output Format (DO NOT COPY)**
    {
        "warm_up": {
        "duration": 5.0,
        "exercises": [
            {
            "name": "Jumping Jacks",
            "duration": 2.0
            },
            ... and so on
        ]
        },
        "main_workout": {
        "duration": 20.0,
        "exercises": [
            {
            "name": "Burpees",
            "sets": 3,
            "reps_per_set": 10,
            "duration": 4.0,
            "calories_burned": 50
            },
            ... and so on
        ]
        },
        "cool_down": {
        "duration": 5.0,
        "exercises": [
            {
            "name": "Static Stretching",
            "duration": 5.0
            },
            ... and so on
        ]
        }
    }
    """
    instructions = "Never make up facts, and if you are not 100% sure, \
    be transparent in stating when you are not sure"

    context = f"""
    User Information:
    Age: {age}
    Sex: {sex}
    Weight (in pounds): {weight}
    Height (in inches): {height}
    Goal: {goals}
    """
    
    constraints_workout = "ONLY suggest workouts, nothing else!"

    contents_workout = [
        instructions,
        role_workout,
        context,
        "Amount of free time today (in minutes): " + str(length),
        "Meals caloric information (IGNORE the suggestions):",
        res,
        assignment_3,
        constraints_workout
    ]

    response_2 = gemini_vision(contents_workout, multimodal_model)
    print(res)
    print(response_2)

    try:
        response_json = json.loads(extract_curly_braces(response_2))
    except json.JSONDecodeError as e:
        print(f"JSON decoding failed: {e}")
        return jsonify({'error': 'Failed to parse response as JSON'}), 500
    
    return jsonify(response_json)

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


landmarker = PoseLandmarker()

@app.route('/getSquat')
def get_squat():
    return landmarker.check_squat()

@app.route('/getPullup')
def get_pullup():
    return landmarker.check_pullup()

@app.route('/getCurl')
def get_curl():
    return landmarker.check_curl()

def load_frames():

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