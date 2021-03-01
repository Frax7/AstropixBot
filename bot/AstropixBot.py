
import os
import schedule
import time
import json
import telegram
from datetime import date
from urllib.request import urlopen
from youtubeID import get_yt_video_id

def astropixbot():
    # Read secrets
    with open("secrets",'r') as secrets:
        lines = secrets.readlines()
        token = lines[0][:-1]
        chat_id = lines[1][:-1]
        api_key = lines[2]

    # Create the Bot object
    bot = telegram.Bot(token)

    # Pick today's page and today's link for JSON.
    today = date.today()
    today_link = 'http://apod.nasa.gov/apod/ap'+today.strftime("%y%m%d")+'.html'
    link = "https://api.nasa.gov/planetary/apod?api_key="+api_key+"&date="+today.strftime("%Y-%m-%d")

    with urlopen(link) as response:
        # .decode("utf-8") is for converting bytes into string.
        source = response.read().decode("utf-8")
        data = json.loads(source)

    # Picking all relevant information from the JSON.
    media_type = data["media_type"]
    url = data["url"]
    title = data["title"]

    # Diferenciate between image and video content
    if (media_type == "image"):
        # In case of image, will download the image and then send
        # it with a caption(title + today's link).
        
        # Start downloading the image.
        with open("image.jpeg",'wb') as imagefile:
            imagefile.write(urlopen(url).read())
        # Image downloaded.

        # Open and send the image with its caption.
        with open('image.jpeg', 'rb') as image:
            bot.send_photo(
                chat_id,
                image,
                caption = "<b>"+title+"</b> \n <a href='"+today_link+"'>Check the explanation.</a>",
                parse_mode='html')
        # Image sent.
        if os.path.exists('image.jpeg'):
            os.remove('image.jpeg')
        else:
            print("Error :: the file \'image.jpeg\' does not exist")

    elif (media_type == "video"):
        # In case of video, will download the thumbnail and then send
        # it with a caption ([VIDEO]title + video's link + today's link)
        
        # Use the script to get the youtube video ID.
        yt_video_id = get_yt_video_id(url)
        yt_thumbnail_link = "https://img.youtube.com/vi/"+yt_video_id+"/hqdefault.jpg"
        
        with open("image.jpg",'wb') as imagefile:
            imagefile.write(urlopen(yt_thumbnail_link).read())
        # Thumbnail downloaded.
    
        # Open and send the thumbnail with its caption.
        with open('image.jpg', 'rb') as image:
            bot.send_photo(
                chat_id,
                image,
                caption = "[VIDEO] <b>"+title+"</b>\n <a href='"+url+"'>Watch full video.</a>\n <a href='"+today_link+"'>Check the explanation.</a>",
                parse_mode='html')
        # Thumbnail sent.

# Every day at 9:00 astropixbot is called.
schedule.every().day.at("10:00").do(astropixbot)

# Loop so that the scheduling task keeps on running all time.
while True:
    # Check whether a scheduled task is pending to run or not
    schedule.run_pending()
    time.sleep(1) # it will refersh every second
