import os
import cv2
import subprocess
import numpy as np
import json
import time
from datetime import datetime
from camera_controller import CameraController

class CameraTests:
    def __init__(self, camera_device, fps=30, duration=5, output_dir="captures", log_dir="logs"):
        self.camera_device = camera_device
        self.fps = fps
        self.duration = duration
        self.output_dir = output_dir
        self.log_dir = log_dir

        # Generate a unique timestamp for each test session
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Unique file names for this session
        self.image_path = os.path.join(output_dir, f'image_{self.timestamp}.jpg')
        self.video_path = os.path.join(output_dir, f'video_{self.timestamp}.mp4')
        self.log_path = os.path.join(log_dir, f'{self.timestamp}_log.txt')

        # Initialize the CameraController for the selected camera
        self.camera = CameraController(device=camera_device, output_dir=self.output_dir)

        # Ensure directories exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

        # Create log file
        with open(self.log_path, "w") as log_file:
            log_file.write(f"Audit Log - Test Session {self.timestamp} - Camera: {self.camera_device}\n")
            log_file.write("=" * 50 + "\n")

    def log(self, message):
        """Write messages to the audit log file."""
        with open(self.log_path, "a") as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        print(message)

    def assert_test(self, condition, message):
        """Assert a test case and log the result."""
        try:
            assert condition, message
            self.log(f"PASS: {message}")
        except AssertionError as e:
            self.log(f"FAIL: {message}")

    def record_video(self):
        """Triggers the CameraController to record a video."""
        self.log(f"Starting video recording on {self.camera_device}: {self.duration}s at {self.fps} FPS...")
        self.camera.record_video(duration=self.duration, filename=f"video_{self.timestamp}.mp4")
        self.log("Recording complete.")

    def capture_image(self):
        """Captures an image before running tests."""
        self.log(f"Capturing an image on {self.camera_device}...")
        self.camera.capture_image(filename=f"image_{self.timestamp}.jpg")

        # Ensure the image exists before proceeding
        max_retries = 3
        for attempt in range(max_retries):
            time.sleep(1)  # Small delay to allow file to be written
            if os.path.exists(self.image_path) and os.path.getsize(self.image_path) > 0:
                self.log("Image captured successfully.")
                return True
            self.log(f"Retrying image capture... Attempt {attempt + 1}")
        self.log("Image capture failed after retries.")
        return False

    def run_tests(self):
        """Run all tests and print results."""
        self.log(f"Running Tests on Camera: {self.camera_device}")

        if not self.capture_image():
            self.log("Skipping image tests due to failed capture.")
        else:
            self.log("Running Image Tests...")
            self.assert_test(self.test_image_exists(), "Image exists")
            self.assert_test(self.test_image_validity(), "Image is a valid JPEG file")
            self.assert_test(self.test_image_resolution(), "Image resolution is correct")
            self.assert_test(self.test_image_brightness(), "Image brightness is acceptable")

        self.record_video()
        self.log("Running Video Tests...")
        self.assert_test(self.test_video_exists(), "Video file exists")
        self.assert_test(self.test_video_validity(), "Video is a valid file")
        self.assert_test(self.test_video_fps(), "Video FPS is correct")
        self.assert_test(self.test_video_audio(), "Audio track detected in video")

        self.log("Test session completed.")

    # Image Tests
    def test_image_exists(self):
        """Check if the captured image exists."""
        return os.path.exists(self.image_path) and os.path.getsize(self.image_path) > 0

    def test_image_validity(self):
        """Check if the image is a valid, non-corrupt JPEG file."""
        img = cv2.imread(self.image_path)
        return img is not None

    def test_image_resolution(self, expected_width=1280, expected_height=720):
        """Verify the image resolution."""
        img = cv2.imread(self.image_path)
        if img is None:
            self.log("Skipping resolution test: Image cannot be loaded.")
            return False
        return img.shape[1] == expected_width and img.shape[0] == expected_height

    def test_image_brightness(self):
        """Check if the image is too dark or too bright."""
        img = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            self.log("Skipping brightness test: Image cannot be loaded.")
            return False
        avg_brightness = np.mean(img)
        return 50 <= avg_brightness <= 200

    # Video Tests
    def test_video_exists(self):
        """Check if the recorded video file exists."""
        return os.path.exists(self.video_path)

    def test_video_validity(self):
        """Check if the video is valid using FFprobe."""
        command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'json', self.video_path]
        result = subprocess.run(command, capture_output=True, text=True)
        return '"width"' in result.stdout and '"height"' in result.stdout

    def test_video_fps(self):
        """Check if the video FPS is correct."""
        command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'json', self.video_path]
        result = subprocess.run(command, capture_output=True, text=True)

        try:
            output_json = json.loads(result.stdout)
            fps_str = output_json["streams"][0]["r_frame_rate"]
            fps = eval(fps_str)  # Converts "30/1" to 30
            return abs(fps - self.fps) <= 1
        except Exception:
            return False

    def test_video_audio(self):
        """Check if the video has an audio track."""
        command = ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_name', '-of', 'json', self.video_path]
        result = subprocess.run(command, capture_output=True, text=True)
        return "codec_name" in result.stdout



def list_cameras():
    """Lists all available camera devices."""
    result = subprocess.run(['v4l2-ctl', '--list-devices'], capture_output=True, text=True)
    devices = [line.strip() for line in result.stdout.split("\n") if "/dev/video" in line]
    return devices

if __name__ == "__main__":
    cameras = list_cameras()

    if not cameras:
        print("No cameras detected.")
        exit(1)

    print("Available Cameras:")
    for i, cam in enumerate(cameras):
        print(f"{i + 1}. {cam}")

    # Check if CAMERA_DEVICE is set in environment variables (for Docker)
    camera_device = os.getenv("CAMERA_DEVICE")

    if camera_device:
        print(f"Using camera from environment variable: {camera_device}")
    else:
        # If running inside Docker without input support, auto-select the first camera
        if os.getenv("RUNNING_IN_DOCKER"):
            camera_device = cameras[0]  # Auto-select first camera
            print(f"Running in Docker: Auto-selected {camera_device}")
        else:
            # Allow user input in normal execution
            choice = input("Select a camera (enter number) or type 'all' to test all: ").strip()

            if choice.lower() == 'all':
                for cam in cameras:
                    tester = CameraTests(camera_device=cam)
                    tester.run_tests()
                exit(0)
            else:
                try:
                    cam_index = int(choice) - 1
                    if cam_index < 0 or cam_index >= len(cameras):
                        print("Invalid selection.")
                        exit(1)
                    camera_device = cameras[cam_index]
                except ValueError:
                    print("Invalid input.")
                    exit(1)

    # Run tests for the selected camera
    tester = CameraTests(camera_device=camera_device)
    tester.run_tests()
