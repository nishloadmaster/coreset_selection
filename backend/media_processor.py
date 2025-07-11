import zipfile
import uuid
import shutil
from pathlib import Path
import imageio
import os

class MediaProcessor:
    def __init__(self, zip_path, output_dir):
        self.zip_path = Path(zip_path)
        self.output_dir = Path(output_dir)
        self.temp_extract_dir = self.output_dir / "temp_extract"
        self.all_image_paths = []

    def unzip_folder(self):
        """Extract zip file to temporary directory"""
        self.temp_extract_dir.mkdir(parents=True, exist_ok=True)
        print(f"Extracting zip file to: {self.temp_extract_dir}")
        
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_extract_dir)
        
        print(f"Extraction complete. Found {len(list(self.temp_extract_dir.rglob('*')))} files")

    def is_image(self, file_path):
        """Check if file is an image"""
        return file_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif", ".webp"]

    def is_video(self, file_path):
        """Check if file is a video"""
        return file_path.suffix.lower() in [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv"]

    def extract_frames_from_video(self, video_path, video_name):
        """Extract frames from video and save as images"""
        print(f"Processing video: {video_path.name}")
        
        try:
            reader = imageio.get_reader(str(video_path))
            frame_paths = []
            
            # Extract frames at a reasonable rate (e.g., 1 frame per second)
            fps = reader.get_meta_data().get('fps', 30)
            frame_interval = max(1, int(fps))  # Extract 1 frame per second
            
            for frame_idx, frame in enumerate(reader):
                if frame_idx % frame_interval == 0:  # Extract every nth frame
                    frame_name = f"{video_name}_frame_{frame_idx:06d}.jpg"
                    frame_path = self.output_dir / frame_name
                    imageio.imwrite(frame_path, frame)
                    frame_paths.append(str(frame_path.resolve()))
                    
                    # Limit to reasonable number of frames (e.g., max 100 frames per video)
                    if len(frame_paths) >= 100:
                        break
            
            reader.close()
            print(f"Extracted {len(frame_paths)} frames from {video_path.name}")
            return frame_paths
            
        except Exception as e:
            print(f"Error processing video {video_path.name}: {e}")
            return []

    def copy_image_to_output(self, image_path, output_dir):
        """Copy image to output directory with unique name"""
        original_name = image_path.name
        counter = 1
        
        # Generate unique filename
        while (output_dir / original_name).exists():
            name_parts = original_name.rsplit('.', 1)
            if len(name_parts) > 1:
                original_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
            else:
                original_name = f"{original_name}_{counter}"
            counter += 1
        
        target_path = output_dir / original_name
        shutil.copy(image_path, target_path)
        return str(target_path.resolve())

    def process(self):
        """Main processing function"""
        print(f"Starting media processing for: {self.zip_path}")
        print(f"Output directory: {self.output_dir}")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract zip file
        self.unzip_folder()
        
        # Process all files
        processed_count = 0
        video_count = 0
        image_count = 0
        
        for file_path in self.temp_extract_dir.rglob("*"):
            if file_path.is_file():
                try:
                    if self.is_image(file_path):
                        # Copy image to output directory
                        target_path = self.copy_image_to_output(file_path, self.output_dir)
                        self.all_image_paths.append(target_path)
                        image_count += 1
                        print(f"Processed image: {file_path.name}")
                        
                    elif self.is_video(file_path):
                        # Extract frames from video
                        video_name = file_path.stem
                        frame_paths = self.extract_frames_from_video(file_path, video_name)
                        self.all_image_paths.extend(frame_paths)
                        video_count += 1
                        processed_count += len(frame_paths)
                        
                except Exception as e:
                    print(f"Error processing file {file_path.name}: {e}")
                    continue
        
        # Clean up temporary extraction directory
        if self.temp_extract_dir.exists():
            shutil.rmtree(self.temp_extract_dir)
        
        print(f"Processing complete!")
        print(f"Images processed: {image_count}")
        print(f"Videos processed: {video_count}")
        print(f"Total frames extracted: {processed_count}")
        print(f"Total files in output: {len(self.all_image_paths)}")
        
        return self.all_image_paths
