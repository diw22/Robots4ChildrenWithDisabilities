import depthai as dai
import cv2

pipeline = dai.Pipeline()
cam = pipeline.createColorCamera()
cam.setPreviewSize(640, 480)
cam.setInterleaved(False)
cam.setBoardSocket(dai.CameraBoardSocket.RGB)

xout = pipeline.createXLinkOut()
xout.setStreamName('video')
cam.preview.link(xout.input)

with dai.Device(pipeline) as device:
    q = device.getOutputQueue(name='video', maxSize=4, blocking=False)
    while True:
        in_frame = q.get()
        frame = in_frame.getCvFrame()
        cv2.imshow('OAK-D Feed', frame)
        if cv2.waitKey(1) == ord('q'):
            break
cv2.destroyAllWindows()
