from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

# Data storage file
DATA_FILE = 'attendance_data.json'

# Initialize data structure
def load_data():
    """Load attendance data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'students': [], 'attendance': []}

def save_data(data):
    """Save attendance data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/students", methods=['GET', 'POST'])
def manage_students():
    """Get all students or add a new student"""
    data = load_data()
    
    if request.method == 'POST':
        student_data = request.json
        new_student = {
            'id': len(data['students']) + 1,
            'name': student_data.get('name'),
            'roll_number': student_data.get('roll_number'),
            'email': student_data.get('email'),
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        data['students'].append(new_student)
        save_data(data)
        return jsonify({'message': 'Student added successfully', 'student': new_student}), 201
    
    return jsonify(data['students']), 200

@app.route("/api/students/<int:student_id>", methods=['GET', 'DELETE', 'PUT'])
def student_detail(student_id):
    """Get, update, or delete a specific student"""
    data = load_data()
    
    student = next((s for s in data['students'] if s['id'] == student_id), None)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    if request.method == 'GET':
        return jsonify(student), 200
    
    elif request.method == 'PUT':
        student_data = request.json
        student.update(student_data)
        save_data(data)
        return jsonify({'message': 'Student updated', 'student': student}), 200
    
    elif request.method == 'DELETE':
        data['students'].remove(student)
        save_data(data)
        return jsonify({'message': 'Student deleted'}), 200

@app.route("/api/attendance", methods=['GET', 'POST'])
def manage_attendance():
    """Get all attendance records or mark attendance"""
    data = load_data()
    
    if request.method == 'POST':
        attendance_data = request.json
        new_record = {
            'id': len(data['attendance']) + 1,
            'student_id': attendance_data.get('student_id'),
            'date': attendance_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'status': attendance_data.get('status'),  # 'Present' or 'Absent'
            'time': datetime.now().strftime('%H:%M:%S')
        }
        data['attendance'].append(new_record)
        save_data(data)
        return jsonify({'message': 'Attendance marked', 'record': new_record}), 201
    
    # Filter by date if provided
    date_filter = request.args.get('date')
    records = data['attendance']
    if date_filter:
        records = [r for r in records if r['date'] == date_filter]
    
    return jsonify(records), 200

@app.route("/api/attendance/<int:student_id>", methods=['GET'])
def student_attendance(student_id):
    """Get attendance records for a specific student"""
    data = load_data()
    
    records = [r for r in data['attendance'] if r['student_id'] == student_id]
    total = len(records)
    present = len([r for r in records if r['status'] == 'Present'])
    absent = len([r for r in records if r['status'] == 'Absent'])
    percentage = (present / total * 100) if total > 0 else 0
    
    return jsonify({
        'records': records,
        'total': total,
        'present': present,
        'absent': absent,
        'attendance_percentage': round(percentage, 2)
    }), 200

@app.route("/api/attendance/report", methods=['GET'])
def attendance_report():
    """Get overall attendance report"""
    data = load_data()
    
    report = []
    for student in data['students']:
        records = [r for r in data['attendance'] if r['student_id'] == student['id']]
        total = len(records)
        present = len([r for r in records if r['status'] == 'Present'])
        absent = len([r for r in records if r['status'] == 'Absent'])
        percentage = (present / total * 100) if total > 0 else 0
        
        report.append({
            'student_id': student['id'],
            'student_name': student['name'],
            'roll_number': student['roll_number'],
            'total_classes': total,
            'present': present,
            'absent': absent,
            'attendance_percentage': round(percentage, 2)
        })
    
    return jsonify(report), 200

@app.route("/api/statistics", methods=['GET'])
def get_statistics():
    """Get overall statistics"""
    data = load_data()
    
    total_students = len(data['students'])
    total_records = len(data['attendance'])
    total_present = len([r for r in data['attendance'] if r['status'] == 'Present'])
    total_absent = len([r for r in data['attendance'] if r['status'] == 'Absent'])
    
    return jsonify({
        'total_students': total_students,
        'total_records': total_records,
        'total_present': total_present,
        'total_absent': total_absent,
        'overall_attendance': round((total_present / total_records * 100) if total_records > 0 else 0, 2)
    }), 200

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0.0',port=5000)