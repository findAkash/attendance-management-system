import qrcode
import time
import threading
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from io import BytesIO
from datetime import datetime, timedelta
from pydantic import BaseModel
from config import Config
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from auth import verify_jwt_token
from urllib.parse import quote, unquote


app = FastAPI()

# MongoDB connection
client = MongoClient(Config.DATABASE_URL)
db = client["test"]



# OAuth2PasswordBearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

current_qr_code_data = ""
qr_code_expiry_time = datetime.utcnow()

class AttendanceData(BaseModel):
    class_schedule_id: str
    timestamp: float


# Function to generate a new QR code
def generate_qr_code(data: str) -> qrcode.image:
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return img

# Function to update the QR code every 3 seconds
def update_qr_code():
    global current_qr_code_data, qr_code_expiry_time
    while True:
        current_qr_code_data = str(int(time.time()))
        qr_code_expiry_time = datetime.utcnow() + timedelta(seconds=3)
        time.sleep(Config.QR_REFRESH_INTERVAL)

# Start the QR code update in a separate thread
qr_code_thread = threading.Thread(target=update_qr_code)
qr_code_thread.start()

@app.get("/professor/generate-qr-attendance")
def get_qr_code(scheduled_class_id: str):
    global current_qr_code_data
    timestamp = datetime.utcnow().isoformat()
    encoded_timestamp = quote(timestamp)
    qr_data = {
        "url": f"http://localhost:8000/mark-attendance/{scheduled_class_id}",
        "timestamp": encoded_timestamp
    }
    current_qr_code_data = qr_data

    qr_data_str = f"{qr_data['url']}?timestamp={qr_data['timestamp']}"
    img = generate_qr_code(qr_data_str)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")

@app.post("/mark-attendance/{scheduled_class_id}/{time}")
def mark_attendance(scheduled_class_id: str, time: str, token: str = Depends(oauth2_scheme)):
    # Decode and parse the datetime string
    try:
        qr_code_time = datetime.fromisoformat(time)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")

    # Check if the QR code is expired
    if datetime.utcnow() > qr_code_time + timedelta(seconds=Config.QR_REFRESH_INTERVAL):
        raise HTTPException(status_code=400, detail="Invalid or expired QR code")

    # Verify the JWT token
    response = verify_jwt_token(token)
    if not response['success']:
        raise HTTPException(status_code=401, detail=response['message'])

    user_id = response['data']['_id']
    student = db.students.find_one({"user": user_id})
    if student is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Update attendance in the database
    result = db.attendance.update_one(
        {"classSchedule": scheduled_class_id, "attendeeId": student["_id"]},
        {"$set": {"status": "Present"}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    return {"message": "Attendance marked successfully"}

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "QR Code Attendance System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
