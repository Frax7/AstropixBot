import datetime
import logging
import mimetypes

import Constants
import requests
from telegram import Update
from telegram.ext import (ApplicationBuilder, ContextTypes, MessageHandler,
                          filters)
from youtubeID import get_yt_video_id

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def get_todays_info() -> (dict, str):
    todays_date = datetime.datetime.today().strftime("%Y-%m-%d")
    response = requests.get(f"https://api.nasa.gov/planetary/apod?api_key={Constants.NASA_API_TOKEN}&date={todays_date}")
    todays_link = f'http://apod.nasa.gov/apod/ap{datetime.datetime.today().strftime("%y%m%d")}.html'
    return response.json(), todays_link

async def disclaimer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id != Constants.PERSONAL_CHAT_ID:
        await context.bot.send_message(chat_id=chat_id, text="This bot works only on @AstropixChannel\nFollow the channel so you don't miss any pic! 🤩")
    else:
        response = get_todays_info()
        await context.bot.send_message(chat_id=chat_id, text=update)
        await context.bot.send_message(chat_id=chat_id, text=response)
        await send_apod(context=context)

async def send_todays_image(image_url: str, caption: str, context: ContextTypes.DEFAULT_TYPE):
    mimetype, _ = mimetypes.guess_type(image_url)
    caption = f"📸 {caption}"
    if mimetype == 'image/gif':
        await context.bot.send_document(chat_id=Constants.CHANNEL_CHAT_ID, document=image_url, caption=caption, parse_mode="html")
    else:
        await context.bot.send_photo(chat_id=Constants.CHANNEL_CHAT_ID, photo=image_url, caption=caption, parse_mode="html")

async def send_todays_video(video_url: str, caption: str, context: ContextTypes.DEFAULT_TYPE):
    yt_video_id = get_yt_video_id(video_url)
    image_url = f"https://img.youtube.com/vi/{yt_video_id}/hqdefault.jpg"
    caption = f"<b>🎬 <a href='{video_url}'>[VIDEO]</a></b> {caption}"
    await context.bot.send_photo(chat_id=Constants.CHANNEL_CHAT_ID, photo=image_url, caption=caption, parse_mode='html')

async def send_apod(context: ContextTypes.DEFAULT_TYPE):
    response, todays_link = get_todays_info()
    media_type = response['media_type']
    caption = f"<b>{response['title']}</b>\n<a href='{todays_link}'>Check the explanation</a>"
    match media_type:
        case "image":
            await send_todays_image(image_url=response['hdurl'], caption=caption, context=context)
        case "video":
            await send_todays_video(video_url=response['url'], caption=caption, context=context)

def main():
    application = ApplicationBuilder().token(token=Constants.TOKEN).build()
    
    text_handler = MessageHandler(filters.ALL, disclaimer)
    application.add_handler(text_handler)

    time = datetime.time(8, 00, 00, 000000)
    application.job_queue.run_daily(callback=send_apod, time=time, chat_id=Constants.CHANNEL_CHAT_ID, name=str(Constants.CHANNEL_CHAT_ID))
    
    application.run_polling()

if __name__ == '__main__':
    main()