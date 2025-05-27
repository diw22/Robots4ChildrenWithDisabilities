import torch
import torch.nn as nn
import torchvision.transforms as transforms
import cv2
from PIL import Image
import pyttsx3
import os

# ----------------------------
# STEP 1: Load Model and Labels
# ----------------------------

class RobotNN(nn.Module):
    def __init__(self):
        super(RobotNN, self).__init__()
        self.fc1 = nn.Linear(64*64*3, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 3)

    def forward(self, x):
        x = x.view(-1, 64*64*3)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

# Check model exists
if not os.path.exists("simple_mnist_model.pt"):
    print("❌ Error: 'simple_mnist_model.pt' not found. Please train your model and save it first.")
    exit()

# Load trained model
model = RobotNN()
model.load_state_dict(torch.load("simple_mnist_model.pt", map_location=torch.device("cpu")))
model.eval()

# Class labels
labels = ['ball', 'toy', 'book']

# Text-to-speech
engine = pyttsx3.init()

# ----------------------------
# STEP 2: Define Preprocessing
# ----------------------------

transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])  # for RGB
])

# ----------------------------
# STEP 3: Start Webcam
# ----------------------------

cap = cv2.VideoCapture(0)
print("✅ Press SPACE to predict, Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Couldn't access camera.")
        break

    frame_resized = cv2.resize(frame, (640, 480))
    cv2.imshow("Robot Camera", frame_resized)

    key = cv2.waitKey(1) & 0xFF

    # SPACE to predict
    if key == ord(' '):
        # Convert frame to PIL Image and preprocess
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image)
        input_tensor = transform(pil_image).unsqueeze(0)

        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.softmax(output, dim=1)[0]
            predicted = torch.argmax(probabilities).item()
            prediction = labels[predicted]
            confidence = probabilities[predicted].item() * 100
        
        # Print and speak result
        print(f"[Robot]: I see a {prediction} ({confidence:.1f}%)")
        engine.say(f"I see a {prediction}")
        engine.runAndWait()

        # Draw on frame
        cv2.putText(frame_resized, f"I see a {prediction} ({confidence:.1f}%)",
                    (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        cv2.imshow("Robot Camera", frame_resized)
        cv2.waitKey(1500)

    # Q to quit
    elif key == ord('q'):
        print("🛑 Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
