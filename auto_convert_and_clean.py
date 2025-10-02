#!/usr/bin/env python3
"""
Automatically convert all recordings to MP4 and clean up frame images
"""

import os
import subprocess
import json
from pathlib import Path
import shutil

def check_ffmpeg():
    """Check if ffmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ ffmpeg is available")
            return True
    except FileNotFoundError:
        pass
    
    print("✗ ffmpeg not found!")
    print("Install ffmpeg:")
    print("  macOS: brew install ffmpeg")
    print("  Ubuntu: sudo apt install ffmpeg")
    print("  Windows: Download from https://ffmpeg.org/")
    return False

def convert_session_to_mp4(session_dir):
    """Convert a single session's frames to MP4"""
    session_path = Path(session_dir)
    session_name = session_path.name
    
    # Find frame files
    frame_files = sorted(session_path.glob("frame_*.png"))
    if not frame_files:
        print(f"  ⚠ No frame files found in {session_name}")
        return False
    
    # Check if MP4 already exists
    mp4_file = session_path / f"{session_name}.mp4"
    if mp4_file.exists():
        print(f"  ✓ MP4 already exists: {mp4_file.name}")
        return True
    
    # Create video using ffmpeg
    input_pattern = str(session_path / "frame_%06d.png")
    
    try:
        cmd = [
            "ffmpeg", "-y",  # -y to overwrite output files
            "-framerate", "24",  # Match game FPS
            "-i", input_pattern,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",  # High quality
            str(mp4_file)
        ]
        
        print(f"  🎬 Creating video: {mp4_file.name}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✓ Video created successfully: {mp4_file.name}")
            return True
        else:
            print(f"  ✗ Error creating video: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ✗ Exception during video creation: {e}")
        return False

def clean_frame_images(session_dir, keep_first_last=True):
    """Clean up frame images, optionally keeping first and last frames"""
    session_path = Path(session_dir)
    frame_files = sorted(session_path.glob("frame_*.png"))
    
    if not frame_files:
        return
    
    print(f"  🧹 Cleaning up {len(frame_files)} frame images...")
    
    if keep_first_last and len(frame_files) > 2:
        # Keep first and last frames for reference
        frames_to_keep = {frame_files[0], frame_files[-1]}
        frames_to_delete = [f for f in frame_files if f not in frames_to_keep]
        
        for frame_file in frames_to_delete:
            try:
                frame_file.unlink()
            except Exception as e:
                print(f"    ⚠ Could not delete {frame_file.name}: {e}")
        
        print(f"    ✓ Deleted {len(frames_to_delete)} frames, kept first and last")
    else:
        # Delete all frames
        for frame_file in frame_files:
            try:
                frame_file.unlink()
            except Exception as e:
                print(f"    ⚠ Could not delete {frame_file.name}: {e}")
        
        print(f"    ✓ Deleted all {len(frame_files)} frames")

def process_session(session_dir, clean_frames=True, keep_first_last=True):
    """Process a single session: convert to MP4 and clean frames"""
    session_path = Path(session_dir)
    session_name = session_path.name
    
    print(f"\n📁 Processing session: {session_name}")
    
    # Check if recording_data.json exists
    data_file = session_path / "recording_data.json"
    if not data_file.exists():
        print(f"  ⚠ No recording_data.json found")
        return False
    
    # Read recording data
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        print(f"  📊 All colors: {len(data.get('all_colors', []))}")
        print(f"  🎯 Visited waypoints: {len(data.get('visited_waypoints', []))}")
        
        # Show visit order
        for i, wp in enumerate(data.get('visited_waypoints', [])[:5]):  # Show first 5
            print(f"    {i+1}. {wp.get('color_name', 'unknown')} {wp.get('color_code', [])}")
        if len(data.get('visited_waypoints', [])) > 5:
            print(f"    ... and {len(data.get('visited_waypoints', [])) - 5} more")
            
    except Exception as e:
        print(f"  ⚠ Error reading recording data: {e}")
    
    # Convert to MP4
    success = convert_session_to_mp4(session_dir)
    
    if success and clean_frames:
        # Clean up frame images
        clean_frame_images(session_dir, keep_first_last)
    
    return success

def process_all_recordings(clean_frames=True, keep_first_last=True):
    """Process all recording sessions"""
    recordings_dir = Path("recordings")
    
    if not recordings_dir.exists():
        print("❌ No recordings directory found!")
        return
    
    # Find all session directories
    session_dirs = [d for d in recordings_dir.iterdir() if d.is_dir()]
    
    if not session_dirs:
        print("❌ No recording sessions found!")
        return
    
    print(f"🔍 Found {len(session_dirs)} recording session(s)")
    
    # Process each session
    successful = 0
    failed = 0
    
    for session_dir in sorted(session_dirs):
        try:
            if process_session(session_dir, clean_frames, keep_first_last):
                successful += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Error processing {session_dir.name}: {e}")
            failed += 1
    
    # Summary
    print(f"\n📈 SUMMARY:")
    print(f"  ✅ Successfully processed: {successful}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📁 Total sessions: {len(session_dirs)}")
    
    if successful > 0:
        print(f"\n🎉 {successful} MP4 video(s) created successfully!")
        if clean_frames:
            print("🧹 Frame images cleaned up to save space")

def main():
    """Main entry point"""
    print("🎬 DOOM Auto Video Converter & Cleaner")
    print("=" * 50)
    
    # Check dependencies
    if not check_ffmpeg():
        return
    
    # Process all recordings
    process_all_recordings(
        clean_frames=True,      # Clean up frame images
        keep_first_last=True    # Keep first and last frames for reference
    )

if __name__ == "__main__":
    main()