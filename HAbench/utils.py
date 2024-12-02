import os
import json
import cv2
import time
import base64
import numpy as np
from concurrent.futures import ThreadPoolExecutor

class Video_Dataset:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.json_path = os.path.join(data_dir, 'human_anno/color.json')
        self.annotations = self.load_annotations()

    def load_annotations(self):
        with open(self.json_path, 'r') as f:
            return json.load(f)

    def process_video(self, datadir, videos_path, extract_frames_persecond=2, resize_fx=1, resize_fy=1):
        base64Frames = {
            "cogvideox5b": [],
            "kling": [],
            "gen3": [],
            "lavie": [],
            "pika": [],
            "show1": [],
            "videocrafter2": []
        }
        
        for key in base64Frames.keys():
            video = cv2.VideoCapture(os.path.join(datadir, videos_path[key]))

            if not video.isOpened():
                print(f"Error: Cannot open video file {datadir + videos_path[key]}")
                continue

            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = video.get(cv2.CAP_PROP_FPS)
            frames_to_skip = int(fps / extract_frames_persecond)

            curr_frame = 1
            end_frame = total_frames - 1
            
            # Loop through the video and extract frames at specified sampling rate
            while curr_frame < total_frames - 1:
                video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
                success, frame = video.read()
                if not success:
                    break

                frame = cv2.resize(frame, None, fx=resize_fx, fy=resize_fx)
                _, buffer = cv2.imencode(".jpg", frame)
                base64Frames[key].append(base64.b64encode(buffer).decode("utf-8"))
                curr_frame += frames_to_skip

            # Get the last frame
            video.set(cv2.CAP_PROP_POS_FRAMES, end_frame)
            success, frame = video.read()
            if success:
                frame = cv2.resize(frame, None, fx=resize_fx, fy=resize_fx)
                _, buffer = cv2.imencode(".jpg", frame)
                base64Frames[key].append(base64.b64encode(buffer).decode("utf-8"))

            video.release()

        return base64Frames
    
    def process_video2gridview(datadir, videos_path, extract_frames_persecond=8):
        base64Frames = {"cogvideox5b": [], "kling": [], "gen3": [], "lavie": [], "pika": [], "show1": [], "videocrafter2": []}

        def process_video(key):
            frames = []
            video = cv2.VideoCapture(os.path.join(datadir, videos_path[key]))

            if not video.isOpened():
                print(f"Error: Cannot open video file {datadir+videos_path[key]}")
                return

            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = video.get(cv2.CAP_PROP_FPS)
            frames_to_skip = int(fps / extract_frames_persecond)
            curr_frame = 0

            while curr_frame < total_frames:
                video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
                curr_frame += frames_to_skip
                success, frame = video.read()
                if not success:
                    break
                frames.append(frame)
                if len(frames) == extract_frames_persecond:
                    height, width, _ = frames[0].shape
                    grid_image = np.zeros((height, extract_frames_persecond * width, 3))

                    for j in range(extract_frames_persecond):
                        grid_image[0:height, j * width:(j + 1) * width] = frames[j]

                    _, buffer = cv2.imencode(".jpg", grid_image)
                    base64Frames[key].append(base64.b64encode(buffer).decode("utf-8"))
                    frames = []

            video.release()

        with ThreadPoolExecutor() as executor:
            executor.map(process_video, base64Frames.keys())

        return base64Frames


    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, idx):
        annotation = self.annotations[idx]
        frames = self.process_video(self.data_dir, annotation['videos'], 2)
        grid_frames = self.process_video2gridview(self.data_dir, annotation['videos'], 8)
        
        return {
            'frames': frames,
            'grid_frames': grid_frames,
            'prompt': annotation['prompt_en']
        }

def save_json(data, path, indent=4):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)

def load_json(path):
    """
    Load a JSON file from the given file path.
    
    Parameters:
    - file_path (str): The path to the JSON file.
    
    Returns:
    - data (dict or list): The data loaded from the JSON file, which could be a dictionary or a list.
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
