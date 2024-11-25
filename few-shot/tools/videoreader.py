import cv2
import os
import time
import base64
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from IPython.display import display
from PIL import Image
from concurrent.futures import ThreadPoolExecutor


def process_video(datadir,videos_path, extract_frames_persecond=2,resize_fx=1,resize_fy=1):
    base64Frames = {"cogvideox5b": [],"kling": [],"gen3": [],"lavie": [],"pika": [],"show1":[],"videocrafter2":[]}
    for key in base64Frames.keys():
        video = cv2.VideoCapture(os.path.join(datadir,videos_path[key]))
        if not video.isOpened():
            print(f"Error: Cannot open video file {datadir+videos_path[key]}")
            continue

        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        frames_to_skip = int(fps/extract_frames_persecond)
    
        curr_frame=1
        end_frame = total_frames - 1
        # Loop through the video and extract frames at specified sampling rate
        while curr_frame < total_frames - 1:
            video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
            success, frame = video.read()
            if not success:
                break

            frame = cv2.resize(frame, None, fx=resize_fx, fy=resize_fy)

            _, buffer = cv2.imencode(".jpg", frame)
            base64Frames[key].append(base64.b64encode(buffer).decode("utf-8"))
            curr_frame += frames_to_skip

        video.set(cv2.CAP_PROP_POS_FRAMES, end_frame)
        success, frame = video.read()
        if not success:
            break

        frame = cv2.resize(frame, None, fx=resize_fx, fy=resize_fy)

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



def display_base64_images(base64Frames):
    for idx, base64_image in enumerate(base64Frames):
        img_data = base64.b64decode(base64_image)
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        pil_img = Image.fromarray(img_rgb)

        display(pil_img)