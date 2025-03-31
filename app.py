from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import Doctor, Patient
from dbb import db_session
from tensorflow.keras.models import load_model
import numpy as np
import PIL
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
tf.config.set_visible_devices([], 'GPU')


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management and flash messages

# Load the model
model = load_model("retina_weights.hdf5")

# Labels for prediction
labels = {
    0: 'Mild Diabetic Retinopathy',
    1: 'Moderate Diabetic Retinopathy',
    2: 'No Diabetic Retinopathy',
    3: 'Proliferate Diabetic Retinopathy',
    4: 'Severe Diabetic Retinopathy'
}

# Ensure uploads directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home route
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = Doctor.query.filter_by(id=session['user']).first()
    return render_template('profile.html', user=user)

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('_id')
        password = request.form.get('psw')
        name = request.form.get('name')  # Capture the name field

        # Validate that all fields are filled
        if not email or not password or not name:
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))

        # Check if the user already exists
        existing_user = db_session.query(Doctor).filter_by(id=email).first()
        if existing_user:
            flash('User already exists!', 'error')
            return redirect(url_for('register'))

        # Create a new user
        new_user = Doctor(id=email, password=password, name=name)  # Ensure the name is included
        db_session.add(new_user)
        db_session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('_id')  # _id field from the login form
        password = request.form.get('psw')  # Password field from the login form

        # Check if the user exists in the database
        user = db_session.query(Doctor).filter_by(id=email).first()

        if user and user.password == password:  # Verify if the password matches
            # Store user ID and name in the session
            session['user_id'] = user.id  # Store doctor ID in the session
            session['user_name'] = user.name  # Optionally store doctor name in the session
            
            flash('Login successful!', 'success')  # Show success message
            return redirect(url_for('home'))  # Redirect to home page (or dashboard)
        else:
            flash('Invalid email or password!', 'error')  # Show error message if login fails
            return redirect(url_for('login'))  # Stay on the login page if the login fails

    return render_template('login.html')  # Render the login page if GET request

# Dashboard route
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access the dashboard.', 'error')
        return redirect(url_for('login'))

    user_name = session.get('user_name', 'User')
    doctor_id = session.get('user_id')  # Get the logged-in doctor's ID from session

    # Handle search
    search_query = request.args.get('search', '')

    # Fetch patients based on search query
    if search_query:
        patients = db_session.query(Patient).filter(Patient.name.ilike(f'%{search_query}%')).all()
    else:
        patients = db_session.query(Patient).all()

    return render_template('dashboard.html', user_name=user_name, patients=patients, search_query=search_query)

# Detect severity route
@app.route('/detect_severity', methods=['POST'])
def detect_severity():
    if 'user_id' not in session:
        flash('Please login to access the dashboard.', 'error')
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash('No file uploaded!', 'error')
        return redirect(url_for('dashboard'))

    file = request.files['file']
    patient_name = request.form.get('patient_name')
    action = request.form.get('action')  # Get the action (detect or add_patient)

    if file.filename == '':
        flash('No file selected!', 'error')
        return redirect(url_for('dashboard'))

    if not patient_name:
        flash('Patient name is required!', 'error')
        return redirect(url_for('dashboard'))

    # Save the file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Preprocess the image
    img = PIL.Image.open(file_path).convert("RGB").resize((256, 256))
    img = np.asarray(img, dtype=np.float32) / 255.0
    img = img.reshape(1, 256, 256, 3)

    # Make prediction
    predict = model.predict(img)
    predict = np.argmax(predict)
    severity = labels[predict]

    # Fetch patients for the logged-in doctor
    doctor_id = session.get('user_id')
    patients = db_session.query(Patient).filter_by(doctor_id=doctor_id).all()

    if action == 'detect':
        # Only show the prediction result
        return render_template(
            'dashboard.html',
            user_name=session.get('user_name'),
            patients=patients,  # Pass patients data
            search_query='',
            prediction=severity
        )
    elif action == 'add_patient':
        # Add patient to the database
        new_patient = Patient(name=patient_name, severity=severity, doctor_id=doctor_id)
        db_session.add(new_patient)
        db_session.commit()
        flash(f'Patient added successfully! Severity: {severity}', 'success')
        return redirect(url_for('dashboard'))

# Logout route
@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
