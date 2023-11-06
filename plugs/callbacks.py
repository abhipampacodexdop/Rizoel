import pyqrcode, os, sys, pytz, random
from pyrogram import filters, Client
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from database import users
from . import cancel, get_stats, seller_stats
from .seller import *
from .start import *

a_chat = -1001542886535 #logs
back_button = [[InlineKeyboardButton("⌫", callback_data="back")]]

menu_buttons = [
  [
    InlineKeyboardButton("Buy Ind OTP", callback_data="purchase:ind")
  ],
  [
    InlineKeyboardButton("Buy Other OTP", callback_data="purchase:other")
  ],
  [
    InlineKeyboardButton("Deposit funds 🏦", callback_data="deposit"),
    InlineKeyboardButton("Check stats 📈", callback_data="stats")
  ],
]

async def get_amount(RiZoeL: Client, message: Message):
   chat = message.chat
   amount = await RiZoeL.ask(chat.id, "💲 **Share the amount of deposit \n\nMinimum deposit ₹16 or else wouldn't be added**", filters.text, timeout=300)
   if await cancel(amount):
      return "cancel"
   elif amount.text.isnumeric():
      if int(amount.text) >= 16:
         if int(int(amount.text) / 16) <= int(sess.count()):
            return int(amount.text)
         else:
            await amount.reply(f"**Sorry! Currently only {sess.count()} IDs in stock, so you can add upto ₹{int(sess.count()) * 16} only.**")
            return await get_amount(RiZoeL, message)
      else:
         await amount.reply("❗Minimum amount ₹16")
         return await get_amount(RiZoeL, message)
   else:
      await amount.reply("⚠️ Amount should be in Numbers! E.g 100")
      return await get_amount(RiZoeL, message)

async def get_ss(RiZoeL, m, amount):
   proof = await RiZoeL.ask(m.chat.id, f"💳 **Pay ₹{amount} on given QR code! and share screenshot!**", timeout=300)
   if proof.photo:
      return proof
   else:
      if await cancel(proof):
         return "cancel"
      else:
         await proof.reply("**Please share screenshot, or send /cancel to cancel the process**")
         return await get_ss(RiZoeL, m, amount)

async def add_fundings(RiZoeL: Client, message: Message):
   chat = message.chat
   kolkata_timezone = pytz.timezone("Asia/Kolkata")
   current_time = pytz.utc.localize(message.date).astimezone(kolkata_timezone).time()
   # Check if it's within active hours or sleeping hours
   if 23 < current_time.hour or current_time.hour < 9:
      await RiZoeL.send_message(chat.id, "**Sorry it's sleep time! You cannot add/deposit funds between 11PM to 09AM, because Team is Off**")
      return 
   user = await RiZoeL.get_users(chat.id)
   amount = await get_amount(RiZoeL, message)
   if amount == "cancel":
      return
   hue = await RiZoeL.send_message(user.id, "wait generating QR Code...")
   upi = random.choice(['', ''])
   s = str(f"upi://pay?pa={upi}&pn=Gurpreet Singh&am={amount}")
   qrname = str(chat.id)
   qrcode = pyqrcode.create(s)
   qrcode.png(qrname + '.png', scale=6)
   img = qrname + '.png'
   await RiZoeL.send_photo(
             chat.id,
             img,
             caption="**SCAN and PAY** 🧾")
   await hue.delete()
   proof = await get_ss(RiZoeL, message, amount)
   if proof == "cancel":
      return 
   logs = "**New Deposit!** \n\n"
   logs += f"by user: {user.mention} \n"
   logs += f"Amount: ₹{amount} \n"
   log_buttons = [
                  [
                  InlineKeyboardButton("Approve", callback_data=f"pay:a:{user.id}:{amount}")
                  ],
                  [
                  InlineKeyboardButton("R - SS", callback_data=f"pay:r:ss:{user.id}:{amount}"),
                  InlineKeyboardButton("R - Cont", callback_data=f"pay:r:cont:{user.id}:{amount}")
                  ],
                  ]
   await RiZoeL.send_photo(
               a_chat,
               proof.photo.file_id,
               caption=logs,
               reply_markup=InlineKeyboardMarkup(log_buttons))
   await proof.reply("**☑️ Screenshot and amount submitted to Team! Wait for approval**")

async def get_upi_qr(RiZoeL: Client, message: Message):
   chat = message.chat
   method = await RiZoeL.ask(chat.id, "📤 **Please Share QR Code pic or UPI!**", timeout=300)
   if await cancel(method):
      return
   if method.text:
     if "@" in method.text:
        return method.text, "upi"
     else:
        return await get_upi_qr(RiZoeL, message)
   elif method.photo:
     return method.photo.file_id, "qr"
   else:
     return await get_upi_qr(RiZoeL, message)

async def get_with_amount(RiZoeL: Client, message: Message):
   chat = message.chat
   check = sellers.check(chat.id)
   if int(check.amount) == 0:
      return "no-funds" 
   amount = await RiZoeL.ask(chat.id, "💳 **Share the amount of deposit \n\nMinimum withdraw ₹10**", filters.text, timeout=300)
   if await cancel(amount):
      return
   if amount.text.isnumeric():
      if int(amount.text) > 9:
         if int(check.amount) > int(amount.text) or int(check.refer) == int(amount.text):
            return int(amount.text)
         else:
            return "no-funds"
      else:
         await amount.reply("⚠️Minimum amount ₹10")
         return await get_amount(RiZoeL, message)
   else:
      await amount.reply("⚠️Amount should be in Numbers! E.g 100")
      return await get_with_amount(RiZoeL, message)

async def withdraw_query(RiZoeL: Client, message: Message):
   amount = await get_with_amount(RiZoeL, message)
   if amount == "no-funds":
      await RiZoeL.send_message(message.chat.id, "**You don't have enough refer funds!**")
      return
   pay, type = await get_upi_qr(RiZoeL, message)
   logs = "**Withdraw request!** \n\n"
   logs += f"by user: {message.from_user.mention} \n"
   logs += f"Amount: ₹{amount} \n"
   log_buttons = [
                  [InlineKeyboardButton("Done ✅", callback_data=f"with:a:{message.chat.id}:{amount}"),
                  InlineKeyboardButton("Reject", callback_data=f"with:r:{message.chat.id}:{amount}")],
                  ]
   if type == "upi":
      logs += f"UPI: `{pay}` \n"
      await RiZoeL.send_message(a_chat, logs, reply_markup=InlineKeyboardMarkup(log_buttons))
   else:
      await RiZoeL.send_photo(a_chat, pay, caption=logs, reply_markup=InlineKeyboardMarkup(log_buttons))
   await RiZoeL.send_message(message.chat.id, "☑️ **Your request sent ✓ please wait for team's approval!**")
   
@Client.on_callback_query()
async def callbacks(RiZoeL: Client, callback_query: CallbackQuery):
   query = callback_query.data.lower()
   message = callback_query.message
   user = callback_query.from_user

   if query == "back":
      await callback_query.edit_message_text(start_message.format(user.mention), reply_markup=InlineKeyboardMarkup(start_buttons))

   elif query.startswith("purchase"):
      que = query.split(":")
      if que[1] == "ind":
         if int(sess.count()) != 0:
            if int(users.check(user.id).deposit) > 15:
               await message.delete()
               await start_purchase(RiZoeL, message, que[1])
            else:
               await callback_query.edit_message_text(f"**Sorry!! You don't have enough funds! Your Deposits: ₹{users.check(user.id).deposit} \n\nKindly add funds!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Deposit funds 🏦", callback_data="deposit")]]))
          else:
            await callback_query.edit_message_text("**Opps sorry 😐 0 IDs in stock, try again later!**")
      else:
        if int(sess_oth.count()) != 0:
           if int(users.check(user.id).deposit) > 20:
              await message.delete()
              await start_purchase(RiZoeL, message, que[1])
          else:
              await callback_query.edit_message_text(f"**Sorry!! You don't have enough funds! Your Deposits: ₹{users.check(user.id).deposit} \n\nKindly add funds!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Deposit funds 🏦", callback_data="deposit")]]))
      else:
          await callback_query.edit_message_text("**Opps sorry 😐 0 IDs in stock, try again later!**")
   
   elif query == "menu":
      await callback_query.edit_message_text("**User Menu 💠**", reply_markup=InlineKeyboardMarkup(menu_buttons))

   elif query == "deposit":
      await message.delete()
      await add_fundings(RiZoeL, message)
   
   elif query == "stats":
      await callback_query.edit_message_text(get_stats(user.id), reply_markup=InlineKeyboardMarkup(back_button))

   elif query == "sstats":
      await callback_query.edit_message_text(seller_stats(user.id))
      
   elif query == "withdraw":
      await message.delete()
      await withdraw_query(RiZoeL, message)
      
   elif query.startswith("with"):
     que = query.split(':')
     if que[1] == "a":
        left_am = sellers.withdraw(que[2], que[3])
        await RiZoeL.send_message(que[2], f"✅ **Your request for withdraw of ₹{que[3]} has been approved and paid ✓** \n**Refer amount left: ₹{left_am} only** \n\nContact @TheRiZoeL if any question!")
        await message.delete()
        await RiZoeL.send_message(message.chat.id, f"**Accepted Withdrawal **✓ \n\nuser: {que[2]} \nAmonut: ₹{que[3]}")

     elif que[1] == "r":
        await RiZoeL.send_message(que[2], f"❌ **Your request for withdraw of ₹{que[3]} has been rejected! \nKindly Contact Us**!")
        await message.delete()
        await RiZoeL.send_message(message.chat.id, f"**Rejected Withdrawal **✓ \n\nuser: {que[2]} \nAmonut: ₹{que[3]}")

   elif query.startswith("pay"):
      que = query.split(':')
      if que[1] == "a":
         amount = users.update_deposit(int(que[2]), int(que[3]))
         await RiZoeL.send_message(que[2], f"**Your Request for ₹{que[3]} has been approved \n\nTotal amount/deposit: ₹{amount}**")
         await message.delete()
         await RiZoeL.send_message(message.chat.id, f"**Approved deposit** ✓ \n\nuser: {que[2]} \nAmount: ₹{amount}")
       
      elif que[1] == "r":    
         if que[2] == "ss":
            u = await RiZoeL.get_users(que[3])
            msg = await RiZoeL.send_photo(u.id, message.photo.file_id)
            await msg.reply(f"**Your deposit request for ₹{que[4]} has been rejected** \nReason: Screenshot invalid!")
            await message.delete()
            await RiZoeL.send_message(message.chat.id, f"**Reject deposit** ✓ \n\nuser: {que[3]} \nAmonut: ₹{que[4]}")
            proof = await RiZoeL.ask(u.id, f"**Pay ₹{que[4]} and please share valid screenshot!**", filters.photo, timeout=600)
            logs = "**Resend Screenshot of Deposit!** \n\n"
            logs += f"by user: {u.mention} \n"
            logs += f"Amount: ₹{que[4]} \n"
            log_buttons = [
                  [
                  InlineKeyboardButton("Approve", callback_data=f"pay:a:{u.id}:{que[4]}")
                  ],
                  [
                  InlineKeyboardButton("R - SS", callback_data=f"pay:r:ss:{u.id}:{que[4]}"),
                  #InlineKeyboardButton("R - Pay", callback_data=f"pay:r:p:{user.id}:{que[4]}"),
                  InlineKeyboardButton("R - Cont", callback_data=f"pay:r:cont:{u.id}:{que[4]}")
                  ],
                  ]
            await RiZoeL.send_photo(
               a_chat,
               proof.photo.file_id,
               caption=logs,
               reply_markup=InlineKeyboardMarkup(log_buttons))
            await proof.reply("**☑️ Screenshot and amount submitted to Team! Wait for approval**")
         elif que[2] == "cont":
            u = await RiZoeL.get_users(que[3])
            await RiZoeL.send_message(u.id, f"**⚠️ Something went wrong! Your request for ₹{que[4]} has been rejected by Team! please contact us. Support: @AceXSupport**")
            await message.delete()
            await RiZoeL.send_message(message.chat.id, f"**Approved deposit** ✓ \n\nuser: {que[3]} \nAmonut: ₹{que[4]}")
