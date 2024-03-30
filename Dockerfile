# Use the official Python image as a base
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update package lists and install build essentials
RUN apt-get update && \
    apt-get install -y build-essential portaudio19-dev gettext libgl1-mesa-glx git cmake

# Install PyAudio
RUN pip install --no-cache-dir pyaudio

# Install Python dependencies from requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Clone and install dlib
RUN git clone https://github.com/davisking/dlib.git && \
    cd dlib && \
    mkdir build && \
    cd build && \
    cmake .. && \
    cmake --build . && \
    cd ../.. && \
    python3 dlib/setup.py install && \
    rm -rf dlib

# Install libmysqlclient-dev and mysqlclient
RUN apt-get install -y libmysqlclient-dev && \
    pip install --no-cache-dir mysqlclient

# Install face-recognition
RUN pip install --no-cache-dir face-recognition==1.3.0

# Set the working directory in the container
WORKDIR /emocare

# Copy the Django project files
COPY . /emocare


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
