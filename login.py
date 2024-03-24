import streamlit as st
import os
import shutil
from image_pred import pred_image
from video_pred import process_video
from PIL import Image
from dotenv import load_dotenv
from twilio.rest import Client
from livecam import process_live_camera
from server import upload_image, display_database_with_images, upload_image_vid


load_dotenv()

# Function to authenticate user
def authenticate(username, password):
    # Hardcoded admin credentials 
    if username == "admin" and password == "admin123":
        return True
    else:
        return False

# Define session state variables
def init_session_state():
    return {
        'authenticated': False
    }

# Get or create the session state
session_state = st.session_state.get('session_state', init_session_state())

# Display login page if not authenticated
if not session_state['authenticated']:
    st.markdown(
        """
        <style>
        body {
            background-color: #1E1E1E;
            color: #FFFFFF;
            font-family: Arial, sans-serif;
        }
        .centered {
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        .custom-container {
            padding: 20px;
            border-radius: 10px;
            background-color: rgba(0, 0, 0, 0.6);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            width: 300px;
        }
        .login-button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .login-button:hover {
            background-color: #45a049;
        }
        .error-message {
            color: #FF5733;
            margin-top: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<h1 class="centered">ADMIN LOGIN</h1>', unsafe_allow_html=True)

    st.markdown("---")

    # Centering container
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        with st.container():
            st.markdown('<h2 class="centered" style="font-size: 18px;">Please Enter Your Login Credentials</h2>', unsafe_allow_html=True)
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.button("Login")
            
            if login_button:
                if authenticate(username, password):
                    session_state['authenticated'] = True
                    st.session_state['session_state'] = session_state
                    st.success("Login successful!")
                else:
                    st.error("Invalid Credentials")

# Add logout button at top right corner
if session_state['authenticated']:
    st.sidebar.empty()
    st.sidebar.markdown("""---""")
    st.sidebar.markdown(
        """
        <style>
        .logout-button {
            background-color: #DC143C;
            color: white;
            padding: 5px 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .logout-button:hover {
            background-color: #C71585;
        }
        </style>
        """
        , unsafe_allow_html=True)
    if st.sidebar.button("Logout", key='logout'):
        session_state['authenticated'] = False
        st.session_state['session_state'] = session_state

# Only display contents if authenticated
if session_state['authenticated']:

    st.sidebar.write("# **Configurations**")
    options = st.sidebar.selectbox("Choose your medium of inference", ["Home", "Live Camera", "Image", "Video", "Database"])

    # Twilio configuration
    account_sid = os.getenv("account_sid")
    auth_token = os.getenv("auth_token")
    twilio_phone_number = os.getenv("twilio_phone_number")
    destination_phone_number = os.getenv("destination_phone_number")

    client = Client(account_sid, auth_token)

    def del_fol(folder_path):
        # Remove all contents of the folder (files and subdirectories)
        shutil.rmtree(folder_path)
        # Recreate the empty folder
        os.makedirs(folder_path)

    def lf(main_folder_path):
        # Check if the provided path exists and is a directory
        if os.path.exists(main_folder_path) and os.path.isdir(main_folder_path):
            # List all directories inside the main folder
            subfolders = [f for f in os.listdir(main_folder_path) if os.path.isdir(os.path.join(main_folder_path, f))]
            
            # If there are subfolders, return the last one
            if subfolders:
                last_subfolder = sorted(subfolders)[-1]
                return os.path.join(main_folder_path, last_subfolder)
            else:
                return None  # No subfolders found
        else:
            return None
        

    def del_f(main_folder_path):
        # Check if the provided path exists and is a directory
        if os.path.exists(main_folder_path) and os.path.isdir(main_folder_path):
            # List all directories inside the main folder
            subfolders = [f for f in os.listdir(main_folder_path) if os.path.isdir(os.path.join(main_folder_path, f))]
            
            # Delete each subfolder
            for subfolder in subfolders:
                subfolder_path = os.path.join(main_folder_path, subfolder)
                shutil.rmtree(subfolder_path)
            
            return True  # Successfully deleted all subfolders
        else:
            return False  # Invalid path or not a directory
        
    def del_vi(main_folder_path):
        # Check if the provided path exists and is a directory
        if os.path.exists(main_folder_path) and os.path.isdir(main_folder_path):
            # List all files in the main folder
            files = [f for f in os.listdir(main_folder_path) if os.path.isfile(os.path.join(main_folder_path, f))]
            
            # Delete each video file
            for file in files:
                # Check if the file has a video extension (you can add more video extensions if needed)
                if file.endswith(('.mp4', '.avi', '.mov')):
                    file_path = os.path.join(main_folder_path, file)
                    os.remove(file_path)
            
            return True  # Successfully deleted all video files
        else:
            return False  # Provided path is not a valid directory


    def send_sms(message):
        try:
            client.messages.create(
                body=message,
                from_=twilio_phone_number,
                to=destination_phone_number
            )
            print("SMS sent successfully!")
        except Exception as e:
            print(f"Error sending SMS: {str(e)}")

    def process_model_predictions_img(predictions_folder):
        # Get the path to the labels folder
        labels_folder = os.path.join(predictions_folder, "labels")
        print(labels_folder)
        # Check if the labels folder exists
        if os.path.exists(labels_folder) and os.path.isdir(labels_folder):
            # List all files in the labels folder
            label_files = os.listdir(labels_folder)
            d = {
            0: "fire",  # Example mapping, update with your classes
            1: "smoke",
            2: "Accident",
            3: "Non Accident" # ... other class ID mappings
        }
            for entry in os.scandir(labels_folder):
                # Check if the entry is a file and ends with '.txt'
                if entry.is_file() and entry.name.endswith('.txt'):
                    # Read the content of the label file
                    with open(entry.path, 'r') as file:
                        # Read the first line and split it by space
                        first_term = float(file.readline().split()[0])
                        
                        # Check if the first term falls within the specified range
                        if first_term in [0, 1, 2,3]:
                            # Send an SMS notification
                            send_sms(f"🚨{d[first_term]} detected!!. Be cautious.")
                            return d[first_term]
        else:
            print("Labels folder not found.")

    def process_model_predictions_vid(predictions_folder):
        # Get the path to the labels folder
        labels_folder = r'video_labels'
        d = {
            0: "fire", 
            1: "smoke",
            2: "Accident",
            3: "Non Accident" 
        }
        for entry in os.scandir(labels_folder):
                # Check if the entry is a file and ends with '.txt'
                if entry.is_file() and entry.name.endswith('.txt'):
                    # Read the content of the label file
                    with open(entry.path, 'r') as file:
                        # Read the first line and split it by space
                        first_term = float(file.readline().split()[0])
                        upload_image(f'video_labels\{d[first_term]}.jpg',d[first_term],"Verified","College")
                        # Check if the first term falls within the specified range
                        if first_term in [0, 1, 2,3]:
                            # Send an SMS notification
                            print(f"-----------🚨{d[first_term]} detected!!. Be cautious.--------------")
                            send_sms(f"🚨{d[first_term]} detected!!. Be cautious.")
        # else:
        #     print("Labels folder not found.")
    def process_model_predictions_liv(predictions_folder):
        # Get the path to the labels folder
        labels_folder = r'live_cam_labels'
        d = {
            0: "fire",  # Example mapping, update with your classes
            1: "smoke",
            2: "Accident",
            3: "Non Accident" # ... other class ID mappings
        }
        for entry in os.scandir(labels_folder):
                # Check if the entry is a file and ends with '.txt'
                if entry.is_file() and entry.name.endswith('.txt'):
                    # Read the content of the label file
                    with open(entry.path, 'r') as file:
                        # Read the first line and split it by space
                        first_term = float(file.readline().split()[0])
                        
                        # Check if the first term falls within the specified range
                        if first_term in [0, 1, 2,3]:
                            # Send an SMS notification
                            print(f"-----------🚨{d[first_term]} detected!!. Be cautious.--------------")
                            send_sms(f"🚨{d[first_term]} detected!!. Be cautious.")

    if options:
        if options=='Home':
            # Header with Icon
            st.title("🚀 Envisioning the Future: Real-time Situational Awareness for Optimized Emergency Response")

            # Introduction with Icon
            st.write("""
            This project is  aimed at image and video analysis using state-of-the-art deep learning models. Dive in and explore the power of AI in analyzing images and videos.
            """)

            # Features with Icon
            st.header("✨ Features")
            st.markdown("""
            - **Image Analysis**: Upload an image and get predictions for objects detected within the image.
            - **Video Analysis**: Upload a video and get predictions for objects detected within each frame of the video.
            """)

            # Instructions with Icon
            st.header("📝 Instructions")
            st.markdown("""
            1. **Choose Your Medium**: Select 'Image' or 'Video' from the sidebar options.
            2. **Upload Your Files**: Upload your image or video file.
            3. **View Predictions**: Explore the predictions and enjoy the insights!
            """)

            # About with Icon
            st.header("🔍 About")
            st.write("""
            🤖 This project utilizes the YOLO (You Only Look Once) object detection algorithm for image and video analysis. YOLO is known for its efficiency and accuracy in object detection tasks.
            """)

            # Credits with Icon
            st.header("🙌 Credits")
            st.write("""
            - **Streamlit**: This application is built using Streamlit, a powerful framework for building web applications with Python.
            - **YOLO Model**: The object detection models used in this project are from the Ultralytics YOLO repository.
            """)

        elif options=='Live Camera':
            process_live_camera()

        elif options=='Image':
            st.write("# **Upload your image**")
            file = st.file_uploader("",type=["jpg", "jpeg", "png"])
            st.sidebar.header("🖼️ Image Analysis Instructions")
            st.sidebar.info("""
            1. **Upload Image**: Use the file uploader to upload an image file (JPEG, PNG, etc.).
            2. **View Predictions**: After uploading, the model will detect objects within the image.
            3. **Explore Results**: Explore the annotated image with predicted objects highlighted.
            """)
            if file is not None:
                # image = Image.open(file)
                im = Image.open(file)
                st.sidebar.image(im,caption="Original Image")

                # Save the uploaded image to a specific folder
                save_folder = "uploaded_images"
                os.makedirs(save_folder, exist_ok=True)  # Create the folder if it doesn't exist
                save_path = os.path.join(save_folder, file.name)
                im.save(save_path)
                del_f(r"runs\detect")
                pred_image(f"uploaded_images/{file.name}")\
                # send sms
                lab = process_model_predictions_img(r'runs\detect\predict')
                # Display the image
                upload_image(f'runs\detect\predict\{file.name}',lab,"Verified","College")
                st.image(f'runs\detect\predict\{file.name}', caption='Predicted Image', use_column_width=True)


        elif options=='Video':
            save_folder = "uploaded_images"
            st.sidebar.header("🎥 Video Analysis Instructions")
            st.sidebar.info("""
        1. **Upload Video**: Use the file uploader to upload a video file (MP4, AVI, etc.).
        2. **Wait for Processing**: The system will analyze each frame of the video for object detection.
        3. **Watch the Output**: Once processing is complete, watch the annotated video with detected objects.
        """)
            # file = st.file_uploader("Upload your video", type=["mp4", "avi", "mov"])
            st.write("# **Upload your video**")
            file = st.file_uploader("", type=["mp4", "avi", "mov"])

            if file is not None:
                video_bytes = file.read()
                # Get the filename
                filename = file.name
                file_path = os.path.join(save_folder, filename)
                # Save the video
                with open(file_path, "wb") as f:
                    f.write(video_bytes)

                # del_vi(r'/results')
                progress_bar = st.progress(0)

                del_fol('video_labels')
                vi_path,v_dic = process_video(f'uploaded_images/{file.name}',progress_bar)
                print("-------------",v_dic)
            
                # print(vi_path)
                process_model_predictions_vid(r'runs\detect\predict')
                st.video(r"results\output_video.mp4")
        elif options =='Database':
            display_database_with_images()
