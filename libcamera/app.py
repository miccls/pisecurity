from flask import Flask, Response
import subprocess

app = Flask(__name__)

def generate_camera_stream():
    # Run libcamera-vid to capture MJPEG stream
    cmd = ['libcamera-vid', '--inline', '--codec', 'mjpeg', '-o', '-', '--width', '1280', '--height', '720', '--framerate', '30']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)

    try:
        while True:
            frame = b''
            while True:
                data = process.stdout.read(1024)
                if not data:
                    break
                frame += data
                # End of JPEG frame is signaled by the EOI (End of Image) marker: 0xFFD9
                if b'\xff\xd9' in frame:
                    break

            # Yield a complete MJPEG frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except GeneratorExit:
        process.terminate()

@app.route('/video_feed')
def video_feed():
    # Return a multipart response with the video stream
    return Response(generate_camera_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    # A basic HTML page to display the video stream
    return '''
    <html>
    <head>
        <title>Raspberry Pi Camera Stream</title>
    </head>
    <body>
        <h1>Raspberry Pi Camera Stream</h1>
        <img src="/video_feed" width="100%">
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
