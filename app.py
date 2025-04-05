from flask import Flask, render_template, request, jsonify, url_for
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Firebase with explicit path to serviceAccountKey.json
try:
    # Get the absolute path to serviceAccountKey.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cred_path = os.path.join(current_dir, 'serviceAccountKey.json')
    
    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"Firebase credentials file not found at: {cred_path}")
    
    cred = credentials.Certificate(cred_path)
    
    # Initialize Firebase app if not already initialized
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    
    # Get Firestore client
    db = firestore.client()
    print("Firebase initialized successfully!")
except Exception as e:
    print(f"Error initializing Firebase: {str(e)}")
    raise

@app.route('/')
def index():
    return render_template('student_form.html')

@app.route('/search_barcode', methods=['POST'])
def search_barcode():
    try:
        data = request.json
        barcode = data.get('barcode')
        
        if not barcode:
            return jsonify({'error': 'Barcode is required'}), 400

        # Search for student with matching roll number (since barcode = roll number)
        students_ref = db.collection('students')
        query = students_ref.where('rollNo', '==', barcode).limit(1).get()
        
        student_found = False
        for doc in query:
            student_found = True
            student_data = doc.to_dict()
            return jsonify(student_data), 200
            
        if not student_found:
            return jsonify({'error': f'No student found with Roll Number: {barcode}'}), 404

    except Exception as e:
        print(f"Error in search_barcode: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/check_duplicate', methods=['POST'])
def check_duplicate():
    try:
        data = request.json
        roll_no = data.get('rollNo')
        reg_no = data.get('regNo')
        
        if not roll_no:
            return jsonify({'error': 'Roll number is required'}), 400

        # Check for duplicate roll number
        students_ref = db.collection('students')
        roll_query = students_ref.where('rollNo', '==', roll_no).limit(1).get()
        
        if any(doc.exists for doc in roll_query):
            return jsonify({
                'isDuplicate': True,
                'message': f'Student with Roll Number {roll_no} already exists!'
            }), 200

        # Check for duplicate registration number if provided
        if reg_no:
            reg_query = students_ref.where('regNo', '==', reg_no).limit(1).get()
            if any(doc.exists for doc in reg_query):
                return jsonify({
                    'isDuplicate': True,
                    'message': f'Student with Registration Number {reg_no} already exists!'
                }), 200

        return jsonify({
            'isDuplicate': False,
            'message': 'No duplicate found'
        }), 200

    except Exception as e:
        print(f"Error in check_duplicate: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Get form data and create student dictionary
        student_data = {
            'regNo': request.form.get('regNo'),
            'rollNo': request.form.get('rollNo'),
            'classSection': request.form.get('classSection'),
            'studentName': request.form.get('studentName'),
            'fatherName': request.form.get('fatherName'),
            'gender': request.form.get('gender'),
            'dob': request.form.get('dob'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'studentContact': request.form.get('studentContact'),
            'parentNo': request.form.get('parentNo'),
            'aadharNo': request.form.get('aadharNo'),
            'bloodGroup': request.form.get('bloodGroup'),
            'state': request.form.get('state'),
            'district': request.form.get('district'),
            'religion': request.form.get('religion'),
            'category': request.form.get('category'),
            'caste': request.form.get('caste'),
            'income': request.form.get('income'),
            'pucRollNo': request.form.get('pucRollNo'),
            'pucYear': request.form.get('pucYear'),
            'pucInstitute': request.form.get('pucInstitute'),
            'pucTotalMarks': request.form.get('pucTotalMarks'),
            'pucObtainedMarks': request.form.get('pucObtainedMarks'),
            'pucPercentage': request.form.get('pucPercentage'),
            'discipline1': request.form.get('discipline1'),
            'lang2': request.form.get('lang2'),
            'yearOfAdmission': request.form.get('yearOfAdmission'),
            'abcId': request.form.get('abcId'),
            'mailId': request.form.get('mailId'),
            'barcode': request.form.get('barcode')
        }

        # Remove None and empty string values
        student_data = {k: v for k, v in student_data.items() if v is not None and v != ''}

        # Validate required fields
        if not student_data.get('rollNo'):
            return jsonify({'error': 'Roll number is required'}), 400

        try:
            # Check for duplicates before saving
            students_ref = db.collection('students')
            roll_query = students_ref.where('rollNo', '==', student_data['rollNo']).limit(1).get()
            
            if any(doc.exists for doc in roll_query):
                return jsonify({
                    'error': f'Student with Roll Number {student_data["rollNo"]} already exists!'
                }), 409

            # Check for duplicate registration number if provided
            if student_data.get('regNo'):
                reg_query = students_ref.where('regNo', '==', student_data['regNo']).limit(1).get()
                if any(doc.exists for doc in reg_query):
                    return jsonify({
                        'error': f'Student with Registration Number {student_data["regNo"]} already exists!'
                    }), 409

            # Use roll number as document ID
            doc_ref = db.collection('students').document(student_data['rollNo'])
            
            # Create new document
            doc_ref.set(student_data)
            print(f"New student data saved for roll number: {student_data['rollNo']}")
            
            return jsonify({
                'message': 'Student data saved successfully!',
                'studentId': student_data['rollNo']
            }), 200

        except Exception as e:
            print(f"Firestore error: {str(e)}")
            return jsonify({'error': f'Database error: {str(e)}'}), 500

    except Exception as e:
        print(f"Error in submit: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/manage')
def manage_students():
    try:
        # Get all students from Firestore
        students_ref = db.collection('students')
        students = students_ref.stream()
        
        # Group students by class
        students_by_class = {}
        for student in students:
            student_data = student.to_dict()
            class_section = student_data.get('classSection', 'Unassigned')
            if class_section not in students_by_class:
                students_by_class[class_section] = []
            students_by_class[class_section].append({
                'id': student.id,
                **student_data
            })
        
        return render_template('student_management.html', students_by_class=students_by_class)
    except Exception as e:
        print(f"Error in manage_students: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/search_students', methods=['POST'])
def search_students():
    try:
        data = request.json
        query = data.get('query', '').strip().lower()  # Convert query to lowercase
        filter_type = data.get('filter', 'all')  # Get filter type
        
        if not query:
            return jsonify({'students': []}), 200

        # Search in Firestore
        students_ref = db.collection('students')
        
        # Get all students (since Firestore doesn't support case-insensitive search directly)
        all_students = students_ref.get()
        
        # Filter students based on case-insensitive search
        students = []
        seen_ids = set()
        
        for doc in all_students:
            student_data = doc.to_dict()
            student_name = student_data.get('studentName', '').lower()
            roll_no = student_data.get('rollNo', '').lower()
            class_section = student_data.get('classSection', '').lower()
            
            # Apply different search logic based on filter type
            match_found = False
            
            if filter_type == 'name':
                # Search only in student name
                if query in student_name:
                    match_found = True
            elif filter_type == 'roll':
                # Search only in roll number
                if query in roll_no:
                    match_found = True
            elif filter_type == 'class':
                # Search only in class section
                if query in class_section:
                    match_found = True
            else:
                # Search in all fields (default)
                if (query in roll_no or 
                    query in student_name or 
                    query in class_section):
                    match_found = True
            
            if match_found and doc.id not in seen_ids:
                # Only include necessary fields
                students.append({
                    'id': doc.id,
                    'studentName': student_data.get('studentName', ''),
                    'rollNo': student_data.get('rollNo', ''),
                    'classSection': student_data.get('classSection', '')
                })
                seen_ids.add(doc.id)
        
        # Limit to 20 results
        students = students[:20]
        
        return jsonify({'students': students}), 200
    except Exception as e:
        print(f"Error in search_students: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/advanced_search', methods=['POST'])
def advanced_search():
    try:
        criteria = request.json
        
        # Search in Firestore
        students_ref = db.collection('students')
        
        # Get all students
        all_students = students_ref.get()
        
        # Filter students based on advanced criteria
        students = []
        seen_ids = set()
        
        for doc in all_students:
            student_data = doc.to_dict()
            
            # Check if student matches all provided criteria
            match = True
            
            # Name criteria
            if criteria.get('name') and criteria['name'].strip():
                if criteria['name'].lower() not in student_data.get('studentName', '').lower():
                    match = False
            
            # Roll number criteria
            if criteria.get('rollNo') and criteria['rollNo'].strip():
                if criteria['rollNo'].lower() not in student_data.get('rollNo', '').lower():
                    match = False
            
            # Class section criteria
            if criteria.get('classSection') and criteria['classSection'].strip():
                if criteria['classSection'].lower() not in student_data.get('classSection', '').lower():
                    match = False
            
            # Gender criteria
            if criteria.get('gender') and criteria['gender'].strip():
                if criteria['gender'] != student_data.get('gender', ''):
                    match = False
            
            # Blood group criteria
            if criteria.get('bloodGroup') and criteria['bloodGroup'].strip():
                if criteria['bloodGroup'] != student_data.get('bloodGroup', ''):
                    match = False
            
            # Category criteria
            if criteria.get('category') and criteria['category'].strip():
                if criteria['category'].lower() not in student_data.get('category', '').lower():
                    match = False
            
            # Address criteria
            if criteria.get('address') and criteria['address'].strip():
                if criteria['address'].lower() not in student_data.get('address', '').lower():
                    match = False
            
            if match and doc.id not in seen_ids:
                # Only include necessary fields
                students.append({
                    'id': doc.id,
                    'studentName': student_data.get('studentName', ''),
                    'rollNo': student_data.get('rollNo', ''),
                    'classSection': student_data.get('classSection', '')
                })
                seen_ids.add(doc.id)
        
        # Limit to 30 results
        students = students[:30]
        
        return jsonify({'students': students}), 200
    except Exception as e:
        print(f"Error in advanced_search: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_student_details/<student_id>')
def get_student_details(student_id):
    try:
        # Get student document from Firestore
        student_doc = db.collection('students').document(student_id).get()
        
        if not student_doc.exists:
            return jsonify({'error': 'Student not found'}), 404
            
        student_data = student_doc.to_dict()
        return jsonify(student_data), 200
    except Exception as e:
        print(f"Error in get_student_details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/edit_student/<student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    try:
        if request.method == 'GET':
            # Get student data for editing
            student_doc = db.collection('students').document(student_id).get()
            
            if not student_doc.exists:
                return jsonify({'error': 'Student not found'}), 404
                
            student_data = student_doc.to_dict()
            return render_template('student_update.html', student=student_data)
            
        else:  # POST request
            # Get form data
            student_data = {
                'regNo': request.form.get('regNo'),
                'rollNo': request.form.get('rollNo'),
                'classSection': request.form.get('classSection'),
                'studentName': request.form.get('studentName'),
                'fatherName': request.form.get('fatherName'),
                'gender': request.form.get('gender'),
                'dob': request.form.get('dob'),
                'email': request.form.get('email'),
                'address': request.form.get('address'),
                'studentContact': request.form.get('studentContact'),
                'parentNo': request.form.get('parentNo'),
                'aadharNo': request.form.get('aadharNo'),
                'bloodGroup': request.form.get('bloodGroup'),
                'state': request.form.get('state'),
                'district': request.form.get('district'),
                'religion': request.form.get('religion'),
                'category': request.form.get('category'),
                'caste': request.form.get('caste'),
                'income': request.form.get('income'),
                'pucRollNo': request.form.get('pucRollNo'),
                'pucYear': request.form.get('pucYear'),
                'pucInstitute': request.form.get('pucInstitute'),
                'pucTotalMarks': request.form.get('pucTotalMarks'),
                'pucObtainedMarks': request.form.get('pucObtainedMarks'),
                'pucPercentage': request.form.get('pucPercentage'),
                'discipline1': request.form.get('discipline1'),
                'lang2': request.form.get('lang2'),
                'yearOfAdmission': request.form.get('yearOfAdmission'),
                'abcId': request.form.get('abcId'),
                'mailId': request.form.get('mailId')
            }
            
            # Remove None and empty string values
            student_data = {k: v for k, v in student_data.items() if v is not None and v != ''}
            
            # Update student document in Firestore
            db.collection('students').document(student_id).update(student_data)
            
            return jsonify({
                'success': True,
                'message': 'Student data updated successfully!',
                'studentId': student_id
            }), 200
            
    except Exception as e:
        print(f"Error in edit_student: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/delete_student/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        # Get the student document reference
        student_ref = db.collection('students').document(student_id)
        student_doc = student_ref.get()
        
        if not student_doc.exists:
            return jsonify({'success': False, 'error': 'Student not found'}), 404
            
        # Delete the student document
        student_ref.delete()
        
        return jsonify({'success': True, 'message': 'Student deleted successfully'})
    except Exception as e:
        print(f"Error deleting student: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 