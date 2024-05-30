from flask import Flask, render_template, request, redirect, url_for, session,jsonify
import os
from werkzeug.utils import secure_filename
from predict import detect_image
import sqlite3

app = Flask(__name__, static_folder='outputs')


app.secret_key = 'AQWERTYUIOP'
DATABASE = 'database.db'

# Set up SQLite connection and create necessary tables
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                uploaded_image TEXT,
                detected_image TEXT,
                image_name TEXT,
                masks_present INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()

# Function to verify user credentials
def verify_user_credentials(username, password):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        return user
    

# Function to fetch historical images for the current user
def get_historical_images(username):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT image_name, detected_image, masks_present
            FROM images
            WHERE user_id = (
                SELECT id
                FROM users
                WHERE username = ?
            )
            ORDER BY id DESC
            LIMIT 5
        """, (username,))
        return cursor.fetchall()

# Function to create a new user
def create_new_user(username, password):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Username already exists
            return False

# Function to insert image data for a user
def insert_image(user_id, uploaded_image, detected_image, image_name, masks_present):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO images (user_id, uploaded_image, detected_image, image_name, masks_present)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, uploaded_image, detected_image, image_name, masks_present))
        conn.commit()

# Initialize the database when the application starts
init_db()



# Set the path to upload files
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('./index0.html')


@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        return render_template('profile.html', username=username)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = verify_user_credentials(username, password)
        if user:
            session['username'] = username
            return redirect(url_for('profile'))
        else:
            return render_template('login.html', message='Invalid username or password')
    return render_template('login.html', message='')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if create_new_user(username, password):
            return redirect(url_for('login'))
        else:
            return render_template('create_account.html', message='Username already exists')
    return render_template('create_account.html', message='')



@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Call detect_image function with the image path
        result_path, total_masks = detect_image(filepath)
        print("filepath: ", result_path)
        
        # Get the username from the session
        username = session.get('username', 'Anonymous')
        
        # Retrieve the user ID from the database
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username=?", (username,))
            user_row = cursor.fetchone()
            if user_row:
                user_id = user_row[0]
            else:
                return jsonify({'error': 'User not found'})

        # Insert the image data for the user into the database
        insert_image(user_id, filepath, result_path, filename, total_masks)
        
        return jsonify({'file_url': result_path, 'file_name': filename, 'total_masks': total_masks})
    else:
        return jsonify({'error': 'Invalid file type'})

@app.route('/historical_images')
def historical_images():
    # Check if the user is logged in
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'})

    # Get the username from the session
    username = session['username']

    # Fetch historical images for the current user
    historical_data = get_historical_images(username)

    return jsonify(historical_data)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
