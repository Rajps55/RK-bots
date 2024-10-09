from pyrogram import Client, filters
import time
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages, groups_broadcast_messages, temp, get_readable_time
import asyncio
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

lock = asyncio.Lock()

@Client.on_callback_query(filters.regex(r'^broadcast_cancel'))
async def broadcast_cancel(bot, query):
    _, ident = query.data.split("#")
    if ident == 'users':
        temp.USERS_CANCEL = True
        await query.message.edit("User broadcast cancellation requested...")
    elif ident == 'groups':
        temp.GROUPS_CANCEL = True
        await query.message.edit("Group broadcast cancellation requested...")

@Client.on_message(filters.command(["broadcast", "pin_broadcast"]) & filters.user(ADMINS) & filters.reply)
async def users_broadcast(bot, message):
    if lock.locked():
        return await message.reply('A broadcast is already in progress, please wait.')
    
    pin = message.command[0] == 'pin_broadcast'
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    b_sts = await message.reply_text('Broadcasting message to users...')
    start_time = time.time()
    total_users = await db.total_users_count()
    done, success, failed = 0, 0, 0

    async with lock:
        async for user in users:
            if temp.USERS_CANCEL:
                temp.USERS_CANCEL = False
                time_taken = get_readable_time(time.time() - start_time)
                await b_sts.edit(f"User broadcast canceled!\nTime: {time_taken}\nCompleted: <code>{done} / {total_users}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>")
                return

            sts = await broadcast_messages(int(user['id']), b_msg, pin)
            if sts == 'Success':
                success += 1
            elif sts == 'Error':
                failed += 1
            done += 1

            if done % 20 == 0:
                time_taken = get_readable_time(time.time() - start_time)
                btn = [[InlineKeyboardButton('CANCEL', callback_data=f'broadcast_cancel#users')]]
                await b_sts.edit(f"User broadcast in progress...\nTotal: <code>{total_users}</code>\nCompleted: <code>{done}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>\nTime: {time_taken}", reply_markup=InlineKeyboardMarkup(btn))
                
        time_taken = get_readable_time(time.time() - start_time)
        await b_sts.edit(f"User broadcast completed.\nTime: {time_taken}\nTotal: <code>{total_users}</code>\nCompleted: <code>{done}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>")

@Client.on_message(filters.command(["grp_broadcast", "pin_grp_broadcast"]) & filters.user(ADMINS) & filters.reply)
async def groups_broadcast(bot, message):
    if lock.locked():
        return await message.reply('A broadcast is already in progress, please wait.')
    
    pin = message.command[0] == 'pin_grp_broadcast'
    chats = await db.get_all_chats()
    b_msg = message.reply_to_message
    b_sts = await message.reply_text('Broadcasting message to groups...')
    start_time = time.time()
    total_chats = await db.total_chat_count()
    done, success, failed = 0, 0, 0

    async with lock:
        async for chat in chats:
            if temp.GROUPS_CANCEL:
                temp.GROUPS_CANCEL = False
                time_taken = get_readable_time(time.time() - start_time)
                await b_sts.edit(f"Group broadcast canceled!\nTime: {time_taken}\nCompleted: <code>{done} / {total_chats}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>")
                return

            sts = await groups_broadcast_messages(int(chat['id']), b_msg, pin)
            if sts == 'Success':
                success += 1
            elif sts == 'Error':
                failed += 1
            done += 1

            if done % 20 == 0:
                time_taken = get_readable_time(time.time() - start_time)
                btn = [[InlineKeyboardButton('CANCEL', callback_data=f'broadcast_cancel#groups')]]
                await b_sts.edit(f"Group broadcast in progress...\nTotal: <code>{total_chats}</code>\nCompleted: <code>{done}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>\nTime: {time_taken}", reply_markup=InlineKeyboardMarkup(btn))
                
        time_taken = get_readable_time(time.time() - start_time)
        await b_sts.edit(f"Group broadcast completed.\nTime: {time_taken}\nTotal: <code>{total_chats}</code>\nCompleted: <code>{done}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>")
