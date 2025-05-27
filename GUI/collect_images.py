import cv2
import os

# Set your labels here
labels = ["ball", "toy", "book"]
save_path = "custom_dataset"
capture_count = 100  # Images per label

# Create folders if they don't exist
for label in labels:
    os.makedirs(os.path.join(save_path, label), exist_ok=True)

# Initialize webcam
cap = cv2.VideoCapture(0)
current_label = 0
count = 0

print("Press 'space' to capture image, 'n' to switch label, 'q' to quit.")
print(f"Current label: {labels[current_label]}")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Show current image count and label
    text = f"Label: {labels[current_label]} | Image: {count}/{capture_count}"
    cv2.putText(frame, text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Image Collector", frame)
    key = cv2.waitKey(1) & 0xFF

    # Capture image
    if key == ord(' '):
        filename = os.path.join(save_path, labels[current_label], f"{count}.jpg")
        cv2.imwrite(filename, frame)
        count += 1
        print(f"Saved {filename}")

    # Next label
    elif key == ord('n'):
        current_label = (current_label + 1) % len(labels)
        count = 0
        print(f"\nSwitched to label: {labels[current_label]}")

    # Quit
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
