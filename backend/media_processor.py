import zipfile
import uuid
import shutil
from pathlib import Path
import imageio

class MediaProcessor:
    def __init__(self, zip_path, output_dir):
        self.zip_path = Path(zip_path)
        self.output_dir = Path(output_dir)
        self.temp_extract_dir = self.output_dir / "unzipped"
        self.frames_dir = self.output_dir / "frames"
        self.all_image_paths = []

    def unzip_folder(self):
        self.temp_extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_extract_dir)

    def is_image(self, file_path):
        return file_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"]

    def is_video(self, file_path):
        return file_path.suffix.lower() in [".mp4", ".avi", ".mov", ".mkv", ".webm"]

    def extract_frames_from_video(self, video_path, uid):
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        reader = imageio.get_reader(str(video_path))
        frame_paths = []
        for frame_idx, frame in enumerate(reader):
            frame_name = f"{uid}_frame{frame_idx + 1}.jpg"
            frame_path = self.frames_dir / frame_name
            imageio.imwrite(frame_path, frame)
            frame_paths.append(str(frame_path.resolve()))
        reader.close()
        return frame_paths

    def process(self):
        self.unzip_folder()
        for file in self.temp_extract_dir.rglob("*"):
            if file.is_file():
                if self.is_image(file):
                    target_path = self.output_dir / file.name
                    counter = 1
                    while target_path.exists():
                        target_path = self.output_dir / f"{target_path.stem}_{counter}{target_path.suffix}"
                        counter += 1
                    shutil.copy(file, target_path)
                    self.all_image_paths.append(str(target_path.resolve()))
                elif self.is_video(file):
                    uid = str(uuid.uuid4())
                    frames = self.extract_frames_from_video(file, uid)
                    self.all_image_paths.extend(frames)
        return self.all_image_paths
