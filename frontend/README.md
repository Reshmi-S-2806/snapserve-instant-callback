 # SnapServe Lead Connect
An automated, AI-powered voice lead generation platform. The system captures lead inquiries through a React frontend, persists records in MongoDB Atlas, and dispatches real-time outbound calls using the SnapServe voice agent platform via a FastAPI backend service.

# Tech Stack
Frontend: React.js, Tailwind CSS / CSS3, Axios

Backend: FastAPI, Python 3.10+, httpx, motor (Async MongoDB driver)

Database: MongoDB Atlas

Voice Integration: SnapServe API / Campaign Webhooks

Deployment Platform: Vercel (Frontend), Render (Backend)

Local Development Setup
1. Backend Setup

cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI dev server
uvicorn main:app --reload --port 8000
FastAPI Interactive Docs will be accessible at

2. Frontend Setup

cd frontend

# Install Node dependencies
npm install

# Start development server
npm start

Deployment Guide
Deploying Backend to Render
Create a new Web Service on Render and connect your GitHub repository.

Configure settings:

Root Directory: backend

Environment: Python

Build Command: pip install -r requirements.txt

Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT

Add environment variables under Environment:

MONGO_URI

SNAPSERVE_API_KEY

SNAPSERVE_AGENT_ID

SNAPSERVE_API_URL

Deploy the service and copy your public Render domain (https://<your-service-name>.onrender.com).

Deploying Frontend to Vercel

Import your GitHub repository into Vercel.

Configure project settings:

Root Directory: frontend

Framework Preset: Create React App

Add Environment Variable:

REACT_APP_API_BASE_URL: https://<your-service-name>[.onrender.com/api](https://.onrender.com/api)

Deploy the project.

API Documentation

POST /api/leads
Captures lead information, saves the record to MongoDB Atlas, and triggers the SnapServe outbound call.

Request Body:

JSON
{
  "name": "John Doe",
  "phone_number": "+1234567890",
  "email": "john@example.com",
  "service_interest": "General Inquiry"
}
Response (201 Created):

JSON
{
  "message": "Lead saved and call initiated successfully!",
  "lead_id": "66d6a2f...",
  "call_id": "cf73d82d-e893-4e09-937a-7db9db46b76c"
}
POST /api/webhooks/snapserve
Webhook listener that receives status updates from SnapServe and updates MongoDB lead records.

Payload Example:

JSON
{
  "call_id": "cf73d82d-e893-4e09-937a-7db9db46b76c",
  "status": "completed",
  "duration": 45
}
