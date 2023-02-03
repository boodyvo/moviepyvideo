apt-get update
apt-get install -y python3-pip nano ffmpeg libsm6 libxext6

pip3 install moviepy boto3 botocore Pillow numpy flask requests
# optionally for tests pip install opencv-python