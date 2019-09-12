#
# This scripts generates an html file based on a directory of mp4 videos. 

#Instructions:
#
# Install ffmpeg for your platform
# Install python3 and pip3
# pip install ffmpy yattag python-crontab

import os
import time
import argparse
from shutil import copyfile
from ffmpy import FFmpeg
from yattag import Doc, indent
doc, tag, text = Doc().tagtext()

class VideoHtmlGenerator:

    HTML_FILENAME = 'index.html'

    OVERWRITE_THUMBNAIL = False     

    def __init__(self, src_dir, dst_dir, cronjob_frequency):
        self.video_files = []

        self.video_root_dir         = src_dir
        self.web_server_dir         = dst_dir
        self.web_server_video_dir   = os.path.join(self.web_server_dir, 'videos')
        self.cronjob_frequency = cronjob_frequency

    def generate(self):
        self.search_for_videos()
        self.copy_videos()
        self.generate_html()
        self.setup_crontab()

    def search_for_videos(self):

        print ('Searching ' + self.video_root_dir + ' for mp4 files...')

        for dirpath, dnames, fnames in os.walk(self.video_root_dir):
            for f in fnames:
                if f.endswith('.mp4'):
                    file_path = os.path.join(dirpath, f)
                    # print('Found mp4 file at ' + file_path)
                    self.video_files.append(file_path)

        self.video_files.sort(reverse=True)

        if len(self.video_files) == 0:
            print ('No video files found!')
        else:
            print(len(self.video_files), 'video files found')


    # Copy the mp4s to the web server directory so it can serve them
    def copy_videos(self):

        print ('Copying video files to ' + self.web_server_video_dir)

        if not os.path.exists(self.web_server_video_dir):
            os.mkdir(self.web_server_video_dir)

        skipped = 0
        copied = 0

        for file_path in self.video_files:
            head, filename = os.path.split(file_path)   
            dst_filepath = os.path.join(self.web_server_video_dir, filename)

            if os.path.exists(dst_filepath):
                # print(filename + ' already exists in destination folder.')
                skipped += 1
            else:
                print('Copying video to ' + file_path)
                copied += 1
                copyfile(file_path, dst_filepath)

        if skipped > 0:
            print('Skipped copy of', skipped, 'existing video files')
        if copied > 0:
            print('Copied', copied, 'video files.')

    def generate_html(self):

        with tag('html'):
            with tag('body'):
                with tag('a', href='index.html', target="_blank"):
                    with tag('div'):
                        with tag('h3'):
                            text('Open in new tab')

                with tag('ul', id='motion-list', style="list-style-type:none"):
                    for index, movie_path in enumerate(self.video_files):
                        head, movie_filename = os.path.split(movie_path)
                        with tag('li'):
                            with tag('a', href='videos/' + movie_filename, target="_blank"):

                                link_text = movie_filename

                                output_image_path = movie_path.strip('.mp4') + '.png'
                                head, image_filename = os.path.split(output_image_path)

                                print('Thumbnail', index + 1, 'of', len(self.video_files))
                                self.generate_thumbnail(video_path=movie_path, output_image_path=output_image_path)
                                
                                doc.stag('img', src='videos/' + image_filename, width='300')


        # Write the HTML to disk
        html_text = indent(doc.getvalue(), indent_text = True)

        html_filepath = os.path.join(self.web_server_dir, self.HTML_FILENAME)

        print ('Generating html file at ' + html_filepath)
        file = open(html_filepath, 'w+')
        file.write(html_text)
        file.close()

    def generate_thumbnail(self, video_path, output_image_path):
        head, image_filename = os.path.split(output_image_path)
        image_output_path = os.path.join(self.web_server_video_dir, image_filename)

        if os.path.exists(image_output_path) and not self.OVERWRITE_THUMBNAIL:
            print(image_filename + ' thumnail already exists.')
        else:
            print('Generating thumbnail at ' + output_image_path)
            try:
                last_mod_time = time.ctime(os.path.getmtime(video_path))
                last_mod_time = last_mod_time.replace(':','\\\\:')  # Handle escaping for ffmpeg text

                ffmpeg_options = ['-loglevel', 'panic', '-y', '-ss', '00:00:5', '-vframes', '1', '-vf', "scale=iw/4:-1, drawtext=fontfile=/Library/Fonts/Verdana.ttf: text=" + last_mod_time + ": r=25: x=(w-tw)/2: y=h-(2*lh): fontsize=32: fontcolor=white: ", '-an']
                ff = FFmpeg(inputs={video_path: None}, outputs={image_output_path: ffmpeg_options})
                # print (ff.cmd)
                ffmpeg_result = ff.run()
                # print(ffmpeg_result)

            except Exception as e: 
                print(e)

    def setup_crontab(self):

        if (self.cronjob_frequency is not None):
            from crontab import CronTab

            crontab_comment = 'Video HTML Generator script'
            script_path = os.path.realpath(__file__)
            command = 'python3 ' + script_path +  ' --src ' + self.video_root_dir + ' --dst ' + self.web_server_dir
            print(command)
            my_cron = CronTab(user='alex')
            existing_cron_job = None
            for job in my_cron:
                if job.comment == crontab_comment:
                    print ('Updating existing cronjob')
                    existing_cron_job = job

            print('Crontab job command is ' + command)
            if existing_cron_job is None:
                print ('Creating new cronjob')
                existing_cron_job = my_cron.new(command=command, comment=crontab_comment)
            else:
                existing_cron_job.set_command(command)
                
            existing_cron_job.minute.every(self.cronjob_frequency)
             
            my_cron.write()

def main():

    parser = argparse.ArgumentParser(description='This script takes a source folder of mp4 files and generates a webpage.')# You can optionally add --dst to specify a directory where you would like to copy the files to (a web server dir).')
    parser.add_argument('-s','--src', help='Root directory where you have mp4 files stored.',required=True)
    parser.add_argument('-d','--dst', help='Directory where you are hosting your web server, where the generated web page will be copied.', required=True)
    parser.add_argument('-c', '--cronjob', help='Add an entry to the crontab to start this script periodically.')
    args = parser.parse_args()

    src = args.src
    dst = args.dst
    cronjob = args.cronjob

    htmlGenerator = VideoHtmlGenerator(src, dst, cronjob)
    htmlGenerator.generate()

if __name__ == "__main__":
    main()
