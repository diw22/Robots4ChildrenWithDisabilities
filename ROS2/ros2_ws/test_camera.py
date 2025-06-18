import depthai as dai
import cv2

# Create pipeline
pipeline = dai.Pipeline()

# Define a color camera node
cam = pipeline.createColorCamera()
cam.setPreviewSize(640, 480)
cam.setInterleaved(False)

# Create an XLink output node to send the preview stream to host
xout = pipeline.createXLinkOut()
xout.setStreamName("preview")
cam.preview.link(xout.input)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:
    q = device.getOutputQueue(name="preview", maxSize=4, blocking=False)
    
    while True:
        inPreview = q.get()  # Blocking call, waits for data
        frame = inPreview.getCvFrame()
        
        cv2.imshow("OAK-D Color Preview", frame)
        
        if cv2.waitKey(1) == ord('q'):
            break

cv2.destroyAllWindows()
