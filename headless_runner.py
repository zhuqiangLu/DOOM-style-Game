#!/usr/bin/env python3
"""
Headless runner for generating multiple video sessions
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def run_headless_session(session_num=1, total_sessions=1):
    """Run a single headless session"""
    print(f"Starting headless session {session_num}/{total_sessions}")
    
    # Set headless environment BEFORE importing pygame
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    
    try:
        # Initialize pygame first
        import pygame
        pygame.init()
        
        # Force display initialization for headless mode
        pygame.display.init()
        
        # Import and run the game
        from main import Game
        game = Game()
        
        # Run until completion (autopilot will exit when done)
        while True:
            game.check_events()
            game.update()
            game.draw()
            
    except SystemExit:
        print(f"Session {session_num} completed")
    except Exception as e:
        print(f"Error in session {session_num}: {e}")
    finally:
        # Clean up pygame
        try:
            pygame.quit()
        except:
            pass

def run_multiple_sessions(num_sessions=5):
    """Run multiple headless sessions"""
    print(f"Starting {num_sessions} headless sessions...")
    
    for i in range(1, num_sessions + 1):
        print(f"\n{'='*50}")
        print(f"SESSION {i}/{num_sessions}")
        print(f"{'='*50}")
        
        start_time = time.time()
        run_headless_session(i, num_sessions)
        end_time = time.time()
        
        print(f"Session {i} completed in {end_time - start_time:.2f} seconds")
        
        # Small delay between sessions
        if i < num_sessions:
            time.sleep(1)
    
    print(f"\nAll {num_sessions} sessions completed!")
    print("Run 'python create_videos.py' to convert frames to MP4 videos")

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import pygame
        print(f"✓ Pygame version: {pygame.version.ver}")
    except ImportError:
        print("✗ Pygame not found! Install with: pip install pygame")
        return False
    
    try:
        import json
        print("✓ JSON module available")
    except ImportError:
        print("✗ JSON module not found!")
        return False
    
    return True

def main():
    """Main entry point"""
    print("=== DOOM Headless Video Generator ===")
    
    if not check_dependencies():
        sys.exit(1)
    
    # Parse command line arguments
    num_sessions = 1
    if len(sys.argv) > 1:
        try:
            num_sessions = int(sys.argv[1])
        except ValueError:
            print("Usage: python headless_runner.py [number_of_sessions]")
            print("Example: python headless_runner.py 10")
            sys.exit(1)
    
    print(f"Will generate {num_sessions} video session(s)")
    print("Press Ctrl+C to cancel...")
    
    try:
        time.sleep(2)  # Give user time to cancel
        run_multiple_sessions(num_sessions)
    except KeyboardInterrupt:
        print("\nCancelled by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()