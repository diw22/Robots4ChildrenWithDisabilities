import depthai as dai
import cv2

# Create pipeline
pipeline = dai.Pipeline()

# Define color camera node
cam = pipeline.createColorCamera()
cam.setPreviewSize(640, 480)
cam.setInterleaved(False)

# Create XLink output to get frames on host
xout = pipeline.createXLinkOut()
xout.setStreamName("color")
cam.preview.link(xout.input)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:
    q = device.getOutputQueue(name="color", maxSize=4, blocking=False)
    
    for i in range(10):  # Capture 10 frames
        in_frame = q.get()
        frame = in_frame.getCvFrame()
        filename = f"frame_{i}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Saved {filename}")

print("Done capturing frames.")
