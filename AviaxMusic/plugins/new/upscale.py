from pyrogram import Client, filters
import requests
import os
from config import BANNED_USERS
from AviaxMusic import app






API_KEY = "AIzaSyCjNqSj0MQxicbVKiYqkqfTu5Trh3o7yIw"
UPSCALER_URL = "https://api.remini.ai/upscale"


@app.on_message(filters.command(["upscale"]) & filters.private & ~BANNED_USERS)
def upscale_image(client, message):
    if message.reply_to_message.photo:
        photo_file = message.reply_to_message.photo.file_id
        file_path = client.download_media(photo_file)
        
        with open(file_path, 'rb') as image_file:
            response = requests.post(UPSCALER_URL, files={'image': image_file}, headers={'Authorization': f'Bearer {API_KEY}'})
        
        if response.status_code == 200:
            upscale_image_data = response.content
            
            upscale_image_path = "upscaled_image.png"
            with open(upscale_image_path, 'wb') as upscale_image_file:
                upscale_image_file.write(upscale_image_data)
            
            client.send_photo(chat_id=message.chat.id, photo=upscale_image_path)
            os.remove(upscale_image_path)
        else:
            client.send_message(chat_id=message.chat.id, text="Failed to upscale the image.")
        
        os.remove(file_path)
    else:
        client.send_message(chat_id=message.chat.id, text="Please reply to an image to upscale.")
 