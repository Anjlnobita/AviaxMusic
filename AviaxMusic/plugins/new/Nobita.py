import re
import random
from difflib import SequenceMatcher
from pyrogram import Client, filters
from pyrogram.types import Message
from config import OWNER_ID
from AviaxMusic import app
from AviaxMusic.core.mongo import mongodb
from config import OWNER_ID
from AviaxMusic.utils.decorators import AdminRightsCheck



meow = mongodb.meow
nobita = mongodb.nobita



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
    usertext = text  # Add this line to define usertext
    data = await nobita.find_one({"usertext": usertext})
    if data:
        bottexts = ", ".join(data['bottexts'])
        await message.reply(f"Delete text: '{usertext}' and reply: '{bottexts}'")
        await nobita.delete_one({"usertext": usertext})
        # Delete bot text from MongoDB
        for bot_text in data['bottexts']:
            await nobita.delete_one({"bottext": bot_text})
        await message.reply(f"Save text '{usertext}' and reply '{bottexts}' reply text deleted!")
    else:
        await message.reply("Data not found!")





@app.on_message(
    filters.command("chatbot")
    & (filters.group | filters.private)
    & ~filters.forwarded
    & ~filters.via_bot
)
@AdminRightsCheck
async def toggle_chatbot(client, message):
    chat_id = message.chat.id
    data = meow.find_one({"chat_id": chat_id})
    if data:
        if data["chatbot_status"] == "enabled":
            meow.update_one({"chat_id": chat_id}, {"$set": {"chatbot_status": "disabled"}})
            await message.reply("Chatbot disabled!")
        else:
            meow.update_one({"chat_id": chat_id}, {"$set": {"chatbot_status": "enabled"}})
            await message.reply("Chatbot enabled!")
    else:
        meow.insert_one({"chat_id": chat_id, "chatbot_status": "enabled"})
        await message.reply("Chatbot enabled!")

# Chatbot Module
@app.on_message(filters.text & (filters.group | filters.private))
async def reply_text(client, message):
    chat_id = message.chat.id
    data = meow.find_one({"chat_id": chat_id})
    if data and data["chatbot_status"] == "enabled":
        # Find matching text in MongoDB
        data = await nobita.find_one({"usertext": message.text})
        if data:
            bottexts = data["bottexts"]
            await message.chat.send_typing()  # Typing action
            if ", " in bottexts:
                bottexts = bottexts.split(", ")
                await message.reply(random.choice(bottexts))
            else:
                await message.reply(bottexts)
        else:
            # Check for similar text
            pipeline = [
                {"$match": {"usertext": {"$regex": message.text.lower(), "$options": "i"}}},
                {"$sort": {"usertext": 1}}
            ]
            similar_text = nobita.aggregate(pipeline)
            for text in similar_text:
                similarity = SequenceMatcher(None, message.text.lower(), text["usertext"].lower()).ratio()
                if similarity > 0.6:
                    bottexts = text["bottexts"]
                    await message.chat.send_typing()  # Typing action
                    if ", " in bottexts:
                        bottexts = bottexts.split(", ")
                        await message.reply(random.choice(bottexts))
                    else:
                        await message.reply(bottexts)
                    break
            else:
                # Check for tagged reply
                pipeline = [
                    {"$match": {"usertext": {"$regex": message.text.lower(), "$options": "i"}}},
                    {"$sort": {"usertext": 1}}
                ]
                tagged_text = nobita.aggregate(pipeline)
                for text in tagged_text:
                    if re.search(text["usertext"].lower(), message.text.lower()):
                        bottexts = text["bottexts"]
                        await message.chat.send_typing()  # Typing action
                        if ", " in bottexts:
                            bottexts = bottexts.split(", ")
                            await message.reply(random.choice(bottexts))
                        else:
                            await message.reply(bottexts)
                        break