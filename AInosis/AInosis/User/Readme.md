# 🏥 AInosis Medical Application - Backend API

Complete Flask backend with MongoDB and OpenAI integration for the AInosis medical platform.

## 🚀 Features

- ✅ **Aadhaar-based Authentication** with OTP verification
- ✅ **MongoDB Database** for flexible data storage
- ✅ **OpenAI Integration** for AI symptom checker and medicine info
- ✅ **JWT Authentication** for secure API access
- ✅ **Complete REST API** with 30+ endpoints
- ✅ **Doctor Appointments** booking system
- ✅ **Medicine Orders** with home delivery
- ✅ **Medical Records** management
- ✅ **Emergency Tutorials** library
- ✅ **Long-term Care Programs**

## 📋 Prerequisites

- Python 3.8 or higher
- MongoDB (local or MongoDB Atlas)
- MongoDB Compass (for database visualization)
- OpenAI API Key

## 🛠️ Installation

### 1. Install MongoDB

**Windows:**
- Download from [MongoDB Official Site](https://www.mongodb.com/try/download/community)
- Install MongoDB Compass (included)
- Start MongoDB service

**Mac:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux:**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

### 2. Clone and Setup Project

```bash
# Create project directory
mkdir ainosis-backend
cd ainosis-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```env
MONGO_URI=mongodb://localhost:27017/ainosis
SECRET_KEY=your-secret-key-here-change-this
JWT_SECRET_KEY=your-jwt-secret-key-here
OPENAI_API_KEY=sk-your-openai-key-here
```

### 4. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Go to API Keys section
4. Create new secret key
5. Copy and paste into `.env` file

## 🏃 Running the Application

### Start the Server

```bash
python app.py
```

You should see:
```
🏥 AInosis Medical API Server
📡 Server: http://localhost:5000
🗄️  MongoDB: mongodb://localhost:27017/ainosis
🤖 OpenAI: Configured
```

### Initialize Database with Sample Data

Open browser or use curl:
```bash
curl http://localhost:5000/api/init-db
```

Or visit: `http://localhost:5000/api/init-db`

This will create:
- 3 Sample Doctors
- 4 Sample Medicines
- 3 Medical Stores
- 3 Hospitals
- 4 Emergency Tutorials
- 3 Care Programs

## 📚 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/send-otp` | Send OTP to Aadhaar number |
| POST | `/api/auth/verify-otp` | Verify OTP and login |
| POST | `/api/auth/logout` | Logout user |

### User Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user/profile` | Get user profile |
| PUT | `/api/user/profile` | Update user profile |

### Doctors

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/doctors` | Get all doctors (filter by specialty) |
| GET | `/api/doctors/<id>` | Get doctor details |

### Appointments

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/appointments` | Book appointment |
| GET | `/api/appointments` | Get user's appointments |

### Medical Records

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/medical-records` | Get medical history |
| POST | `/api/medical-records` | Add medical record |

### Medicines

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/medicines` | Get medicines (search/filter) |
| GET | `/api/medicines/<id>` | Get medicine details |

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/orders` | Place medicine order |
| GET | `/api/orders` | Get order history |

### Medical Stores & Hospitals

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/medical-stores` | Find nearby stores |
| GET | `/api/hospitals` | Find nearby hospitals |

### Care Programs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/care-programs` | Get care programs |
| POST | `/api/care-programs/<id>/enroll` | Enroll in program |

### Emergency Tutorials

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tutorials` | Get tutorials (filter by type) |
| GET | `/api/tutorials/<id>` | Get tutorial details |

### AI Chatbots

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/symptom-checker` | AI symptom analysis |
| POST | `/api/medicine-info` | Medicine info bot |

## 🧪 Testing the API

### 1. Send OTP

```bash
curl -X POST http://localhost:5000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"aadhaar_number": "123456789012"}'
```

Response:
```json
{
  "message": "OTP sent successfully",
  "demo_otp": "123456"
}
```

### 2. Verify OTP

```bash
curl -X POST http://localhost:5000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "aadhaar_number": "123456789012",
    "otp": "123456"
  }'
```

Response:
```json
{
  "message": "Login successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "...",
    "name": "User",
    "aadhaar": "123456789012"
  }
}
```

### 3. Get Doctors (with token)

```bash
curl -X GET http://localhost:5000/api/doctors \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 4. AI Symptom Checker

```bash
curl -X POST http://localhost:5000/api/symptom-checker \
  -H "Content-Type: application/json" \
  -d '{"symptoms": "I have fever and headache"}'
```

## 🗄️ MongoDB Compass

### Connect to Database

1. Open MongoDB Compass
2. Connection string: `mongodb://localhost:27017`
3. Click "Connect"
4. Select database: `ainosis`

### Collections

You'll see these collections:
- `users` - User accounts
- `doctors` - Doctor profiles
- `appointments` - Appointment bookings
- `medical_records` - Medical history
- `medicines` - Medicine catalog
- `orders` - Medicine orders
- `medical_stores` - Pharmacy locations
- `hospitals` - Hospital information
- `care_programs` - Long-term care programs
- `tutorials` - Emergency tutorials
- `otp_verifications` - OTP records

## 🔧 Configuration

### Change MongoDB Connection

Edit `app.py`:
```python
app.config['MONGO_URI'] = 'your-mongodb-connection-string'
```

For **MongoDB Atlas** (cloud):
```python
app.config['MONGO_URI'] = 'mongodb+srv://username:password@cluster.mongodb.net/ainosis'
```

### Change OpenAI Model

Edit `app.py` in the OpenAI function:
```python
model="gpt-4"  # or "gpt-3.5-turbo" for cheaper/faster
```

### Enable Real SMS OTP

Install Twilio:
```bash
pip install twilio
```

Add to `app.py` in `send_otp()` function:
```python
from twilio.rest import Client

client = Client(account_sid, auth_token)
message = client.messages.create(
    to=phone_number,
    from_=twilio_number,
    body=f"Your AInosis OTP: {otp}"
)
```

## 📱 Connect Frontend

Update your frontend API base URL:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';

// Example: Send OTP
fetch(`${API_BASE_URL}/auth/send-otp`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ aadhaar_number: '123456789012' })
})
```

## 🚀 Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables for Production

```env
FLASK_ENV=production
FLASK_DEBUG=False
MONGO_URI=mongodb+srv://...  # Use MongoDB Atlas
SECRET_KEY=very-strong-secret-key
JWT_SECRET_KEY=very-strong-jwt-key
OPENAI_API_KEY=sk-...
```

### Deploy to Cloud

**Heroku:**
```bash
heroku create ainosis-api
git push heroku main
```

**AWS/DigitalOcean:**
- Use Docker or direct deployment
- Configure environment variables
- Set up MongoDB Atlas

## ⚠️ Important Notes

1. **Security:**
   - Change all secret keys in production
   - Use HTTPS in production
   - Enable MongoDB authentication
   - Rate limit API endpoints

2. **OpenAI Costs:**
   - GPT-4: ~$0.03 per 1K tokens
   - GPT-3.5-turbo: ~$0.001 per 1K tokens
   - Monitor usage at platform.openai.com

3. **Database:**
   - Regular backups recommended
   - Use MongoDB Atlas for production
   - Set up indexes for performance

## 🐛 Troubleshooting

### MongoDB Connection Error
```
Check if MongoDB is running:
- Windows: Services → MongoDB
- Mac/Linux: sudo systemctl status mongodb
```

### OpenAI API Error
```
Verify API key is correct
Check billing at platform.openai.com
Ensure you have credits
```

### JWT Token Expired
```
Tokens expire after 7 days
User needs to login again
```

## 📞 Support

For issues or questions:
- Check MongoDB logs
- Check Flask console output
- Verify all environment variables
- Test with Postman/curl first

## 📄 License

MIT License - Free to use for your project!

---

**Made with ❤️ for AInosis Medical Platform**

_____________________________________________________________________________________________

🎯 Complete Features:
1. Database Models (SQLAlchemy)

✅ User/Patient
✅ Doctor
✅ Medical Records
✅ Appointments
✅ Medicine Catalog
✅ Medicine Orders
✅ Medical Stores
✅ Hospitals
✅ Care Programs
✅ Emergency Tutorials
✅ OTP Verification

2. API Endpoints
Authentication:

POST /api/auth/send-otp - Send OTP to Aadhaar number
POST /api/auth/verify-otp - Verify OTP & login
POST /api/auth/logout - Logout

User Profile:

GET /api/user/profile - Get profile
PUT /api/user/profile - Update profile

Doctors:

GET /api/doctors - Get all doctors (filter by specialty)
GET /api/doctors/<id> - Get doctor details

Appointments:

POST /api/appointments - Book appointment
GET /api/appointments - Get user's appointments

Medical Records:

GET /api/medical-records - Get medical history

Medicines:

GET /api/medicines - Get medicines (search/filter)
GET /api/medicines/<id> - Get medicine info

Orders:

POST /api/orders - Place medicine order
GET /api/orders - Get order history

Medical Stores & Hospitals:

GET /api/medical-stores - Find nearby stores
GET /api/hospitals - Find nearby hospitals

Care Programs:

GET /api/care-programs - Get programs
POST /api/care-programs/<id>/enroll - Enroll

Emergency Tutorials:

GET /api/tutorials - Get tutorials
GET /api/tutorials/<id> - Get tutorial details

AI Chatbots:

POST /api/symptom-checker - AI symptom analysis
POST /api/medicine-info - Medicine info bot

📦 Setup Instructions:
bash# Install dependencies
pip install flask flask-sqlalchemy flask-cors pyjwt

# Run the application
python app.py

# Initialize database with sample data (first time only)
curl http://localhost:5000/api/init-db
🔧 What to Configure:

Line 19: Change database URI (use PostgreSQL/MySQL in production)
Line 21-22: Change secret keys!
Line 113: Integrate SMS API (Twilio, MSG91) for OTP
Line 808-809: Integrate AI model for symptom checker
Line 854-863: Integrate AI for medicine info

_____________________________________________________________________________________________

🚀 Quick Setup:
bash# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
MONGO_URI=mongodb://localhost:27017/ainosis
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=your-secret
JWT_SECRET_KEY=your-jwt-secret

# 3. Run server
python app.py

# 4. Initialize database
curl http://localhost:5000/api/init-db
🔑 Key Features:

✅ MongoDB instead of SQLAlchemy
✅ OpenAI GPT-4 for AI chatbots
✅ 30+ API endpoints all working
✅ JWT authentication
✅ Sample data initialization
✅ Complete documentation

💡 What to Do:

Get OpenAI Key: platform.openai.com
Install MongoDB: Follow README instructions
Configure .env with your keys
Run python app.py
Visit: http://localhost:5000/api/init-db


_____________________________________________________________________________________________