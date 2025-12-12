#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram import Client 
from bot import Bot
from config import *
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import *

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text=ABOUT_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
            [InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="start"), 
             InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data='close')
            ], [InlineKeyboardButton("• ᴅᴇᴠᴇʟᴏᴘᴇʀ •", url="https://t.me/Minato_Sencie")
               ]
              ]
            )
        )
   
       
    elif data == "start":
        await query.message.edit_text(
            text=START_MSG.format(first=query.from_user.first_name,mention=query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
            [InlineKeyboardButton("• ᴀʙᴏᴜᴛ •", callback_data="about"), 
             InlineKeyboardButton("• ʜᴇʟᴘ •", callback_data='help')],
             [InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data='close')],
             [InlineKeyboardButton("• ᴅᴇᴠᴇʟᴏᴘᴇʀ •", url="https://t.me/Minato_Sencie")]
              ]
            )
        )

    elif data == "help":
        await query.message.edit_text(
            text=HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
            [InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="start"), 
             InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data='close')
            ], [InlineKeyboardButton("• ᴅᴇᴠᴇʟᴏᴘᴇʀ •", url="https://t.me/Minato_Sencie")
               ]
              ]
            )
        )


        # ========================= PREMIUM ========================= #
    elif data == "premium":

        await query.message.delete()

        await client.send_photo(
            chat_id=query.message.chat.id,
            photo=QR_PIC,
            caption=(
                f"𝙃𝙚𝙮 𝙜𝙪𝙮𝙨...\n"
                f"𝙔𝙤𝙪 𝙬𝙖𝙣𝙩 𝙨𝙢𝙤𝙤𝙩𝙝 𝙚𝙭𝙥𝙚𝙧𝙞𝙚𝙣𝙘𝙚...\n"
                f"𝙉𝙤 𝙢𝙤𝙧𝙚 𝙩𝙤𝙠𝙚𝙣 𝙫𝙚𝙧𝙞𝙛𝙞𝙘𝙖𝙩𝙞𝙤𝙣...\n"
                f"𝘽𝙪𝙮 𝙤𝙪𝙧 𝙥𝙧𝙚𝙢𝙞𝙪𝙢 𝙨𝙪𝙧𝙫𝙞𝙘𝙚...\n"
                f"<blockquote>🎖️ ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʟᴀɴꜱ</blockquote>\n"
                f"<b>◉ 7 ᴅᴀʏꜱ   :- {PRICE1}\n</b>"
                f"<b>◉ 1 ᴍᴏɴᴛʜ  :- {PRICE2}\n</b>"
                f"<b>◉ 3 ᴍᴏɴᴛʜ  :- {PRICE3}\n</b>"
                f"<b>◉ 6 ᴍᴏɴᴛʜ  :- {PRICE4}\n</b>"
                f"<b>◉ 1 ʏᴇᴀʀ   :- {PRICE5}\n</b>"
                f"•─────•─────────•─────•\n"
                f"𝘿𝙢 𝙢𝙚:- <a href='https://t.me/Minato_Sencie'>Cʟɪᴄᴋ ʜᴇʀᴇ</a>"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⏤͟͞ 𝙈𝙞𝙣𝙖𝙩𝙤ˢᵉⁿᶜᶦᵉ",
                            url=SCREENSHOT_URL,
                        )
                    ],
                    [InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data="close")],
                ]
            ),
        )
        
        
    
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif data.startswith("rfs_ch_"):
        cid = int(data.split("_")[2])
        try:
            chat = await client.get_chat(cid)
            mode = await db.get_channel_mode(cid)
            status = "🟢 ᴏɴ" if mode == "on" else "🔴 ᴏғғ"
            new_mode = "ᴏғғ" if mode == "on" else "on"
            buttons = [
                [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
                [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
            ]
            await query.message.edit_text(
                f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception:
            await query.answer("Failed to fetch channel info", show_alert=True)

    elif data.startswith("rfs_toggle_"):
        cid, action = data.split("_")[2:]
        cid = int(cid)
        mode = "on" if action == "on" else "off"

        await db.set_channel_mode(cid, mode)
        await query.answer(f"Force-Sub set to {'ON' if mode == 'on' else 'OFF'}")

        # Refresh the same channel's mode view
        chat = await client.get_chat(cid)
        status = "🟢 ON" if mode == "on" else "🔴 OFF"
        new_mode = "off" if mode == "on" else "on"
        buttons = [
            [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
            [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
        ]
        await query.message.edit_text(
            f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data == "fsub_back":
        channels = await db.show_channels()
        buttons = []
        for cid in channels:
            try:
                chat = await client.get_chat(cid)
                mode = await db.get_channel_mode(cid)
                status = "🟢" if mode == "on" else "🔴"
                buttons.append([InlineKeyboardButton(f"{status} {chat.title}", callback_data=f"rfs_ch_{cid}")])
            except:
                continue

        await query.message.edit_text(
            "sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴛᴏɢɢʟᴇ ɪᴛs ғᴏʀᴄᴇ-sᴜʙ ᴍᴏᴅᴇ:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#
