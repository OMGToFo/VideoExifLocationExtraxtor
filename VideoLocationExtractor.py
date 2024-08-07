import streamlit as st
import subprocess
import json
import folium
from streamlit_folium import st_folium
import tempfile
import exiftool

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
        # Extract GPS coordinates using the correct keys
        gps_latitude = exif_data.get('Composite:GPSLatitude')
        gps_longitude = exif_data.get('Composite:GPSLongitude')

        if gps_latitude is not None and gps_longitude is not None:
            # GPS data is already in decimal format, no need to parse DMS
            lat = float(gps_latitude)
            lon = float(gps_longitude)
            return lat, lon
        else:
            return None
    except KeyError:
        return None



#update for github
def get_exif_data(file_path):
    try:
        with exiftool.ExifTool() as et:
            metadata = et.execute_json(file_path)
            return metadata[0] if metadata else {}
    except Exception as e:
        st.error(f"Error extracting EXIF data: {e}")
        return None
    
    
    
    

def main():
    st.title("Video Location Extractor from EXIF Data")
    
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])
    
    if uploaded_file is not None:
        st.video(uploaded_file)

        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name

        # Extract EXIF data using the subprocess call to exiftool
        exif_data = get_exif_data(tmp_file_path)
        
        if exif_data:
            st.write(exif_data)  # Debugging: display all EXIF data
            
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

if __name__ == "__main__":
    main()
