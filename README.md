# s3scrot


A screenshot tool that automatically uploads to Amazon S3 and copies
the URL to the clipboard.

### Requirements

 * scrot
 * xclip
 * python-gobject

### Install

After ensuring dependencies are met, simply run:

    pip install s3scrot

### Usage

The first time you run s3scrot it will complain that you do not have a
config file. It will create a default one for you in your home
directory (~/.s3scrot). Edit this file according to the comments in
that file. You will need to enter your Amazon S3 bucket, and access
credentials. 

### Options

    usage: s3scrot [-h] [-n] [-c] [-b] [-p]
    
    s3scrot
    
    optional arguments:
      -h, --help            show this help message and exit
      -n, --non-interactive
                            Capture the whole screen, don't wait for mouse
                            selection
      -c, --no-clipboard    Do not copy URL to clipboard
      -b, --open-browser    Open browser to screenshot URL
      -p, --print-url       Print URL

Example:

#### To take a screenshot of just a portion of your screen:

    s3scrot

Then click on a window or click and drag across a rectangular region
of the screen you wish to capture.

#### An example using all the options:

    s3scrot -ncbpj -q 50

This will take a screenshot of the entire screen, does not copy the
URL to the clipboard, opens the browser to the URL, prints the URL,
and uses JPEG compression instead of PNG, at a quality level of 50.

### How I use this

I wanted an easy way to paste screenshots into IRC / hipchat. I use
[i3wm|http://i3wm.org/] and so I have some easy keybindings setup to
use s3scrot:

    bindsym $mod+Print exec "s3scrot -b"
    bindsym $mod+Shift+Print exec "s3scrot -bn"
 
That makes Alt+PrintScreen take a screenshot with selection, and
Alt+Shift+PrintScreen take a whole screen screenshot. Then it
opens my browser with the URL for preview, and I can paste the URL
directly into my chat client.

