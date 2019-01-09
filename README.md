# Motion Detection and Relay Control on a Raspberry Pi with OpenCV

## Description
This code was thrown together and used during a presentation to Mined Minds. It uses a Raspberry Pi with a Camera Module and a Relay Board to detect motion in video frames using OpenCV. Still images are recorded during motion and a relay is activated and then deactivated after 5 seconds of no motion.

## System Configuration
* Install Raspbian Lite image on Micro SD card.
* Enable SSH access by creating a “ssh” file on the SD card.
* Install Apache Web Server
   * sudo apt-get install apache2 –y
   * sudo chown pi:pi /var/www/html 
* Install Git
   * sudo apt-get install git –y
* Install OpenCV 3.4.0
   * https://www.life2coding.com/install-opencv-3-4-0-python-3-raspberry-pi-3/

