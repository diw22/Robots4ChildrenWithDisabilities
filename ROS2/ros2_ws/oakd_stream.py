from flask import Flask, Response
import depthai as dai
import cv2

# Set up pipeline
pipeline = dai.Pipeline()
cam = pipeline.create(dai.node.ColorCamera)
cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_720_P)
cam.setBoardSocket(dai.CameraBoardSocket.CAM_A)
cam.setInterleaved(False)

xout = pipeline.create(dai.node.XLinkOut)
xout.setStreamName("video")
cam.video.link(xout.input)

# Flask app
app = Flask(__name__)
def generate_frames():
    try:
        with dai.Device(pipeline) as device:
            print("Device opened successfully")
            video = device.getOutputQueue(name="video", maxSize=4, blocking=False)

            while True:
                frame = video.get().getCvFrame()
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    except Exception as e:
        print("Error in generate_frames:", e)
        # Optionally, stop the generator
        return

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '<h1>Oak-D Camera Feed</h1><img src="/video_feed">'


if __name__ == "__main__":
    print("Starting Flask server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
