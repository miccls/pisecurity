from flask import Flask, Response, render_template
import cv2
from picamera2 import Picamera2

app = Flask(__name__)

# Initialize the camera
picam2 = Picamera2()
picam2.framrate = 15
picam2.configure(picam2.create_video_configuration(raw={"size":(1640,1232)},main={"size": (640, 480), "format":"RGB888"}))

picam2.set_controls({"AwbMode": 1})
picam2.start()

def generate_frames():
    while True:
        frame = picam2.capture_array()
        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.png', frame)
        frame = buffer.tobytes()
        # Use the Multipart HTTP response to send the frame
        yield (b'--frame\r\n'
               b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    # Render the main HTML page

    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    # Return the video stream response
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, ssl_context = ('cert.pem', 'key.pem'))
