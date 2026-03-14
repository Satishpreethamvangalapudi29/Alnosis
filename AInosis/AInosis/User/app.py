# """
# AInosis Medical Application - Flask Backend with MongoDB
# Complete production-ready implementation
# """

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from flask_pymongo import PyMongo
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime, timedelta
# from bson import ObjectId
# import os
# import jwt
# import random
# import string
# from dotenv import load_dotenv
# from functools import wraps
# from twilio.rest import Client

# # Load environment variables
# load_dotenv()

# # Initialize Twilio client
# TWILIO_ENABLED = all([
#     os.getenv('TWILIO_ACCOUNT_SID'),
#     os.getenv('TWILIO_AUTH_TOKEN'),
#     os.getenv('TWILIO_PHONE_NUMBER')
# ])

# if TWILIO_ENABLED:
#     twilio_client = Client(
#         os.getenv('TWILIO_ACCOUNT_SID'),
#         os.getenv('TWILIO_AUTH_TOKEN')
#     )
#     TWILIO_PHONE = os.getenv('TWILIO_PHONE_NUMBER')
#     print("✅ Twilio SMS enabled")
# else:
#     twilio_client = None
#     TWILIO_PHONE = None
#     print("⚠️  Twilio not configured - OTP will be shown in console")

# # ==================== APP CONFIGURATION ====================
# app = Flask(__name__)
# CORS(app, supports_credentials=True, resources={
#     r"/api/*": {
#         "origins": "*",
#         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#         "allow_headers": ["Content-Type", "Authorization"]
#     }
# })

# # Configuration
# app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ainosis')
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
# app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')
# app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')

# # Initialize MongoDB
# mongo = PyMongo(app)
# db = mongo.db

# # ==================== HELPER FUNCTIONS ====================

# def json_response(data, status=200):
#     """Helper to convert ObjectId to string in JSON responses"""
#     if isinstance(data, list):
#         for item in data:
#             if isinstance(item, dict) and '_id' in item:
#                 item['_id'] = str(item['_id'])
#     elif isinstance(data, dict) and '_id' in data:
#         data['_id'] = str(data['_id'])
#     return jsonify(data), status

# def generate_otp():
#     """Generate 6-digit OTP"""
#     return ''.join(random.choices(string.digits, k=6))

# def send_sms_otp(phone_number, otp):
#     """Send OTP via Twilio SMS"""
#     try:
#         if not TWILIO_ENABLED:
#             print(f"[DEBUG - SMS Disabled] OTP for {phone_number}: {otp}")
#             return True
        
#         message = twilio_client.messages.create(
#             body=f"Your AInosis verification code is: {otp}\n\nValid for 10 minutes.\n\nDo not share this code with anyone.",
#             from_=TWILIO_PHONE,
#             to=phone_number
#         )
        
#         print(f"✅ SMS sent successfully. SID: {message.sid}")
#         return True
#     except Exception as e:
#         print(f"❌ Failed to send SMS: {str(e)}")
#         return False

# def create_jwt_token(user_id):
#     """Create JWT token for authentication"""
#     payload = {
#         'user_id': str(user_id),
#         'exp': datetime.utcnow() + timedelta(days=7)
#     }
#     return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

# def verify_jwt_token(token):
#     """Verify JWT token and return user_id"""
#     try:
#         payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
#         return payload['user_id']
#     except jwt.ExpiredSignatureError:
#         return None
#     except jwt.InvalidTokenError:
#         return None

# def token_required(f):
#     """Decorator to protect routes with JWT authentication"""
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.headers.get('Authorization', '')
#         if token.startswith('Bearer '):
#             token = token[7:]
        
#         user_id = verify_jwt_token(token)
#         if not user_id:
#             return jsonify({'error': 'Unauthorized - Invalid or expired token'}), 401
        
#         # Get user from database
#         user = db.users.find_one({'_id': ObjectId(user_id)})
#         if not user:
#             return jsonify({'error': 'User not found'}), 404
        
#         return f(user, *args, **kwargs)
#     return decorated

# # ==================== AUTHENTICATION ROUTES ====================

# @app.route('/api/auth/send-otp', methods=['POST'])
# def send_otp():
#     """Send OTP to Aadhaar-linked mobile number"""
#     try:
#         data = request.json
#         aadhaar = data.get('aadhaar_number', '').replace('-', '').strip()
#         phone = data.get('phone_number', '').strip()
        
#         if not aadhaar or len(aadhaar) != 12 or not aadhaar.isdigit():
#             return jsonify({'error': 'Invalid Aadhaar number. Must be 12 digits'}), 400
        
#         # Validate phone number (Indian format)
#         if not phone:
#             return jsonify({'error': 'Phone number is required'}), 400
        
#         # Clean phone number and validate
#         phone = phone.replace(' ', '').replace('-', '')
#         if not phone.startswith('+'):
#             # Add India country code if not present
#             if phone.startswith('0'):
#                 phone = '+91' + phone[1:]
#             elif not phone.startswith('91'):
#                 phone = '+91' + phone
#             else:
#                 phone = '+' + phone
        
#         # Validate Indian phone number format
#         if not (phone.startswith('+91') and len(phone) == 13):
#             return jsonify({'error': 'Invalid Indian phone number. Use format: +919876543210'}), 400
        
#         # Generate OTP
#         otp = generate_otp()
        
#         # Delete any existing OTPs for this Aadhaar
#         db.otps.delete_many({'aadhaar_number': aadhaar})
        
#         # Save OTP to database
#         otp_doc = {
#             'aadhaar_number': aadhaar,
#             'phone_number': phone,
#             'otp': otp,
#             'created_at': datetime.utcnow(),
#             'expires_at': datetime.utcnow() + timedelta(minutes=10),
#             'is_used': False
#         }
#         db.otps.insert_one(otp_doc)
        
#         # Send OTP via SMS
#         sms_sent = send_sms_otp(phone, otp)
        
#         response_data = {
#             'message': f'OTP sent successfully to {phone[-4:].rjust(10, "*")}',
#             'phone_masked': phone[-4:].rjust(10, "*")
#         }
        
#         # Only show OTP in development mode if SMS failed
#         if not sms_sent or os.getenv('FLASK_DEBUG', 'False').lower() == 'true':
#             response_data['demo_otp'] = otp  # Remove in production!
#             response_data['note'] = 'OTP shown for development/testing only'
        
#         return jsonify(response_data), 200
        
#     except Exception as e:
#         print(f"Error in send_otp: {str(e)}")
#         return jsonify({'error': 'Failed to send OTP'}), 500

# @app.route('/api/auth/verify-otp', methods=['POST'])
# def verify_otp():
#     """Verify OTP and login/register user"""
#     try:
#         data = request.json
#         aadhaar = data.get('aadhaar_number', '').replace('-', '').strip()
#         otp = data.get('otp', '').strip()
        
#         if not aadhaar or not otp:
#             return jsonify({'error': 'Aadhaar and OTP are required'}), 400
        
#         # Find valid OTP
#         otp_doc = db.otps.find_one({
#             'aadhaar_number': aadhaar,
#             'otp': otp,
#             'is_used': False,
#             'expires_at': {'$gt': datetime.utcnow()}
#         })
        
#         if not otp_doc:
#             return jsonify({'error': 'Invalid or expired OTP'}), 400
        
#         # Mark OTP as used
#         db.otps.update_one(
#             {'_id': otp_doc['_id']},
#             {'$set': {'is_used': True}}
#         )
        
#         # Find or create user
#         user = db.users.find_one({'aadhaar_number': aadhaar})
        
#         if not user:
#             # Create new user
#             user_doc = {
#                 'aadhaar_number': aadhaar,
#                 'name': data.get('name', 'User'),
#                 'phone': data.get('phone', ''),
#                 'blood_group': data.get('blood_group', 'Unknown'),
#                 'date_of_birth': None,
#                 'address': '',
#                 'created_at': datetime.utcnow()
#             }
#             result = db.users.insert_one(user_doc)
#             user = db.users.find_one({'_id': result.inserted_id})
        
#         # Generate JWT token
#         token = create_jwt_token(user['_id'])
        
#         return jsonify({
#             'message': 'Login successful',
#             'token': token,
#             'user': {
#                 'id': str(user['_id']),
#                 'name': user.get('name', 'User'),
#                 'aadhaar': user['aadhaar_number'],
#                 'blood_group': user.get('blood_group', 'Unknown'),
#                 'phone': user.get('phone', '')
#             }
#         }), 200
        
#     except Exception as e:
#         print(f"Error in verify_otp: {str(e)}")
#         return jsonify({'error': 'Verification failed'}), 500

# @app.route('/api/auth/logout', methods=['POST'])
# def logout():
#     """Logout user (client should delete JWT token)"""
#     return jsonify({'message': 'Logged out successfully'}), 200

# # ==================== USER PROFILE ROUTES ====================

# @app.route('/api/user/profile', methods=['GET'])
# @token_required
# def get_user_profile(user):
#     """Get user profile"""
#     try:
#         profile = {
#             'id': str(user['_id']),
#             'name': user.get('name', ''),
#             'aadhaar': user['aadhaar_number'],
#             'phone': user.get('phone', ''),
#             'blood_group': user.get('blood_group', ''),
#             'address': user.get('address', ''),
#             'date_of_birth': user.get('date_of_birth')
#         }
#         return json_response(profile)
#     except Exception as e:
#         print(f"Error in get_user_profile: {str(e)}")
#         return jsonify({'error': 'Failed to fetch profile'}), 500

# @app.route('/api/user/profile', methods=['PUT'])
# @token_required
# def update_user_profile(user):
#     """Update user profile"""
#     try:
#         data = request.json
        
#         update_fields = {}
#         if 'name' in data:
#             update_fields['name'] = data['name']
#         if 'phone' in data:
#             update_fields['phone'] = data['phone']
#         if 'blood_group' in data:
#             update_fields['blood_group'] = data['blood_group']
#         if 'address' in data:
#             update_fields['address'] = data['address']
#         if 'date_of_birth' in data:
#             update_fields['date_of_birth'] = data['date_of_birth']
        
#         if update_fields:
#             db.users.update_one(
#                 {'_id': user['_id']},
#                 {'$set': update_fields}
#             )
        
#         return jsonify({'message': 'Profile updated successfully'}), 200
#     except Exception as e:
#         print(f"Error in update_user_profile: {str(e)}")
#         return jsonify({'error': 'Failed to update profile'}), 500

# # ==================== DOCTOR ROUTES ====================

# @app.route('/api/doctors', methods=['GET'])
# def get_doctors():
#     """Get all doctors or filter by specialty"""
#     try:
#         specialty = request.args.get('specialty')
        
#         query = {}
#         if specialty and specialty != 'all':
#             query['specialty'] = specialty
        
#         doctors = list(db.doctors.find(query))
        
#         # Convert ObjectId to string
#         for doc in doctors:
#             doc['_id'] = str(doc['_id'])
        
#         return json_response(doctors)
#     except Exception as e:
#         print(f"Error in get_doctors: {str(e)}")
#         return jsonify({'error': 'Failed to fetch doctors'}), 500

# @app.route('/api/doctors/<doctor_id>', methods=['GET'])
# def get_doctor(doctor_id):
#     """Get single doctor details"""
#     try:
#         doctor = db.doctors.find_one({'_id': ObjectId(doctor_id)})
#         if not doctor:
#             return jsonify({'error': 'Doctor not found'}), 404
        
#         doctor['_id'] = str(doctor['_id'])
#         return json_response(doctor)
#     except Exception as e:
#         print(f"Error in get_doctor: {str(e)}")
#         return jsonify({'error': 'Failed to fetch doctor'}), 500

# # ==================== APPOINTMENT ROUTES ====================

# @app.route('/api/appointments', methods=['POST'])
# @token_required
# def book_appointment(user):
#     """Book a doctor appointment"""
#     try:
#         data = request.json
        
#         appointment = {
#             'patient_id': user['_id'],
#             'doctor_id': ObjectId(data['doctor_id']),
#             'appointment_date': datetime.fromisoformat(data['appointment_date']),
#             'symptoms': data.get('symptoms', ''),
#             'consultation_type': data.get('consultation_type', 'in-person'),
#             'status': 'scheduled',
#             'created_at': datetime.utcnow()
#         }
        
#         result = db.appointments.insert_one(appointment)
        
#         return jsonify({
#             'message': 'Appointment booked successfully',
#             'appointment_id': str(result.inserted_id)
#         }), 201
#     except Exception as e:
#         print(f"Error in book_appointment: {str(e)}")
#         return jsonify({'error': 'Failed to book appointment'}), 500

# @app.route('/api/appointments', methods=['GET'])
# @token_required
# def get_appointments(user):
#     """Get user's appointments"""
#     try:
#         appointments = list(db.appointments.find({'patient_id': user['_id']}))
        
#         # Populate doctor details
#         for apt in appointments:
#             doctor = db.doctors.find_one({'_id': apt['doctor_id']})
#             apt['_id'] = str(apt['_id'])
#             apt['doctor_id'] = str(apt['doctor_id'])
#             apt['patient_id'] = str(apt['patient_id'])
#             apt['doctor_name'] = doctor['name'] if doctor else 'Unknown'
#             apt['specialty'] = doctor['specialty'] if doctor else ''
#             apt['appointment_date'] = apt['appointment_date'].isoformat()
        
#         return json_response(appointments)
#     except Exception as e:
#         print(f"Error in get_appointments: {str(e)}")
#         return jsonify({'error': 'Failed to fetch appointments'}), 500

# # ==================== MEDICAL RECORDS ROUTES ====================

# @app.route('/api/medical-records', methods=['GET'])
# @token_required
# def get_medical_records(user):
#     """Get user's medical history"""
#     try:
#         records = list(db.medical_records.find(
#             {'patient_id': user['_id']}
#         ).sort('date', -1))
        
#         for record in records:
#             record['_id'] = str(record['_id'])
#             record['patient_id'] = str(record['patient_id'])
#             if 'doctor_id' in record:
#                 record['doctor_id'] = str(record['doctor_id'])
#             if 'date' in record:
#                 record['date'] = record['date'].isoformat()
#             if 'follow_up_date' in record and record['follow_up_date']:
#                 record['follow_up_date'] = record['follow_up_date'].isoformat()
        
#         return json_response(records)
#     except Exception as e:
#         print(f"Error in get_medical_records: {str(e)}")
#         return jsonify({'error': 'Failed to fetch medical records'}), 500

# # ==================== MEDICINE ROUTES ====================

# @app.route('/api/medicines', methods=['GET'])
# def get_medicines():
#     """Get all medicines or filter by category"""
#     try:
#         category = request.args.get('category')
#         search = request.args.get('search')
        
#         query = {}
#         if category:
#             query['category'] = category
#         if search:
#             query['name'] = {'$regex': search, '$options': 'i'}
        
#         medicines = list(db.medicines.find(query))
        
#         for med in medicines:
#             med['_id'] = str(med['_id'])
        
#         return json_response(medicines)
#     except Exception as e:
#         print(f"Error in get_medicines: {str(e)}")
#         return jsonify({'error': 'Failed to fetch medicines'}), 500

# @app.route('/api/medicines/<medicine_id>', methods=['GET'])
# def get_medicine_info(medicine_id):
#     """Get detailed medicine information"""
#     try:
#         medicine = db.medicines.find_one({'_id': ObjectId(medicine_id)})
#         if not medicine:
#             return jsonify({'error': 'Medicine not found'}), 404
        
#         medicine['_id'] = str(medicine['_id'])
#         return json_response(medicine)
#     except Exception as e:
#         print(f"Error in get_medicine_info: {str(e)}")
#         return jsonify({'error': 'Failed to fetch medicine info'}), 500

# # ==================== MEDICINE ORDER ROUTES ====================

# @app.route('/api/orders', methods=['POST'])
# @token_required
# def place_order(user):
#     """Place medicine delivery order"""
#     try:
#         data = request.json
        
#         delivery_charges = {
#             'regular': 40,
#             'emergency': 100,
#             'senior': 20,
#             'disabled': 0
#         }
        
#         order = {
#             'patient_id': user['_id'],
#             'order_items': data['items'],
#             'total_amount': data['total_amount'],
#             'delivery_address': data['delivery_address'],
#             'delivery_type': data.get('delivery_type', 'regular'),
#             'delivery_charge': delivery_charges.get(data.get('delivery_type', 'regular'), 40),
#             'status': 'pending',
#             'order_date': datetime.utcnow(),
#             'delivery_date': None
#         }
        
#         result = db.medicine_orders.insert_one(order)
        
#         return jsonify({
#             'message': 'Order placed successfully',
#             'order_id': str(result.inserted_id),
#             'estimated_delivery': '2-4 hours' if order['delivery_type'] == 'regular' else '30-60 mins'
#         }), 201
#     except Exception as e:
#         print(f"Error in place_order: {str(e)}")
#         return jsonify({'error': 'Failed to place order'}), 500

# @app.route('/api/orders', methods=['GET'])
# @token_required
# def get_orders(user):
#     """Get user's medicine orders"""
#     try:
#         orders = list(db.medicine_orders.find(
#             {'patient_id': user['_id']}
#         ).sort('order_date', -1))
        
#         for order in orders:
#             order['_id'] = str(order['_id'])
#             order['patient_id'] = str(order['patient_id'])
#             order['order_date'] = order['order_date'].isoformat()
#             if order.get('delivery_date'):
#                 order['delivery_date'] = order['delivery_date'].isoformat()
        
#         return json_response(orders)
#     except Exception as e:
#         print(f"Error in get_orders: {str(e)}")
#         return jsonify({'error': 'Failed to fetch orders'}), 500

# # ==================== MEDICAL STORES ROUTES ====================

# @app.route('/api/medical-stores', methods=['GET'])
# def get_medical_stores():
#     """Get nearby medical stores"""
#     try:
#         stores = list(db.medical_stores.find())
        
#         for store in stores:
#             store['_id'] = str(store['_id'])
        
#         return json_response(stores)
#     except Exception as e:
#         print(f"Error in get_medical_stores: {str(e)}")
#         return jsonify({'error': 'Failed to fetch medical stores'}), 500

# # ==================== HOSPITALS ROUTES ====================

# @app.route('/api/hospitals', methods=['GET'])
# def get_hospitals():
#     """Get nearby hospitals"""
#     try:
#         hospitals = list(db.hospitals.find())
        
#         for hospital in hospitals:
#             hospital['_id'] = str(hospital['_id'])
        
#         return json_response(hospitals)
#     except Exception as e:
#         print(f"Error in get_hospitals: {str(e)}")
#         return jsonify({'error': 'Failed to fetch hospitals'}), 500

# # ==================== CARE PROGRAMS ROUTES ====================

# @app.route('/api/care-programs', methods=['GET'])
# def get_care_programs():
#     """Get long-term care programs"""
#     try:
#         condition = request.args.get('condition')
        
#         query = {}
#         if condition:
#             query['condition'] = condition
        
#         programs = list(db.care_programs.find(query))
        
#         for program in programs:
#             program['_id'] = str(program['_id'])
#             if 'specialist_id' in program:
#                 specialist = db.doctors.find_one({'_id': program['specialist_id']})
#                 if specialist:
#                     program['specialist'] = {
#                         'name': specialist['name'],
#                         'specialty': specialist['specialty']
#                     }
        
#         return json_response(programs)
#     except Exception as e:
#         print(f"Error in get_care_programs: {str(e)}")
#         return jsonify({'error': 'Failed to fetch care programs'}), 500

# @app.route('/api/care-programs/<program_id>/enroll', methods=['POST'])
# @token_required
# def enroll_in_program(user, program_id):
#     """Enroll in a care program"""
#     try:
#         program = db.care_programs.find_one({'_id': ObjectId(program_id)})
#         if not program:
#             return jsonify({'error': 'Program not found'}), 404
        
#         enrollment = {
#             'patient_id': user['_id'],
#             'program_id': ObjectId(program_id),
#             'enrolled_at': datetime.utcnow(),
#             'status': 'active'
#         }
        
#         db.care_enrollments.insert_one(enrollment)
        
#         return jsonify({'message': 'Enrolled successfully'}), 200
#     except Exception as e:
#         print(f"Error in enroll_in_program: {str(e)}")
#         return jsonify({'error': 'Failed to enroll in program'}), 500

# # ==================== EMERGENCY TUTORIALS ROUTES ====================

# @app.route('/api/tutorials', methods=['GET'])
# def get_tutorials():
#     """Get emergency tutorials"""
#     try:
#         tutorial_type = request.args.get('type')
#         category = request.args.get('category')
        
#         query = {}
#         if tutorial_type and tutorial_type != 'all':
#             query['type'] = tutorial_type
#         if category:
#             query['category'] = category
        
#         tutorials = list(db.emergency_tutorials.find(query))
        
#         for tutorial in tutorials:
#             tutorial['_id'] = str(tutorial['_id'])
        
#         return json_response(tutorials)
#     except Exception as e:
#         print(f"Error in get_tutorials: {str(e)}")
#         return jsonify({'error': 'Failed to fetch tutorials'}), 500

# @app.route('/api/tutorials/<tutorial_id>', methods=['GET'])
# def get_tutorial(tutorial_id):
#     """Get single tutorial details"""
#     try:
#         tutorial = db.emergency_tutorials.find_one({'_id': ObjectId(tutorial_id)})
#         if not tutorial:
#             return jsonify({'error': 'Tutorial not found'}), 404
        
#         # Increment views
#         db.emergency_tutorials.update_one(
#             {'_id': ObjectId(tutorial_id)},
#             {'$inc': {'views': 1}}
#         )
        
#         tutorial['_id'] = str(tutorial['_id'])
#         return json_response(tutorial)
#     except Exception as e:
#         print(f"Error in get_tutorial: {str(e)}")
#         return jsonify({'error': 'Failed to fetch tutorial'}), 500

# # ==================== AI CHATBOT ROUTES ====================

# @app.route('/api/symptom-checker', methods=['POST'])
# def symptom_checker():
#     """AI Symptom Checker"""
#     try:
#         data = request.json
#         symptoms = data.get('symptoms', '').lower()
        
#         # Simple rule-based responses (replace with AI model in production)
#         responses = {
#             'fever': {
#                 'assessment': 'You may have a viral infection',
#                 'risk_level': 'Low',
#                 'recommendations': [
#                     'Rest and stay hydrated',
#                     'Take Paracetamol for fever',
#                     'Monitor temperature'
#                 ],
#                 'consult_if': 'Fever persists beyond 3 days or exceeds 103°F'
#             },
#             'chest': {
#                 'assessment': 'Chest pain requires immediate attention',
#                 'risk_level': 'HIGH',
#                 'recommendations': [
#                     'Seek emergency care immediately',
#                     'Do not drive yourself',
#                     'Call emergency services: 108'
#                 ],
#                 'consult_if': 'Immediate medical attention required'
#             }
#         }
        
#         for keyword, response in responses.items():
#             if keyword in symptoms:
#                 return json_response(response)
        
#         return json_response({
#             'assessment': 'Unable to determine',
#             'risk_level': 'Moderate',
#             'recommendations': ['Consult with a doctor for proper diagnosis'],
#             'consult_if': 'Symptoms persist'
#         })
#     except Exception as e:
#         print(f"Error in symptom_checker: {str(e)}")
#         return jsonify({'error': 'Failed to process symptoms'}), 500

# @app.route('/api/medicine-info', methods=['POST'])
# def medicine_info_bot():
#     """AI Medicine Information Bot"""
#     try:
#         data = request.json
#         medicine_name = data.get('medicine_name', '').lower()
        
#         medicine = db.medicines.find_one({
#             'name': {'$regex': medicine_name, '$options': 'i'}
#         })
        
#         if medicine:
#             return json_response({
#                 'found': True,
#                 'name': medicine['name'],
#                 'uses': medicine.get('uses', ''),
#                 'dosage': medicine.get('dosage', ''),
#                 'side_effects': medicine.get('side_effects', ''),
#                 'precautions': medicine.get('precautions', '')
#             })
        
#         return json_response({
#             'found': False,
#             'message': 'Medicine not found in our database'
#         }, 404)
#     except Exception as e:
#         print(f"Error in medicine_info_bot: {str(e)}")
#         return jsonify({'error': 'Failed to fetch medicine info'}), 500

# # ==================== DATABASE INITIALIZATION ====================

# @app.route('/api/init-db', methods=['GET'])
# def init_database():
#     """Initialize database with sample data (DEVELOPMENT ONLY!)"""
#     try:
#         # Clear existing data
#         db.doctors.delete_many({})
#         db.medicines.delete_many({})
#         db.medical_stores.delete_many({})
#         db.hospitals.delete_many({})
#         db.emergency_tutorials.delete_many({})
#         db.care_programs.delete_many({})
        
#         # Insert sample doctors
#         doctors = [
#             {
#                 'name': 'Dr. Priya Sharma',
#                 'specialty': 'General Physician',
#                 'hospital': 'Apollo Hospital',
#                 'location': 'Koramangala, Bangalore',
#                 'qualifications': ['MBBS', 'MD'],
#                 'experience': 15,
#                 'consultation_fee': 500,
#                 'rating': 4.8,
#                 'is_available': True,
#                 'avatar_url': 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=150',
#                 'phone': '+91 98765 43210',
#                 'email': 'priya.sharma@example.com'
#             },
#             {
#                 'name': 'Dr. Amit Patel',
#                 'specialty': 'Cardiologist',
#                 'hospital': 'Fortis Hospital',
#                 'location': 'Whitefield, Bangalore',
#                 'qualifications': ['MBBS', 'DM', 'FACC'],
#                 'experience': 20,
#                 'consultation_fee': 1200,
#                 'rating': 4.9,
#                 'is_available': True,
#                 'avatar_url': 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=150',
#                 'phone': '+91 98765 43211',
#                 'email': 'amit.patel@example.com'
#             }
#         ]
#         db.doctors.insert_many(doctors)
        
#         # Insert sample medicines
#         medicines = [
#             {
#                 'name': 'Paracetamol 500mg',
#                 'manufacturer': 'Cipla',
#                 'category': 'Pain Relief',
#                 'price': 25,
#                 'dosage': '1 tablet every 6 hours',
#                 'description': 'Pain reliever and fever reducer',
#                 'uses': 'Fever reduction, mild to moderate pain relief',
#                 'side_effects': 'Rare - allergic reactions, rash',
#                 'precautions': 'Do not exceed dose. Avoid with alcohol.',
#                 'stock_quantity': 500
#             },
#             {
#                 'name': 'Metformin 500mg',
#                 'manufacturer': 'Sun Pharma',
#                 'category': 'Diabetes',
#                 'price': 45,
#                 'dosage': '1 tablet twice daily with meals',
#                 'description': 'Blood sugar control medication',
#                 'uses': 'Control blood sugar in Type 2 Diabetes',
#                 'side_effects': 'Nausea, diarrhea, stomach upset',
#                 'precautions': 'Regular blood sugar monitoring required',
#                 'stock_quantity': 300
#             }
#         ]
#         db.medicines.insert_many(medicines)
        
#         return jsonify({'message': 'Database initialized successfully with sample data'}), 200
#     except Exception as e:
#         print(f"Error in init_database: {str(e)}")
#         return jsonify({'error': 'Failed to initialize database'}), 500

# # ==================== HEALTH CHECK ====================

# @app.route('/api/health', methods=['GET'])
# def health_check():
#     """Health check endpoint"""
#     try:
#         # Test MongoDB connection
#         db.command('ping')
#         return jsonify({
#             'status': 'healthy',
#             'message': 'Server is running',
#             'database': 'connected'
#         }), 200
#     except Exception as e:
#         return jsonify({
#             'status': 'unhealthy',
#             'message': 'Database connection failed',
#             'error': str(e)
#         }), 500

# # ==================== ERROR HANDLERS ====================

# @app.errorhandler(404)
# def not_found(error):
#     return jsonify({'error': 'Endpoint not found'}), 404

# @app.errorhandler(500)
# def internal_error(error):
#     return jsonify({'error': 'Internal server error'}), 500

# # ==================== RUN APPLICATION ====================

# if __name__ == '__main__':
#     port = int(os.getenv('PORT', 5000))
#     debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
#     print(f"""
#     ╔═══════════════════════════════════════════════════════╗
#     ║           AInosis Medical Application                 ║
#     ║                Flask Backend Server                   ║
#     ╠═══════════════════════════════════════════════════════╣
#     ║  Server running on: http://localhost:{port}           ║
#     ║  API Base URL: http://localhost:{port}/api            ║
#     ║  Debug Mode: {debug}                                  ║
#     ╚═══════════════════════════════════════════════════════╝
    
#     Quick Start:
#     1. Initialize DB: GET http://localhost:{port}/api/init-db
#     2. Test health: GET http://localhost:{port}/api/health
#     3. Send OTP: POST http://localhost:{port}/api/auth/send-otp
#     """)
    
#     app.run(
#         debug=debug,
#         host='0.0.0.0',
#         port=port
#     )

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from twilio.rest import Client
import random
from openai import OpenAI
import json
from datetime import datetime

load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

# Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize clients
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# In-memory storage (replace with database in production)
users_db = {}
otp_store = {}
chat_history = {}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/api/check-user', methods=['POST'])
def check_user():
    """Check if user exists"""
    data = request.json
    aadhaar = data.get('aadhaar', '').replace('-', '')
    
    if not aadhaar or len(aadhaar) != 12:
        return jsonify({'error': 'Invalid Aadhaar number'}), 400
    
    user_exists = aadhaar in users_db
    return jsonify({
        'exists': user_exists,
        'user': users_db.get(aadhaar) if user_exists else None
    })

@app.route('/api/signup', methods=['POST'])
def signup():
    """Register new user"""
    data = request.json
    aadhaar = data.get('aadhaar', '').replace('-', '')
    name = data.get('name', '')
    phone = data.get('phone', '')
    blood_group = data.get('blood_group', '')
    
    if not all([aadhaar, name, phone]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if aadhaar in users_db:
        return jsonify({'error': 'User already exists'}), 400
    
    # Store user data
    users_db[aadhaar] = {
        'aadhaar': aadhaar,
        'name': name,
        'phone': phone,
        'blood_group': blood_group,
        'created_at': datetime.now().isoformat(),
        'medical_history': []
    }
    
    return jsonify({
        'success': True,
        'message': 'User registered successfully'
    })

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    """Send OTP via Twilio"""
    data = request.json
    aadhaar = data.get('aadhaar', '').replace('-', '')
    
    if aadhaar not in users_db:
        return jsonify({'error': 'User not found. Please signup first.'}), 404
    
    user = users_db[aadhaar]
    phone = user['phone']
    
    # Generate OTP
    otp = str(random.randint(100000, 999999))
    otp_store[aadhaar] = otp
    
    try:
        # Send OTP via Twilio
        message = twilio_client.messages.create(
            body=f'Your AInosis verification code is: {otp}',
            from_=TWILIO_PHONE_NUMBER,
            to=phone
        )
        
        return jsonify({
            'success': True,
            'message': 'OTP sent successfully',
            'phone': phone[-4:]  # Last 4 digits for display
        })
    except Exception as e:
        # For development/testing, return OTP in response
        print(f"Twilio error: {str(e)}")
        return jsonify({
            'success': True,
            'message': 'OTP sent (dev mode)',
            'otp': otp,  # Remove in production!
            'phone': phone[-4:]
        })

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and login"""
    data = request.json
    aadhaar = data.get('aadhaar', '').replace('-', '')
    otp = data.get('otp', '')
    
    if aadhaar not in users_db:
        return jsonify({'error': 'User not found'}), 404
    
    if aadhaar not in otp_store:
        return jsonify({'error': 'OTP not sent or expired'}), 400
    
    if otp_store[aadhaar] != otp:
        return jsonify({'error': 'Invalid OTP'}), 401
    
    # OTP verified, remove from store
    del otp_store[aadhaar]
    
    user = users_db[aadhaar]
    return jsonify({
        'success': True,
        'user': user,
        'message': 'Login successful'
    })

@app.route('/api/chat/symptom', methods=['POST'])
def symptom_chat():
    """AI Symptom Assistant"""
    data = request.json
    user_message = data.get('message', '')
    aadhaar = data.get('aadhaar', '')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Initialize chat history for user
    if aadhaar not in chat_history:
        chat_history[aadhaar] = {'symptom': [], 'medicine': []}
    
    # Add user message to history
    chat_history[aadhaar]['symptom'].append({
        'role': 'user',
        'content': user_message
    })
    
    try:
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a medical symptom assessment AI assistant. 
                    Provide preliminary symptom analysis and risk assessment.
                    IMPORTANT: 
                    - Always include a disclaimer that this is not a diagnosis
                    - For serious symptoms, strongly recommend seeing a doctor
                    - Use clear, structured format with possible conditions, risk level, and recommendations
                    - Keep responses concise and actionable"""
                },
                *chat_history[aadhaar]['symptom'][-10:]  # Last 10 messages
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        assistant_message = response.choices[0].message.content
        
        # Add assistant response to history
        chat_history[aadhaar]['symptom'].append({
            'role': 'assistant',
            'content': assistant_message
        })
        
        return jsonify({
            'success': True,
            'response': assistant_message
        })
    
    except Exception as e:
        return jsonify({'error': f'AI service error: {str(e)}'}), 500

@app.route('/api/chat/medicine', methods=['POST'])
def medicine_chat():
    """AI Medicine Information Assistant"""
    data = request.json
    user_message = data.get('message', '')
    aadhaar = data.get('aadhaar', '')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Initialize chat history for user
    if aadhaar not in chat_history:
        chat_history[aadhaar] = {'symptom': [], 'medicine': []}
    
    # Add user message to history
    chat_history[aadhaar]['medicine'].append({
        'role': 'user',
        'content': user_message
    })
    
    try:
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a medicine information assistant. 
                    STRICT RULES:
                    - ONLY respond to medicine-related queries
                    - If asked about anything other than medicines, politely decline and redirect
                    - Provide: uses, dosage, side effects, and precautions
                    - Always remind users to follow their doctor's prescription
                    - Keep responses structured and easy to read
                    - For non-medicine questions, say: "I can only provide medicine information. Please ask about a specific medicine."
                    """
                },
                *chat_history[aadhaar]['medicine'][-10:]
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        assistant_message = response.choices[0].message.content
        
        # Add assistant response to history
        chat_history[aadhaar]['medicine'].append({
            'role': 'assistant',
            'content': assistant_message
        })
        
        return jsonify({
            'success': True,
            'response': assistant_message
        })
    
    except Exception as e:
        return jsonify({'error': f'AI service error: {str(e)}'}), 500

@app.route('/api/user/<aadhaar>', methods=['GET'])
def get_user(aadhaar):
    """Get user data"""
    aadhaar = aadhaar.replace('-', '')
    if aadhaar not in users_db:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(users_db[aadhaar])

@app.route('/api/user/<aadhaar>/medical-history', methods=['POST'])
def add_medical_record(aadhaar):
    """Add medical history record"""
    aadhaar = aadhaar.replace('-', '')
    if aadhaar not in users_db:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    record = {
        'id': len(users_db[aadhaar]['medical_history']) + 1,
        'date': datetime.now().isoformat(),
        **data
    }
    
    users_db[aadhaar]['medical_history'].append(record)
    
    return jsonify({
        'success': True,
        'record': record
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)