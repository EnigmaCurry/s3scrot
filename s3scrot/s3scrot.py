import subprocess
import shlex
import ConfigParser
import tempfile
import os, os.path
import uuid
import argparse
import subprocess
import webbrowser

from boto.s3.connection import S3Connection
from boto.s3.key import Key

try:
    use_libnotify = True
    from gi.repository import Notify
    Notify.init('s3scrot')
except ImportError:
    use_libnotify = False

# Default config file to write to ~/.s3scrot: 
default_config = """# s3scrot config file
#
# Enter your S3 bucket information and credentials below.
# It's recommended that you create a bucket and access key specifically for 
# s3scrot and never use your root AWS keys. That way if these keys get stolen
# they will only have access to your screenshot bucket.
# 
# You can create a new bucket and access key through the AWS console: 
# https://console.aws.amazon.com - select the IAM console, and create a new group,
# call it whatever you like, and add a Custom Policy to limit it's access to just
# the screenshot bucket. If your bucket is called foobar-screenshots, an example 
# Custom Policy would look like:
#
#     {
#      "Statement": [
#        {
#          "Action": "s3:*",
#          "Effect": "Allow",
#          "Resource": [
#            "arn:aws:s3:::foobar-screenshots",
#            "arn:aws:s3:::foobar-screenshots/*"
#          ]
#        }
#      ]
#     }
#
# Create a new user and assign him to the group you created. Be sure to enter the
# access key and secret key for this user below :

[s3]
bucket = YOUR_BUCKET
access_key = YOUR_ACCESS_KEY
secret_key = YOUR_SECRET_KEY
"""

def read_config(config_path=None):
    if not config_path:
        config_path = os.path.join(os.path.expanduser("~"), '.s3scrot')
    if not os.path.exists(config_path):
        print("Config file not found.")
        with open(config_path, "w") as f:
            f.write(default_config)
        os.chmod(config_path, 0600)
        print("New config file created at {config_path}. You must edit this file with your own Amazon S3 settings.".format(**locals()))
        exit(1)
    config = ConfigParser.ConfigParser()
    config.read(config_path)
    # Validate config:
    sections = ['s3']
    fields = ['bucket', 'access_key', 'secret_key']
    validated = {}
    for s in sections:
        validated[s] = {}
        for f in fields:
            try:
                validated[s][f] = config.get('s3', f)
            except ConfigParser.NoOptionError:
                print("Config file ({config_path}) is missing required field: {f}".format(**locals()))
                print("See comments in the config file for more details.")
                exit(1)
            except ConfigParser.NoSectionError:
                print("Config file({config_path}) is missing section: s3".format(**locals()))
                print("See comments in the config file for more details.")
                exit(1)

    if validated['s3']['bucket'] == "YOUR_BUCKET":
        print("You still need to edit your config file with your Amazon S3 settings: {config_path}".format(**locals()))
        exit(1)
    return validated

def take_screenshot(non_interactive=False, img_format='png', quality='75'):
    """Take a screenshot with the scrot tool. Return the path of the screenshot.

    If non_interactive==True, capture the whole screen, rather than a mouse selection"""
    select = "-s"
    if non_interactive:
        select = ""
    quality = "-q {quality}".format(quality=quality)
    ss = tempfile.mktemp("."+img_format)
    proc = subprocess.Popen(shlex.split("scrot {select} {quality} {ss}".format(**locals())))
    proc.communicate()
    return ss

def upload_to_s3(path, config):
    conn = S3Connection(config['s3']['access_key'], config['s3']['secret_key'])
    bucket = conn.get_bucket(config['s3']['bucket'])
    key = Key(bucket, str(uuid.uuid1())+"."+path.split(".")[-1])
    key.set_contents_from_filename(path)
    key.set_canned_acl('public-read')
    return key.generate_url(0, query_auth=False, force_http=True)

def copy_to_clipboard(text):
    c = subprocess.Popen(shlex.split("xclip -selection clipboard"), stdin=subprocess.PIPE)
    c.communicate(input=text.encode('utf-8'))

def main():
    parser = argparse.ArgumentParser(description='s3scrot')
    parser.add_argument('-n', '--non-interactive', dest='non_interactive', 
                        action="store_true",
                        help='Capture the whole screen, don\'t wait for mouse selection')
    parser.add_argument('-c', '--no-clipboard', dest='no_clipboard', 
                        action="store_true",
                        help='Do not copy URL to clipboard')
    parser.add_argument('-b', '--open-browser', dest='open_browser', 
                        action="store_true",
                        help='Open browser to screenshot URL')
    parser.add_argument('-p', '--print-url', dest='print_url', 
                        action="store_true",
                        help='Print URL')
    parser.add_argument('-j', '--jpeg', dest='use_jpeg',
                        action="store_true",
                        help='Use JPEG compression instead of PNG')
    parser.add_argument('-q', '--quality', dest='quality',
                        default='75',
                        help='Image quality (1-100) high value means high size, low compression. Default: 75. For lossless png, low quality means high compression.')


    args = parser.parse_args()

    img_format = "png"
    if args.use_jpeg:
        img_format = "jpg"

    config = read_config()
    ss = take_screenshot(args.non_interactive, img_format, args.quality)
    url = upload_to_s3(ss, config)
    os.remove(ss)
    if not args.no_clipboard:
        copy_to_clipboard(url)
        notification = Notify.Notification.new("s3scrot","Screenshot URL copied to clipboard","network-transmit")
        notification.show()
    if args.open_browser:
        webbrowser.open(url)
    if args.print_url:
        print(url)
        

if __name__ == "__main__":
    main()
