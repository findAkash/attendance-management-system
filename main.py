import qrcode
import time
import threading
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from datetime import datetime, timedelta
from pydantic import BaseModel

app = FastAPI()

current_qr_code_data = ""
qr_code_expiry_time = datetime.utcnow()

class Attendance(BaseModel):
    qr_code_data: str
    user_id: str

# Function to generate a new QR code
def generate_qr_code(data):
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
        time.sleep(3)

# Start the QR code update in a separate thread
qr_code_thread = threading.Thread(target=update_qr_code)
qr_code_thread.start()

@app.get("/qr-code")
def get_qr_code():
    img = generate_qr_code(current_qr_code_data)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

@app.post("/mark-attendance")
def mark_attendance(attendance: Attendance):
    if attendance.qr_code_data != current_qr_code_data:
        raise HTTPException(status_code=400, detail="Invalid or expired QR code")
    # Here you would mark the attendance in your database
    return {"message": "Attendance marked successfully"}

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "QR Code Attendance System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
