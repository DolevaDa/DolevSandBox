# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project into the container
COPY . /app

# Install necessary system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg v4l-utils fswebcam && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies with trusted hosts
RUN pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    numpy pandas opencv-python-headless

# Grant execution permissions
RUN chmod +x test_camera_output.py

# Define the entry point
CMD ["python", "test_camera_output.py"]
