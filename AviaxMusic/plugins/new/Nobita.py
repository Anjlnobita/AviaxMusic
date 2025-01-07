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
    await message.reply(f"Data saved!{usertext} - {bottexts}")
    
    
    
@app.on_message(filters.command("del") & filters.user(OWNER_ID))
async def del_text(client, message):
    # Delete text from MongoDB
    text = message.text.split(" ", 1)[1]
    data = await nobita.find_one({"usertext": usertext})
    if data:
        reply_text = ", ".join(data['bottexts'])
        await message.reply(f"Delete text: '{usertext}' and reply: '{bottexts}'")
        await nobita.delete_one({"usertext": usertext})
        # Delete bot text from MongoDB
        for bottexts in data['bottexts']:
            await Nobita.delete_one({"bottexts": bottexts})
        await message.reply(f"Save text '{usertext}' and reply '{bottexts}' reply text deleted!")
    else:
        await message.reply("Data not found!")