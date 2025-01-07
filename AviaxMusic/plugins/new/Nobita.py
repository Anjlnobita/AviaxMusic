from difflib import SequenceMatcher
import re
import random
from pyrogram import Client, filters
from AviaxMusic import app
from config import OWNER_ID
from AviaxMusic.core.mongo import mongodb

nobita = mongodb.nobi



@app.on_message(
    filters.command("tsave")
    & filters.user(OWNER_ID)
)
async def tsave(client, message):
    # Save data to MongoDB
    text = message.text.split(" ", 1)[1]
    usertext, bottexts = text.split(" - ")
    bottexts = bottexts.split(", ")
    nobita.insert_one({"usertext": usertext, "bottexts": bottexts})
    await message.reply("Data saved!")
    
    
    
@app.on_message(filters.command("del") & filters.user(OWNER_ID))
async def del_text(client, message):
    # Delete text from MongoDB
    text = message.text.split(" ", 1)[1]
    data = await nobita.find_one({"usertext": text})
    if data:
        reply_text = ", ".join(data['bottexts'])
        await message.reply(f"Delete text: '{text}' and reply: '{reply_text}'")
        await nobita.delete_one({"usertext": text})
        # Delete bot text from MongoDB
        for bot_text in data['bottexts']:
            await Nobita.delete_one({"bottext": bot_text})
        await message.reply(f"Save text '{text}' and reply '{reply_text}' reply text deleted!")
    else:
        await message.reply("Data not found!")