# 🚀 Envisioning the Future: Real-time Situational Awareness for Optimized Emergency Response System

## 🔍 Description

This project aims to provide real-time image and video analysis using state-of-the-art deep learning model. It enables users to analyze images and videos to detect various objects, such as fire, smoke, accidents, etc., using the YOLO (You Only Look Once) object detection algorithm.

## ✨ Features

✨ **Image Analysis**: Upload an image and get predictions for objects detected within the image.

✨ **Video Analysis**: Upload a video and get predictions for objects detected within each frame of the video.

## Installation

1. Clone this repository:

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 📝 Usage

1. **Provide the environment variables:** Provide your MongoDB Cluster URI and the necessary Twilio credentials in the .env file.
For more information visit [MongoDB Atlas](https://www.mongodb.com/atlas/database)

2. **Run the `login.py` script**:
   ```bash
   streamlit run login.py
   ```

3. **Authenticate using the provided username and password from login.py file.** .

4. **Choose your medium of inference** (e.g., Image, Video, LiveCam) from the sidebar options.

5. **Upload Your Files (Image and Video):** Upload your image or video file.

6. **View Predictions:** Explore the predictions from the database and enjoy the insights!
