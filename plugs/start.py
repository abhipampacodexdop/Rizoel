from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database import users, sellers
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden

@Client.on_message(filters.incoming & filters.private, group=-1)
async def must_join_channel(bot: Client, msg: Message):
    join_text = "**Must Join Channel and Support 🪄** \n\n"
    join_text += f"**⎓⎓⎓⎓⎓⎓⎓⎓⎓⎓⎓⎓⎓⎓** \n\n"
    try:
        try:
            await bot.get_chat_member("", msg.from_user.id)
        except UserNotParticipant:
            join_text += " **•) @** \n\n**"
            join_text += f"**⎓⎓⎓⎓⎓⎓⎓⎓⎓⎓⎓⎓⎓⎓** \n\n"
            join_text += "**Before using the bot**"
            try:
                await msg.reply()
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        print(f"I'm not admin in the bith chats !")

start_message = """
****
"""

start_buttons = [
  [
    InlineKeyboardButton("Menu 💠", callback_data="menu")
  ],
  [
    InlineKeyboardButton("Channel 📢", url=""),
    InlineKeyboardButton("Support 👥", url="")
  ],
]

panel_msg = """
**Welcome to sellers panel**

 - Please click below buttons to check your stats or withdraw your amount!
"""

panel_buttons = [
  [
    InlineKeyboardButton("Your stats 📊", callback_data="sstats"),
    InlineKeyboardButton("Withdraw 🔄", callback_data="withdraw")
  ],
  [
    InlineKeyboardButton("Support 👥", url="t.me/")
  ],
]

@Client.on_message(filters.private & filters.command(["start", "help", "buy"]))
async def start_msg(c, message):
  users.adduser(message.from_user.id)
  await message.reply(start_message.format(message.from_user.mention), reply_markup=InlineKeyboardMarkup(start_buttons))

@Client.on_message(filters.private & filters.command(["seller", "panel"]))
async def sellers_panel(_, message):
   if sellers.check(message.from_user.id):
      await message.reply(panel_msg, reply_markup=InlineKeyboardMarkup(panel_buttons))


