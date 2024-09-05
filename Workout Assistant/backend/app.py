import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from utils import gemini_vision

genai.configure(api_key="AIzaSyB28qrLxCiUBnC5OeQ4Tnl8QDB6GwR4yeo")

multimodal_model = genai.GenerativeModel("models/gemini-1.5-flash")


app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def predict():
    print("start")
    # Get data from the React app
    breakfast = request.files.get('breakfast')
    lunch = request.files.get('lunch')
    dinner = request.files.get('dinner')
    age = request.form.get('age')
    sex = request.form.get('sex')
    goals = request.form.get('goals')
    weight = request.form.get('weight')
    height = request.form.get('height')
    length = request.form.get('length')
    print("age is " + goals)

    # print_multimodal_prompt([breakfast,lunch,dinner])

    
    # response_2 = gemini_vision("hello", multimodal_model)

    # try:
    #     response_json = json.loads(response_2)
    # except json.JSONDecodeError as e:
    #     logging.error(f"JSON decoding failed: {e}")
    #     return jsonify({'error': 'Failed to parse response as JSON'}), 500
    
    # return jsonify(response_json)

    return jsonify({"json": 2})

if __name__ == '__main__':
    app.run(debug=True)