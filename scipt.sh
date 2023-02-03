apt-get update
apt-get install -y python3-pip nano ffmpeg libsm6 libxext6 imagemagick screen tmux

pip3 install moviepy boto3 botocore Pillow numpy flask requests

# set correct rights for imagemagick
# example: https://en.linuxportal.info/tutorials/troubleshooting/how-to-fix-errors-from-imagemagick-imagick-conversion-system-security-policy

# flask --app main run --host=0.0.0.0

#Here's an example of how you could run a Flask server in a screen session:
#
#Start a new screen session: screen
#Start the Flask server: python <flask_script.py>
#Detach from the screen session: CTRL-A followed by d
#Note that in the above example, <flask_script.py> should be replaced with the name of the script that runs your Flask server.
#
#Once you have detached from the screen session, the Flask server will continue to run in the background even after you close the ssh connection. To reattach to the screen session, use the following command: screen -r.
