import streamlit as st
import subprocess
import json
import folium
from streamlit_folium import st_folium
import tempfile

def parse_dms(dms_str):
    """
    Convert a string in the format '53 deg 52' 2.64" N' to decimal degrees.
    """
    parts = dms_str.split(' ')
    degrees = float(parts[0])
    minutes = float(parts[2].strip("'"))
    seconds = float(parts[3].strip('"'))
    direction = parts[4]
    
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if direction in ['S', 'W']:
        decimal = -decimal
    
    return decimal

def extract_gps_coordinates(exif_data):
    try:
        # Extract and parse the GPS coordinates
        gps_latitude = exif_data.get('GPSLatitude')
        gps_longitude = exif_data.get('GPSLongitude')

        if gps_latitude and gps_longitude:
            lat = parse_dms(gps_latitude)
            lon = parse_dms(gps_longitude)
            return lat, lon
        else:
            return None
    except KeyError:
        return None

def get_exif_data(file_path):
    try:
        result = subprocess.run(
            ['exiftool', '-json', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        exif_data = json.loads(result.stdout)[0]
        return exif_data
    except Exception as e:
        st.error(f"Error extracting EXIF data: {e}")
        return None



# Function to check if the file is an image
def is_image(file_name):
    image_extensions = ['jpg', 'jpeg', 'png', 'heic']
    return any(file_name.lower().endswith(ext) for ext in image_extensions)

# Function to check if the file is a video
def is_video(file_name):
    video_extensions = ['mp4', 'mov', 'avi', 'mkv']
    return any(file_name.lower().endswith(ext) for ext in video_extensions)

# Assuming get_exif_data returns a dictionary-like structure
def get_create_date(exif_data):
    # Check if the CreateDate key exists in the exif_data
    if "CreateDate" in exif_data:
        return exif_data["CreateDate"]
    else:
        return None



st.title("Video Location Extractor")
st.info("The video loacation and other info is, if possible, extracted from detected exif-data")

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file is not None:
    file_name = uploaded_file.name

    # Check if the file is an image or a video
    if is_image(file_name):
        st.write(f"Uploaded file '{file_name}' is detected as a photo.")
    elif is_video(file_name):
        st.write(f"Uploaded file '{file_name}' is detected as a video.")


    st.video(uploaded_file)

    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    # Extract EXIF data using the subprocess call to exiftool
    exif_data = get_exif_data(tmp_file_path)

    if exif_data:
        with st.expander("Show all exif data >>>>"):
            st.write(exif_data)  # Debugging: display all EXIF data

        # Extract the CreateDate from the EXIF data
        create_date = get_create_date(exif_data)

        if create_date:
            st.write(f"Create Date: {create_date}")
        else:
            st.write("Create Date not found.")





        gps_coordinates = extract_gps_coordinates(exif_data)

        if gps_coordinates:
            st.write(f"Latitude: {gps_coordinates[0]}, Longitude: {gps_coordinates[1]}")

            # Display the location on a map
            map_ = folium.Map(location=gps_coordinates, zoom_start=15)
            folium.Marker(gps_coordinates).add_to(map_)
            st_folium(map_, width=700, height=500)
        else:
            st.error("No GPS data found in the video.")
    else:
        st.error("Could not extract metadata from the video.")


