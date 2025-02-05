import subprocess
import os


class CameraController:
    def __init__(self, device='/dev/video0',  output_dir='captures'):
        self.device = device
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def list_cameras(self):
        """Lists available cameras on the system."""
        result = subprocess.run(['v4l2-ctl', '--list-devices'], capture_output=True, text=True)
        return result.stdout

    def set_camera_property(self, prop, value):
        """Sets a camera property using v4l2-ctl."""
        command = ['v4l2-ctl', '-d', self.device, '--set-ctrl', f'{prop}={value}']
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout

    def get_camera_property(self, prop):
        """Gets a camera property using v4l2-ctl."""
        command = ['v4l2-ctl', '-d', self.device, '--get-ctrl', prop]
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout

    def capture_image(self, filename='image.jpg'):
        """Captures an image from the camera using ffmpeg."""
        output_path = os.path.join(self.output_dir, filename)
        command = [
            'ffmpeg', '-y', '-f', 'video4linux2', '-i', self.device, '-frames:v', '1', output_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        return output_path if result.returncode == 0 else result.stderr

    def record_video(self, duration=10, filename='video.mp4'):
        """Records a video for a configured time using FFmpeg with error handling and explicit paths."""
        output_path = os.path.join(self.output_dir, filename)

        command = [
            '/usr/bin/ffmpeg', '-f', 'v4l2', '-input_format', 'mjpeg', '-video_size', '640x480', '-framerate', '30',
            '-t', str(duration),
            '-i', self.device, '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p', output_path
        ]

        process = subprocess.Popen(" ".join(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   universal_newlines=True, shell=True)
        stdout, stderr = process.communicate()

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        else:
            return f'Failed to record video. FFmpeg output:\nSTDOUT: {stdout}\nSTDERR: {stderr}'


if __name__ == "__main__":
    camera = CameraController()
    print("Available Cameras:")
    print(camera.list_cameras())

    print("\nCapturing Image...")
    print(camera.capture_image())

    print("\nRecording Video...")
    print(camera.record_video(duration=5))
