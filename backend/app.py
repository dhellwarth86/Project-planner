from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from db_config import db, init_db
from backend.models import Project, ProjectImage

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize database configuration and tables
init_db(app)
with app.app_context():
    db.create_all()

# Endpoint to create a new project
@app.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    new_project = Project(name=data['name'], description=data['description'])
    db.session.add(new_project)
    db.session.commit()
    return jsonify({"message": "Project created successfully!", "project_id": new_project.id}), 201

# Endpoint to upload an image to a specific project
@app.route('/upload/<int:project_id>', methods=['POST'])
def upload_image(project_id):
    # Ensure the project exists
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    # Check for file in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save file to the upload folder
    file.save(file_path)

    # Save file reference in database
    new_image = ProjectImage(project_id=project_id, filename=filename)
    db.session.add(new_image)
    db.session.commit()
    
    return jsonify({"message": "Image uploaded successfully!", "filename": filename}), 200

# Endpoint to retrieve an uploaded image
@app.route('/uploads/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Endpoint to retrieve all projects with their images
@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    projects_data = [
        {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "images": [{"id": image.id, "filename": image.filename} for image in project.images]
        }
        for project in projects
    ]
    return jsonify(projects_data), 200

# Endpoint to get a single project's details by ID
@app.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    project_data = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "images": [{"id": image.id, "filename": image.filename} for image in project.images]
    }
    return jsonify(project_data), 200

if __name__ == '__main__':
    app.run(debug=True)

