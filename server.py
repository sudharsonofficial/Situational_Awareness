import os
import base64
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gridfs
import time
from dotenv import load_dotenv
from pymongo import MongoClient
from PIL import Image
from io import BytesIO 
from pymongo.mongo_client import MongoClient

load_dotenv()
uri = os.getenv("URI")

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


db = client['Reports'] 
fs = gridfs.GridFS(db)

# Function to upload image
def upload_image(image_path, user_insights, admin_verification_status,location):
    # Open image file
    with open(image_path, "rb") as f:
        # Read image binary data
        image_binary = f.read()
        
    # Get current timestamp
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    # Upload image binary data to MongoDB GridFS
    image_id = fs.put(image_binary, filename=image_path)

    # Get the current count of documents in the collection
    current_count = db['image_metadata'].count_documents({})

    # Insert metadata into a separate collection
    metadata_collection = db['image_metadata']
    metadata_collection.insert_one({
        "S_No": current_count + 1,
        "issue": user_insights,
        "admin_verification_status": admin_verification_status,
        "timestamp": timestamp,
        "user":"Admin",
        "image_filename": image_path,  # Store image filename for reference
        "image_id": image_id,
        "location":location # Store image ID for retrieval
    })
    print("Image uploaded successfully!")

# Function to display entire database including images
def display_database_with_images():
    try:
        # Retrieve metadata from the metadata collection
        metadata_collection = db['image_metadata']
        metadata_cursor = metadata_collection.find()

        # Initialize list to store data for DataFrame
        data = []

        # Iterate over metadata documents
        for metadata in metadata_cursor:
            # Retrieve image binary data from GridFS
            image_data = fs.get(metadata["image_id"]).read()

            # Open image from binary data
            image = Image.open(BytesIO(image_data))
            # Convert image binary data to base64 encoded string
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Append metadata and image to data list
            data.append({
                "S.No": metadata["S_No"],
                "Issue": metadata["issue"],
                "Location": metadata.get("location", "Location not available"),
                "Admin Verification Status": metadata["admin_verification_status"],
                "Timestamp": metadata["timestamp"],
                "User":metadata["user"],
                # "Image": image  # Add image object to the DataFrame
                "Image": f"data:image/jpeg;base64,{image_base64}"
            })

        # # Create DataFrame from data
        df = pd.DataFrame(data)
        df_display = df.set_index('S.No')
        # Display DataFrame with buttons
        st.write(df_display)
        
        sno_input = st.number_input("Enter S.No:", min_value=1, value=1, step=1)
        try:
        # Retrieve metadata from the metadata collection based on S.No
            metadata = metadata_collection.find_one({"S_No": sno_input})

            if metadata:
                # Retrieve image binary data from GridFS
                image_data = fs.get(metadata["image_id"]).read()

                # Convert image binary data to base64 encoded string
                image_base64 = base64.b64encode(image_data).decode('utf-8')

                # Display the image
                st.image(f"data:image/jpeg;base64,{image_base64}", caption=f"User Insights: {metadata['issue']}", width=500)
            else:
                st.error("Image not found for the entered S.No.")

        except Exception as e:
                st.error("Error displaying image: {}".format(e))
        
        return df

    except Exception as e:
        print("Error displaying database with images:", e)


# Function to upload image
def upload_image_vid(image_bin, user_insights, admin_verification_status):
        
    # Get current timestamp
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    # Upload image binary data to MongoDB GridFS
    image_id = fs.put(image_bin)

    # Get the current count of documents in the collection
    current_count = db['image_metadata'].count_documents({})

    # Insert metadata into a separate collection
    metadata_collection = db['image_metadata']
    metadata_collection.insert_one({
        "S_No": current_count + 1,
        "issue": user_insights,
        "admin_verification_status": admin_verification_status,
        "timestamp": timestamp,
        "user":"Admin",
        "image_filename": f"{current_count + 1} image",  # Store image filename for reference
        "image_id": image_id ,
         "image_base64": image_bin,
         "location":"Need to be updated"# Store image ID for retrieval
    })
    print("Image uploaded successfully!")


