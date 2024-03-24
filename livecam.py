import logging
import tempfile
import streamlit as st
import cv2
import os
import time
from ultralytics import YOLO
from moviepy.editor import ImageSequenceClip


count = 1
detection_start_time = None
def process_live_camera():
    continuous_detection_threshold = 2  
    if "cap" not in st.session_state:
        st.session_state.cap = None

    print(st.session_state)
    # Initialize frames in session state
    if "frames" not in st.session_state:
        st.session_state.frames = []
        
    def video_to_bytes(video_path):
        with open(video_path, 'rb') as video_file:
            video_bytes = video_file.read()
        return video_bytes

    def perform_detection(frame):
        global detection_start_time, count
        # Perform prediction on the frame
        results = model(frame)[0]
        max_conf=-1
        max_class_label =""

        # Draw bounding boxes and labels for each detection
        for box in results:
            # Get individual coordinates
            x1, y1, x2, y2 = box.boxes.xyxy[0].cpu().numpy()

            # Get class label and confidence score
            class_id = box.boxes.cls[0].cpu().numpy().item()
            label = d[class_id]  # Map ID to label
            conf = box.boxes.conf[0].cpu().numpy().item()
            color = colors[class_id]
            if conf>max_conf:
                max_conf=conf
                max_class_label=class_id
            # Draw bounding box
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

            # Add label with optional confidence score
            text = f"{label}: {conf:.2f}"  # Format confidence score

            # Calculate label placement (adjust as needed)
            offset = 5  # Adjust offset based on text size and box size
            text_width, text_height = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
            x_text = int(x1 + offset)
            y_text = int(y1 + offset + text_height)

            cv2.putText(frame, text, (x_text, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            if conf > 0.3:
                if detection_start_time is None:
                    detection_start_time = time.time()
                else:
                    elapsed_time = time.time() - detection_start_time
                    if elapsed_time >= continuous_detection_threshold:
                        # print(f"Continuous detection for {continuous_detection_threshold} seconds!")
                        detection_start_time = None

                        # Save the captured frame
                        image_filename = os.path.join(output_folder, f"img_{count}.jpg")
                        cv2.imwrite(image_filename, frame)
                        count += 1

        return max_class_label

                        

    st.title("Live Cam")
    cap = None
    temp_dir = tempfile.TemporaryDirectory()
    try:
        # Use an RTSP Links for Live Camera streams

        cap = cv2.VideoCapture(0) 
    except:
        st.error("Invalid option selected.")
        st.stop()

    if cap and not cap.isOpened():
        st.error("Error opening video/camera.")
        st.stop()

    if cap and cap.isOpened():
        image_container = st.empty()
        stop_button = st.button("Stop")

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        timestamp = time.strftime("%Y%m%d%H%M%S")

        # Load the YOLO model
        model = YOLO(r"Model\best.pt")

        d = {
                0: "fire",  # Example mapping, update with your classes
                1: "smoke",
                2: "Accident",
                3: "Non Accident" # ... other class ID mappings
            }

        colors = {
            0: (134, 34, 255),
            1: (254, 0, 86),
            2: (0, 255, 206),
            3: (255, 128, 0),
        }

        output_folder = "CapturedFrames"
        continuous_detection_threshold = 2  # 5 seconds of continuous detection
        os.makedirs(output_folder, exist_ok=True)

        # Process each frame of the video
        while True:
            # Capture a frame
            ret, frame = cap.read()

            # Break if frame is not captured
            if not ret:
                break

            # Perform YOLO detection on the frame (Placeholder for your YOLO detection function)
            label = perform_detection(frame)
            with open('live_cam_labels\live_cam.txt','w') as f:
                f.write(f"{label}")

            # Resize the frame to fit within the screen while maintaining the aspect ratio
            max_width = 800  # Adjust this value based on your layout
            aspect_ratio = frame_width / frame_height
            new_width = min(frame_width, max_width)
            new_height = int(new_width / aspect_ratio)
            resized_frame = cv2.resize(frame, (new_width, new_height))

            # Convert BGR to RGB before appending to the list
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

            # Append the RGB frame to the list
            st.session_state.frames.append(rgb_frame)

            # Display the frame with detections
            image_container.image(rgb_frame, channels="RGB", use_column_width=True)

            # Exit on button click
            if stop_button:
                break

        # Release resources
        cap.release()

        # Create an ImageSequenceClip from the frames list
        video_clip = ImageSequenceClip(st.session_state.frames, fps=fps)

        # Write the ImageSequenceClip to the output video file
        output_video_path = os.path.join(temp_dir.name, f"output_video_{timestamp}.mp4")
        video_clip.write_videofile(output_video_path, codec="libx264", audio=False)

        # Display download link for the output video
        st.success("Video processing completed!")
