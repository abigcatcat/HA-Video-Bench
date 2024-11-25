import os
import json
import cv2
import time
import base64
from torch.utils.data import Dataset

class Video_Dataset(Dataset):
    def load_annotations(self):
        with open(self.json_path, 'r') as f:
            data = json.load(f)
        return data

    def process_video(self,datadir, videos_path, extract_frames_persecond=2, resize_fx=1, resize_fy=1):
        base64Frames = {"cogvideox5b": [],"kling": [],"gen3": [],"lavie": [],"pika": [],"show1":[],"videocrafter2":[]}
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

            video.set(cv2.CAP_PROP_POS_FRAMES, end_frame)
            success, frame = video.read()
            if not success:
                break

            frame = cv2.resize(frame, None, fx=resize_fx, fy=resize_fx)

            _, buffer = cv2.imencode(".jpg", frame)
            base64Frames[key].append(base64.b64encode(buffer).decode("utf-8"))

            video.release()

        return base64Frames

    def __init__(self, data_dir,):
        self.data_dir = data_dir
        self.json_path = os.path.join(data_dir, 'human_anno\\color.json')
        self.annotations = self.load_annotations()

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, idx):

        annotation = self.annotations[idx]
        #video_path = os.path.join(self.videos_dir, annotation['videos'])
        frames = self.process_video(self.data_dir, annotation['videos'],2, resize_fx=1, resize_fy=1)

        return {
            'frames': frames,
            'prompt': annotation['prompt_en']
        }
