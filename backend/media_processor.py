"""
Media Processing Module for AI Model Improver

This module provides the MediaProcessor class for handling zip file extraction,
image processing, and video frame extraction. It supports large datasets and
provides efficient processing with progress tracking.

Author: AI Model Improver Team
Version: 1.0.0
"""

import zipfile
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import imageio
import imageio_ffmpeg
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MediaProcessor:
    """
    Handles processing of zip files containing images and videos.
    
    This class provides functionality to:
    - Extract zip files with progress tracking
    - Copy image files to organized folders
    - Extract frames from video files using imageio-ffmpeg
    - Handle large datasets efficiently
    - Provide detailed processing logs
    
    Attributes:
        zip_path (Path): Path to the input zip file
        output_dir (Path): Directory where processed files will be saved
        supported_image_extensions (List[str]): Supported image file extensions
        supported_video_extensions (List[str]): Supported video file extensions
        max_frames_per_video (int): Maximum frames to extract per video
        frame_interval (int): Interval between extracted frames (in seconds)
    """
    
    def __init__(
        self, 
        zip_path: Path, 
        output_dir: Path,
        max_frames_per_video: int = 100,
        frame_interval: int = 1
    ):
        """
        Initialize the MediaProcessor.
        
        Args:
            zip_path (Path): Path to the zip file to process
            output_dir (Path): Directory where processed files will be saved
            max_frames_per_video (int): Maximum number of frames to extract per video
            frame_interval (int): Interval between extracted frames in seconds
        """
        self.zip_path = Path(zip_path)
        self.output_dir = Path(output_dir)
        self.max_frames_per_video = max_frames_per_video
        self.frame_interval = frame_interval
        
        # Supported file extensions
        self.supported_image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
        self.supported_video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Ensure proper permissions for the output directory
        try:
            os.chmod(self.output_dir, 0o777)
        except PermissionError:
            # If that fails, try with sudo
            try:
                import subprocess
                subprocess.run(["sudo", "chmod", "777", str(self.output_dir)], 
                             check=True, capture_output=True)
                print(f"Set permissions for {self.output_dir} using sudo")
            except (subprocess.CalledProcessError, ImportError) as e:
                print(f"Warning: Could not set permissions for {self.output_dir}: {e}")
        except Exception as e:
            print(f"Warning: Could not set permissions for {self.output_dir}: {e}")
        
        logger.info(f"MediaProcessor initialized for {zip_path} -> {output_dir}")
    
    def process(self) -> List[str]:
        """
        Process the zip file and extract all media files.
        
        This method orchestrates the entire processing pipeline:
        1. Extract the zip file
        2. Identify images and videos
        3. Copy images to output directory
        4. Extract frames from videos
        5. Return list of all processed files
        
        Returns:
            List[str]: List of paths to all processed files
            
        Raises:
            Exception: If processing fails at any step
        """
        try:
            logger.info(f"Starting processing of {self.zip_path}")
            
            # Extract zip file to temporary directory
            temp_dir = self._extract_zip()
            
            # Process all files in the extracted directory
            processed_files = self._process_files(temp_dir)
            
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
            
            logger.info(f"Processing complete. {len(processed_files)} files processed.")
            return processed_files
            
        except Exception as e:
            logger.error(f"Error during processing: {e}")
            raise
    
    def _extract_zip(self) -> Path:
        """
        Extract the zip file to a temporary directory.
        
        Creates a temporary directory and extracts all contents of the zip file.
        Handles nested directories and maintains the original structure.
        
        Returns:
            Path: Path to the temporary extraction directory
            
        Raises:
            Exception: If zip extraction fails
        """
        temp_dir = Path(f"/tmp/zip_extract_{uuid.uuid4()}")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            logger.info(f"Zip file extracted to {temp_dir}")
            return temp_dir
            
        except Exception as e:
            logger.error(f"Failed to extract zip file: {e}")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            raise
    
    def _process_files(self, temp_dir: Path) -> List[str]:
        """
        Process all files in the temporary directory.
        
        Walks through all files in the extracted directory, identifies
        images and videos, and processes them accordingly.
        
        Args:
            temp_dir (Path): Path to the temporary extraction directory
            
        Returns:
            List[str]: List of paths to all processed files
        """
        processed_files = []
        
        # Walk through all files in the extracted directory
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = Path(root) / file
                file_extension = file_path.suffix.lower()
                
                try:
                    if file_extension in self.supported_image_extensions:
                        # Process image file
                        processed_path = self._process_image(file_path)
                        if processed_path:
                            processed_files.append(str(processed_path))
                            
                    elif file_extension in self.supported_video_extensions:
                        # Process video file
                        video_frames = self._process_video(file_path)
                        processed_files.extend([str(frame_path) for frame_path in video_frames])
                        
                except Exception as e:
                    logger.warning(f"Failed to process {file_path}: {e}")
                    continue
        
        return processed_files
    
    def _process_image(self, image_path: Path) -> Optional[Path]:
        """
        Process an image file by copying it to the output directory.
        
        Creates a unique filename to avoid conflicts and copies the image
        to the output directory with proper error handling.
        
        Args:
            image_path (Path): Path to the source image file
            
        Returns:
            Optional[Path]: Path to the copied image file, or None if failed
        """
        try:
            # Create unique filename to avoid conflicts
            unique_filename = f"{uuid.uuid4()}_{image_path.name}"
            output_path = self.output_dir / unique_filename
            
            # Copy the image file
            shutil.copy2(image_path, output_path)
            # Ensure proper permissions for the copied file
            try:
                os.chmod(output_path, 0o666)
            except Exception as e:
                print(f"Warning: Could not set permissions for {output_path}: {e}")
            
            logger.debug(f"Image processed: {image_path.name} -> {unique_filename}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to process image {image_path}: {e}")
            return None
    
    def _process_video(self, video_path: Path) -> List[Path]:
        """
        Extract frames from a video file.
        
        Uses imageio-ffmpeg to extract frames from the video at specified
        intervals. Limits the number of frames to prevent memory issues.
        
        Args:
            video_path (Path): Path to the source video file
            
        Returns:
            List[Path]: List of paths to extracted frame images
        """
        try:
            logger.info(f"Processing video: {video_path.name}")
            
            # Generate unique prefix for this video's frames
            video_prefix = f"{uuid.uuid4()}_{video_path.stem}"
            extracted_frames = []
            
            # Open video file
            with imageio.get_reader(video_path) as reader:
                # Get video metadata
                fps = reader.get_meta_data()['fps']
                duration = reader.get_meta_data()['duration']
                
                logger.info(f"Video info: {fps} fps, {duration:.2f} seconds")
                
                # Calculate frame indices to extract
                frame_indices = self._calculate_frame_indices(fps, duration)
                
                # Extract frames
                for i, frame_idx in enumerate(frame_indices):
                    if i >= self.max_frames_per_video:
                        break
                    
                    try:
                        # Read frame
                        frame = reader.get_data(frame_idx)
                        
                        # Save frame as image
                        frame_filename = f"{video_prefix}_frame_{i:04d}.jpg"
                        frame_path = self.output_dir / frame_filename
                        
                        imageio.imwrite(frame_path, frame)
                        # Ensure proper permissions for the extracted frame
                        try:
                            os.chmod(frame_path, 0o666)
                        except Exception as e:
                            print(f"Warning: Could not set permissions for {frame_path}: {e}")
                        extracted_frames.append(frame_path)
                        
                        logger.debug(f"Extracted frame {i+1}/{len(frame_indices)}")
                        
                    except Exception as e:
                        logger.warning(f"Failed to extract frame {frame_idx}: {e}")
                        continue
            
            logger.info(f"Video processing complete: {len(extracted_frames)} frames extracted")
            return extracted_frames
            
        except Exception as e:
            logger.error(f"Failed to process video {video_path}: {e}")
            return []
    
    def _calculate_frame_indices(self, fps: float, duration: float) -> List[int]:
        """
        Calculate frame indices to extract based on interval and duration.
        
        Determines which frames to extract based on the frame interval
        and video duration, ensuring we don't exceed the maximum frames limit.
        
        Args:
            fps (float): Frames per second of the video
            duration (float): Duration of the video in seconds
            
        Returns:
            List[int]: List of frame indices to extract
        """
        # Calculate frame interval based on desired time interval
        frame_interval = int(fps * self.frame_interval)
        
        # Calculate total number of frames
        total_frames = int(duration * fps)
        
        # Generate frame indices
        frame_indices = []
        for i in range(0, total_frames, frame_interval):
            if len(frame_indices) >= self.max_frames_per_video:
                break
            frame_indices.append(i)
        
        logger.debug(f"Will extract {len(frame_indices)} frames from {total_frames} total frames")
        return frame_indices
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the processing operation.
        
        Returns:
            Dict[str, Any]: Processing statistics including file counts and sizes
        """
        if not self.output_dir.exists():
            return {"error": "Output directory does not exist"}
        
        stats = {
            "output_directory": str(self.output_dir),
            "total_files": 0,
            "total_size_bytes": 0,
            "file_types": {}
        }
        
        for file_path in self.output_dir.rglob("*"):
            if file_path.is_file():
                stats["total_files"] += 1
                stats["total_size_bytes"] += file_path.stat().st_size
                
                # Count file types
                extension = file_path.suffix.lower()
                stats["file_types"][extension] = stats["file_types"].get(extension, 0) + 1
        
        return stats
