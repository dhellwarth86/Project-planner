from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from backend.db_config import db, init_db
from backend.models import Project, ProjectImage

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

init_db(app)
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Project Planner API!"})

@app.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    new_project = Project(name=data['name'], description=data['description'])
    db.session.add(new_project)
    db.session.commit()
    return jsonify({"message": "Project created successfully!", "project_id": new_project.id}), 201

# Additional endpoints as needed

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
