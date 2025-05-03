from flask import Flask, jsonify, request
from flask_cors import CORS
from main import get_all_resources

# import os

# port = int(os.environ.get("PORT", 5000))


app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        topicName = request.form.get('topicName')
        if not topicName:
            return jsonify({"error": "Missing topicName in request"}), 400
        
        resources = get_all_resources(f"The best resources for learning or revising or preparing for the topic {topicName}")
        # print(resources)
        return jsonify({
            "topic": topicName,
            "resources": resources
        })
    
    return jsonify({"message": "Use POST Method"})

if __name__ == '__main__':
    app.run(host="0.0.0.0")