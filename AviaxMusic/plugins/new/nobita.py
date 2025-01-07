import re
import random
from difflib import SequenceMatcher
from pyrogram import Client, filters
from pyrogram.types import Message
from config import OWNER_ID
from AviaxMusic import app
from AviaxMusic.core.mongo import mongodb
from AviaxMusic.utils.decorators import AdminRightsCheck
import asyncio

from pyrogram.enums import ChatAction


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

















# Chatbot Module
@app.on_message(filters.text & (filters.group | filters.private))
async def reply_text(client, message):
    chat_id = message.chat.id
    data = await nobita.find_one({"usertext": message.text})
    if data:
        bottexts = data["bottexts"]
        await message.reply_chat_action(ChatAction.TYPING)
        await asyncio.sleep(1)  # 3 second ka delay
        if isinstance(bottexts, list):
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
        similar_text_list = []
        async for doc in similar_text:
            similar_text_list.append(doc)
        for text in similar_text_list:
            similarity = SequenceMatcher(None, message.text.lower(), text["usertext"].lower()).ratio()
            if similarity > 0.6:
                bottexts = text["bottexts"]
                await message.reply_chat_action(ChatAction.TYPING)
                await asyncio.sleep(1)  # 3 second ka delay
                if isinstance(bottexts, list):
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
            tagged_text_list = []
            async for doc in tagged_text:
                tagged_text_list.append(doc)
            for text in tagged_text_list:
                if re.search(text["usertext"].lower(), message.text.lower()):
                    bottexts = text["bottexts"]
                    await message.reply_chat_action(ChatAction.TYPING)
                    await asyncio.sleep(1)  # 3 second ka delay
                    if isinstance(bottexts, list):
                        await message.reply(random.choice(bottexts))
                    else:
                        await message.reply(bottexts)
                    break