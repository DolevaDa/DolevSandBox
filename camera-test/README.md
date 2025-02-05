# Camera Testing Automation

This project provides an **automated testing framework for laptop cameras**, validating image capture, video recording, and various quality metrics. It supports **Docker integration**, making it easy to run tests in an isolated environment.

---

## 📌 Features

- ✅ Automated **image & video capture**
- ✅ Quality checks for **resolution, brightness, FPS, and audio**
- ✅ **Pass/Fail assertion system** for test validation
- ✅ **Audit logging** for every test session**
- ✅ **Multiple camera support** (`/dev/video0`, `/dev/video1`, etc.)
- ✅ **Dockerized execution** for portability

---

## 🚀 Installation Guide

### 1️⃣ Install Docker

#### **On Ubuntu**
```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
```

#### **On Windows/Mac**
1. Download **[Docker Desktop](https://www.docker.com/get-started/)**
2. Install and run Docker.

---

## 🐳 Build & Run the Docker Container

### 2️⃣ Build the Docker Image
```bash
sudo docker build -t camera-test .
```

### 3️⃣ Run the Container

#### **Run with Default Camera (`/dev/video0`)**
```bash
sudo docker run --rm --device=/dev/video0 -e RUNNING_IN_DOCKER=1 -v $(pwd)/logs:/app/logs -v $(pwd)/captures:/app/captures camera-test
```

#### **Run with a Specific Camera (e.g., `/dev/video1`)**
```bash
sudo docker run --rm --device=/dev/video1 -e CAMERA_DEVICE=/dev/video1 -v $(pwd)/logs:/app/logs -v $(pwd)/captures:/app/captures camera-test
```

#### **Run Tests on All Cameras**
```bash
for cam in $(ls /dev/video* | grep video); do
    sudo docker run --rm --device=$cam -e CAMERA_DEVICE=$cam     -v $(pwd)/logs:/app/logs -v $(pwd)/captures:/app/captures camera-test
done
```

---

## 📂 Project Structure

```
📁 camera-test
│── 📄 Dockerfile           # Docker setup
│── 📄 README.md            # Project documentation
│── 📄 test_camera_output.py  # Main test script
│── 📄 camera_controller.py   # Camera interaction logic
│── 📁 captures             # Stores captured images/videos (bind-mounted)
│── 📁 logs                 # Stores test logs (bind-mounted)
│── 📄 .dockerignore        # Ignore unnecessary files in Docker
```

---

## 📜 Test Assertions

Each test **logs results and validates correctness** using assertions.

| Test                | Description                               | Pass Criteria |
|---------------------|-------------------------------------------|--------------|
| **Image Exists**    | Checks if an image was captured          | ✅ File exists |
| **Image Validity**  | Ensures image is a valid JPEG           | ✅ OpenCV can read file |
| **Image Resolution**| Checks if image matches expected size   | ✅ 1280x720 |
| **Image Brightness**| Ensures image is not too dark or bright | ✅ Brightness in range 50-200 |
| **Video Exists**    | Confirms the recorded video is saved    | ✅ File exists |
| **Video Validity**  | Ensures the video file is playable      | ✅ FFmpeg validation |
| **Video FPS**       | Checks if FPS matches expected value    | ✅ 30 FPS |
| **Audio Check**     | Ensures an audio track is present       | ✅ Audio detected |

Each test will log **PASS/FAIL** results.

---

## 🛠 Debugging Inside Docker

To manually inspect files and logs inside the container:

```bash
sudo docker run -it --rm --device=/dev/video0 -v $(pwd)/logs:/app/logs -v $(pwd)/captures:/app/captures camera-test /bin/bash
```

---

## 🧹 Cleanup

To remove old containers and images:
```bash
sudo docker system prune -a
```

To delete the Docker image:
```bash
sudo docker rmi camera-test
```

---

## ✅ Conclusion

This project provides a **fully automated testing solution** for **camera devices** with **Docker support**. By using **Python, OpenCV, FFmpeg, and Docker**, it ensures **consistent, portable, and repeatable camera quality testing**.

---

## 📩 Need Help?

If you encounter any issues, feel free to ask!
