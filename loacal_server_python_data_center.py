from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os

app = Flask(__name__)

# Default directory to store files
UPLOAD_FOLDER = './custom_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# HTML template for the file system, upload, download, and search bar
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        a { text-decoration: none; color: #007BFF; }
        a:hover { text-decoration: underline; }
        ul { list-style-type: none; }
        li { margin: 5px 0; }
        .folder { font-weight: bold; }
    </style>
</head>
<body>
    <h1>File Server</h1>
    
    <!-- Search Bar -->
    <form method="GET" action="/search">
        <input type="text" name="query" placeholder="Search files and folders" required>
        <button type="submit">Search</button>
    </form>
    <br>

    <!-- Upload Form -->
    <h2>Upload File</h2>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="hidden" name="current_folder" value="{{ current_folder }}">
        <input type="file" name="file" required>
        <button type="submit">Upload</button>
    </form>
    <br>

    <!-- File System View -->
    <h2>File System</h2>
    <ul>
        {% if parent_folder %}
            <li><a href="/browse?path={{ parent_folder }}">⬆️ Go Back</a></li>
        {% endif %}
        {% for item in files_and_folders %}
            {% if item.is_folder %}
                <li class="folder">📁 <a href="/browse?path={{ item.path }}">{{ item.name }}</a></li>
            {% else %}
                <li>📄 <a href="/files/{{ item.path }}">{{ item.name }}</a> | <a href="/delete?path={{ item.path }}" style="color: red;">🗑 Delete</a></li>
            {% endif %}
        {% endfor %}
    </ul>
</body>
</html>
"""

def get_file_system(path):
    """
    Retrieve the list of files and folders in the specified path.
    """
    items = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        items.append({
            "name": item,
            "path": os.path.relpath(item_path, UPLOAD_FOLDER),
            "is_folder": os.path.isdir(item_path),
        })
    return items

@app.route('/')
@app.route('/browse')
def browse():
    """
    Show the file system starting from the upload folder.
    """
    browse_path = request.args.get('path', '')
    full_path = os.path.join(UPLOAD_FOLDER, browse_path)

    # Validate the path
    if not os.path.exists(full_path):
        return jsonify({"error": "Path not found"}), 404

    # Get parent folder for navigation
    parent_folder = os.path.relpath(os.path.dirname(full_path), UPLOAD_FOLDER) if browse_path else None

    # Get file and folder structure
    files_and_folders = get_file_system(full_path)
    return render_template_string(HTML_TEMPLATE, files_and_folders=files_and_folders, current_folder=browse_path, parent_folder=parent_folder)

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload a file to the current folder.
    """
    current_folder = request.form.get('current_folder', '')
    upload_path = os.path.join(UPLOAD_FOLDER, current_folder)

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(upload_path, file.filename)
    os.makedirs(upload_path, exist_ok=True)
    file.save(file_path)
    return jsonify({"message": f"File {file.filename} uploaded successfully to {current_folder}"}), 200

@app.route('/files/<path:filename>', methods=['GET'])
def get_file(filename):
    """
    Download a file from the server.
    """
    try:
        directory = os.path.join(UPLOAD_FOLDER, os.path.dirname(filename))
        return send_from_directory(directory, os.path.basename(filename), as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route('/search', methods=['GET'])
def search():
    """
    Search for files and folders across the file system.
    """
    query = request.args.get('query', '').lower()
    matches = []

    for root, dirs, files in os.walk(UPLOAD_FOLDER):
        for name in dirs + files:
            if query in name.lower():
                relative_path = os.path.relpath(os.path.join(root, name), UPLOAD_FOLDER)
                matches.append(relative_path)

    return jsonify({"matches": matches}), 200

@app.route('/delete', methods=['GET'])
def delete_file():
    """
    Delete a file or folder.
    """
    path = request.args.get('path', '')
    full_path = os.path.join(UPLOAD_FOLDER, path)

    if os.path.isdir(full_path):
        return jsonify({"error": "Cannot delete folders"}), 400

    try:
        os.remove(full_path)
        return jsonify({"message": f"Deleted {path}"}), 200
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
