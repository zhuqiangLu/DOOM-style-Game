#!/usr/bin/env python3
"""
Script to convert recorded frames to videos using ffmpeg
Run this after recording sessions to create MP4 videos
"""

import os
import subprocess
import json
from pathlib import Path

def create_videos_from_recordings():
    """Convert all recorded frame sequences to MP4 videos"""
    recordings_dir = Path("recordings")
    
    if not recordings_dir.exists():
        print("No recordings directory found!")
        return
    
    for session_dir in recordings_dir.iterdir():
        if not session_dir.is_dir():
            continue
            
        print(f"Processing session: {session_dir.name}")
        
        # Check if recording_data.json exists
        data_file = session_dir / "recording_data.json"
        if not data_file.exists():
            print(f"  No recording_data.json found in {session_dir.name}")
            continue
            
        # Read recording data
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        print(f"  All colors: {data['all_colors']}")
        print(f"  Visited waypoints: {len(data['visited_waypoints'])}")
        for i, wp in enumerate(data['visited_waypoints']):
            print(f"    {i+1}. {wp['color_name']} {wp['color_code']} at {wp['waypoint']}")
        
        # Find frame files
        frame_files = sorted(session_dir.glob("frame_*.png"))
        if not frame_files:
            print(f"  No frame files found in {session_dir.name}")
            continue
            
        # Create video using ffmpeg
        output_video = session_dir / f"{session_dir.name}.mp4"
        input_pattern = str(session_dir / "frame_%06d.png")
        
        try:
            cmd = [
                "ffmpeg", "-y",  # -y to overwrite output files
                "-framerate", "24",  # Match game FPS
                "-i", input_pattern,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "18",  # High quality
                str(output_video)
            ]
            
            print(f"  Creating video: {output_video}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✓ Video created successfully: {output_video}")
                # Optionally remove frame files to save space
                # for frame_file in frame_files:
                #     frame_file.unlink()
            else:
                print(f"  ✗ Error creating video: {result.stderr}")
                
        except FileNotFoundError:
            print("  ✗ ffmpeg not found! Please install ffmpeg to create videos.")
            print("     On macOS: brew install ffmpeg")
            print("     On Ubuntu: sudo apt install ffmpeg")
            print("     On Windows: Download from https://ffmpeg.org/")

def print_session_summary():
    """Print a summary of all recorded sessions"""
    recordings_dir = Path("recordings")
    
    if not recordings_dir.exists():
        print("No recordings directory found!")
        return
        
    print("\n=== RECORDING SESSIONS SUMMARY ===")
    
    for session_dir in sorted(recordings_dir.iterdir()):
        if not session_dir.is_dir():
            continue
            
        data_file = session_dir / "recording_data.json"
        if not data_file.exists():
            continue
            
        with open(data_file, 'r') as f:
            data = json.load(f)
            
        print(f"\nSession: {data['session_id']}")
        print(f"Timestamp: {data['timestamp']}")
        print(f"Total colors: {len(data['all_colors'])}")
        print(f"Visited waypoints: {len(data['visited_waypoints'])}")
        
        if data['visited_waypoints']:
            print("Visit order:")
            for i, wp in enumerate(data['visited_waypoints']):
                print(f"  {i+1}. {wp['color_name']} {wp['color_code']}")

if __name__ == "__main__":
    print("=== DOOM Game Video Generator ===")
    print_session_summary()
    print("\n=== Creating Videos ===")
    create_videos_from_recordings()
    print("\nDone!")