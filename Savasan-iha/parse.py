import cv2
import os

def extract_frames(video_path, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Capture the video from the file
    cap = cv2.VideoCapture(video_path)
    
    # Initialize a counter for the frames
    frame_count = 0
    
    # Loop through each frame of the video
    while cap.isOpened():
        # Read the next frame
        ret, frame = cap.read()
        
        if not ret:
            break  # Exit if there are no more frames
        
        # Save the frame as an image file
        frame_filename = os.path.join(output_folder, f"frame_{frame_count:04d}.jpg")
        cv2.imwrite(frame_filename, frame)
        
        # Increment the frame counter
        frame_count += 1

    # Release the video capture object
    cap.release()

    print(f"Extracted {frame_count} frames from the video.")

video_path = 'C:\\Users\\asus\\OneDrive - Pamukkale University\\Masaüstü\\AlganYazilim-1-YEDEK-HAZIR-CALISIYOR\\video.mp4'    # Path to the MP4 video file
output_folder = 'frames_folder'  # Directory to store extracted frames
extract_frames(video_path, output_folder)
