import base64
from ultralytics import YOLO
import cv2
import logging
import streamlit as st
from PIL import Image
import os


def process_video(path,progress_bar):
    # Define the video paths
    video_path = f"{path}"  # Replace with your video path
    output_video_path = "results/output_video.mp4"  # Define the output video path with .mp4 extension

    # Load the model
    model = YOLO(r"Model\best.pt")  # Load your trained YOLO model

    # Define the dictionary mapping class IDs to labels
    d = {
        0: "fire",  # Example mapping, update with your classes
        1: "smoke",
        2: "Accident",
        3: "Non Accident" # ... other class ID mappings
    }

    d1={
        0:0,
        1:0,
        2:0,
        3:0
    }

    # Open the video capture
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error opening video:", path)
        exit(1)

    # Initialize dictionary to store frames for each class
    frames_per_class = {}

    # Get the video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Define the video writer with H.264 codec
    fourcc = cv2.VideoWriter_fourcc(*'h264')  # H.264 codec
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    # Process each frame of the video
    for frame_num in range(total_frames):
        # Capture a frame
        ret, frame = cap.read()

        # Break if frame is not captured
        if not ret:
            break
        
        # Perform prediction on the frame
        results = model(frame)[0]

        # Draw bounding boxes and labels for each detection
        for box in results:
            # Get individual coordinates
            x1, y1, x2, y2 = box.boxes.xyxy[0].cpu().numpy()

            # Get class label and confidence score
            class_id = box.boxes.cls[0].cpu().numpy().item()
            label = d[class_id]  # Map ID to label

            # If frame for class not yet captured, save it
            if label not in frames_per_class:
                # # Convert OpenCV frame to PIL image
                # image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # pil_image = Image.fromarray(image)
                # frames_per_class[label] = pil_image
                # Check if the frame for this class has already been saved
                if not os.path.exists(f"video_labels/{label}.jpg"):
                    # Save the frame as a JPEG image
                    frame_path = f"video_labels/{label}.jpg"
                    cv2.imwrite(frame_path, frame)



            conf = box.boxes.conf[0].cpu().numpy().item()
            d1[class_id] = conf
            # Draw bounding box
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

            # Add label with optional confidence score
            text = f"{label}: {conf:.2f}"  # Format confidence score

            # Calculate label placement (adjust as needed)
            offset = 5  # Adjust offset based on text size and box size
            text_width, text_height = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
            x_text = int(x1 + offset)
            y_text = int(y1 + offset + text_height)

            cv2.putText(frame, text, (x_text, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Write the frame with detections to the output video
        out.write(frame)

        # Update progress bar
        progress = (frame_num + 1) / total_frames
        progress_bar.progress(progress)

        # print(class_id, label, conf)
    with open(r"video_labels\video_labels.txt", "w") as f:
        f.write(f"{max(d1, key=d1.get)}")
    print()
    print("------------",max(d1, key=d1.get))
    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    return output_video_path,frames_per_class