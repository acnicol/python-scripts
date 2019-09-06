# python-scripts
 
<h2> video_html_generator.py </h2>
<p>
This script generates an html file based on a directory of mp4 videos. It recursively scans the source directory and generates a thumbnail for each video, uploading them to the dst folder. It creates a simple list of all the videos.

It can be useful to trigger the script when motion videos are uploaded to an FTP server (using watchman or some other file watcher). You can then add the website to other home automation displays, like Home Assistant. In HA, just add an iFrame card and set the url to http://<your_server_ip/index.html.


![](demo_animation.gif)
</p>

Install instructions:
1. Install ffmpeg for your platform
2. Install python3 and pip3
3. pip install ffmpy yattag

Usage:
`python video-html-generator.py --src /var/ftp/uploads --dst /var/www/camsite/`

--src is the source folder where you have your videos stored.<br>
--dst is the destination folder where you will host the site.<br>

Note: It is currently hard coded to only support mp4 formats.
