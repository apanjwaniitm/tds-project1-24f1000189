from flask import Flask, request, jsonify, send_file
import os
import json
import datetime

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_task():
    task = request.args.get('task', '')
    if not task:
        return "Task description is missing.", 400
    
    try:
        # Add logic to parse and execute tasks here
        result = f"Executed task: {task}"
        return result, 200
    except ValueError as e:
        return str(e), 400
    except Exception as e:
        return f"Agent error: {str(e)}", 500

@app.route('/read', methods=['GET'])
def read_file():
    file_path = request.args.get('path', '')
    if not os.path.exists(file_path):
        return "File not found.", 404
    return send_file(file_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
