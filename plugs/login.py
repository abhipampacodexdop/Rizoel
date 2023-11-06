import random
from asyncio import TimeoutError
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from database import sess, sellers, sess_oth
from . import cancel as cancelled

DB_CHAT = -1001860306402 #logs
A_CHAT = -1001542886535 #DB

API_LIST = [
  '4014305 b0cb9e17b2b8bcde3be7161c8bfa6013',
  '28124597 7d71ada2c2b74ed53cc1b5ad829b5277',
  '3147700 e660ea4d20e70a3897aa8cf3a6dc60af',
  '18405415 65a8e3ad64aee6e570d73c02638bc6bf',
  '4487418 3a4aaa8e7e20a071667813226cb45564',
]

def get_api():
  a = random.choice(API_LIST)
  api = a.split(' ')
  return api[0], api[1]

async def sub_proc(client):
    try:
       await client.join_chat("")
    except Exception:
       pass
    try:
       await client.update_profile(first_name="", bio="")
    except Exception:
       pass 

@Client.on_message(filters.private & filters.command(['login', 'save', 'sell']))
async def generate_session(bot: Client, msg: Message):
    chat = msg.chat
    user_id = chat.id
    api_id, api_hash = get_api()
    if not sellers.check(user_id):
       await msg.reply("**Take access from team! Click on contact button!**")
       return
    phone_number_msg = await bot.ask(user_id, "Now please send `PHONE_NUMBER` along with the country code. \nExample : `+91876543210`", filters=filters.text)
    if await cancelled(phone_number_msg):
        return
    if phone_number_msg.text.startswith("+"):
       phone_number = phone_number_msg.text
    else:
       await phone_number_msg.reply("No. must starts with +!")
       return
    await msg.reply("Sending OTP...")
    client = Client(name="user", api_id=api_id, api_hash=api_hash, in_memory=True)
    await client.connect()
    try:
        code = await client.send_code(phone_number)
    except PhoneNumberInvalid:
        await msg.reply('`PHONE_NUMBER` is invalid. Please restart the prosess...')
        return
    try:
        phone_code_msg = await bot.ask(user_id, "Please check for an OTP in official telegram account. If you got it, send OTP here after reading the below format. \nIf OTP is `12345`, **please send it as** `1 2 3 4 5`.", filters=filters.text, timeout=600)
        if await cancelled(phone_code_msg):
           return
    except TimeoutError:
        await msg.reply('Time limit reached of 10 minutes. Please restart the prosess...')
        return
    phone_code = phone_code_msg.text.replace(" ", "")
    try:
       await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
       await msg.reply('OTP is invalid. Please restart the prosess...')
       return
    except PhoneCodeExpired:
       await msg.reply('OTP is expired.  Please restart the prosess...')
       return
    except SessionPasswordNeeded:
       try:
          two_step_msg = await bot.ask(user_id, 'Your account has enabled two-step verification. Please provide the password.', filters=filters.text, timeout=300)
       except exceptions.TimeoutError:
          await msg.reply('Time limit reached of 5 minutes. Please restart the prosess...')
          return
       try:
          password = two_step_msg.text
          await client.check_password(password=password)
       except PasswordHashInvalid:
          await two_step_msg.reply('Invalid Password Provided. Please restart the prosess...', quote=True)
          return
    wm = await bot.send_message(chat.id, "**Saving ID in database...**")
    await sub_proc(client)
    string_session = await client.export_session_string()
    hm = await bot.send_message(DB_CHAT, f'{string_session} {phone_number}')
    if phone_number.startswith("+91"):
       sess.save(hm.id, chat.id)
    else:
       sess_oth.save(hm.id, chat.id) 
    sellers.new(chat.id)
    await wm.edit(f"**Phone no. {phone_number} saved in database I'll update you on sell!**")
    await bot.send_message(, f"**ID on sell** \nLogin By: {chat.id} \nPhone no: {phone_number}")

async def get_and_save(bot, msg, no):
    user_id = msg.chat.id
    api_id, api_hash = get_api()
    await msg.reply(f"**Sending OTP on {no}**")
    client = Client(name=f"user-{no}", api_id=api_id, api_hash=api_hash, in_memory=True)
    await client.connect()
    try:
        code = await client.send_code(no)
        try:
           phone_code_msg = await bot.ask(user_id, "Please check for an OTP in official telegram account. If you got it, send OTP here after reading the below format. \nIf OTP is `12345`, **please send it as** `1 2 3 4 5`.", filters=filters.text, timeout=600)
           if await cancelled(phone_code_msg):
             return
        except TimeoutError:
           await msg.reply('Time limit reached of 10 minutes. Please restart the prosess...')
           return
        phone_code = phone_code_msg.text.replace(" ", "")
        try:
           await client.sign_in(no, code.phone_code_hash, phone_code)
        except PhoneCodeInvalid:
          await msg.reply('OTP is invalid. skiping this no.')
        except PhoneCodeExpired:
          await msg.reply('OTP is expired.  Please restart the prosess...')
          await get_and_save(bot, msg, no)
        except SessionPasswordNeeded:
          try:
             two_step_msg = await bot.ask(user_id, 'Your account has enabled two-step verification. Please provide the password.', filters=filters.text, timeout=300)
          except exceptions.TimeoutError:
             await msg.reply('Time limit reached of 5 minutes. Please restart the prosess...')
             return
          try:
             password = two_step_msg.text
             await client.check_password(password=password)
          except PasswordHashInvalid:
             await two_step_msg.reply('Invalid Password Provided. skiping thi no', quote=True)
        wm = await bot.send_message(msg.chat.id, "**Saving ID in database...**")
        await sub_proc(client)
        string_session = await client.export_session_string()
        hm = await bot.send_message(DB_CHAT, f'{string_session} {no}')
        sess.save(hm.id, msg.chat.id)
        sellers.new(msg.chat.id)
        await wm.edit(f"**Phone no. {no} saved in database I'll update you on sell!**")
        await bot.send_message(A_CHAT, f"**ID on sell** \nLogin By: {msg.chat.id} \nPhone no: {no}")
    except PhoneNumberInvalid:
        await msg.reply('{no} is invalid. skiping this no.')

@Client.on_message(filters.private & filters.command(['multi']))
async def multiple_sessions(bot: Client, m: Message):
    nums = await bot.ask(m.chat.id, "**Share all phone No.s space by space in one message!**")
    if await cancelled(nums):
       return
    num_list = list(nums.text.split(" "))
    await nums.reply("**starting process....**")
    for no in num_list:
       await get_and_save(bot, m, no)
    await m.reply("**All done**")
