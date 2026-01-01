import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ConversationHandler, 
    filters, ContextTypes
)

# Environment variables dan o'qish
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Sizning Google Forms havolangiz
GOOGLE_FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLScx_nMDO4PpanTSl_6iKgJen9pHiAk5J20-ZcJTOkri4BamuA/viewform"

# Loyiha yaratuvchilari
CREATORS = {
    "bird brain ghost": "Bird Brain Ghost",
    "from another period": "From Another Period"
}

# Asosiy menyu
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📚 Loyiha haqida", callback_data='about')],
        [InlineKeyboardButton("📅 Tadbirlar", callback_data='events')],
        [InlineKeyboardButton("🤝 Volonter bo'lish", callback_data='volunteer')],
        [InlineKeyboardButton("❓ Savol berish (AI)", callback_data='question')],
        [InlineKeyboardButton("🌐 Havolalar", callback_data='links')]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! 👋\n\n"
        "**MIS - Milliy Ilm Suhbati** rasmiy botiga xush kelibsiz!\n\n"
        "Iltimos, to'liq ism-familiyangizni kiriting:"
    )
    return 1

# Ismni qabul qilish
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text.strip().lower()
    context.user_data['name'] = update.message.text
    
    if user_name in CREATORS:
        creator_name = CREATORS[user_name]
        await update.message.reply_text(
            f"✨ **Tabriklaymiz, {creator_name}!** ✨\n\n"
            "Siz MIS loyihasining asoschilaridan birisiz! 🎉\n"
            "Bot sizning xizmatingizda!",
            reply_markup=main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            f"Rahmat, {update.message.text}! 👤\n\n"
            "Quyidagi menyudan kerakli bo'limni tanlang:",
            reply_markup=main_menu_keyboard()
        )
    return 2

# Callback handler
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'about':
        await about_project(query)
    elif query.data == 'events':
        await show_events(query)
    elif query.data == 'volunteer':
        await volunteer_form(query)
    elif query.data == 'question':
        await ask_question(query)
    elif query.data == 'links':
        await show_links(query)
    
    return 2

# Loyiha haqida
async def about_project(query):
    text = """🌟 **MIS - Milliy Ilm Suhbati** 🌟

**Nima bu MIS?**
MIS - O'zbek tilida ilmiy muloqot, tahlil va fikrlash madaniyatini rivojlantirish loyihasi.

**Maqsad:**
• O'zbek tilida ilmiy kontent
• Mustaqil fikrlashni o'rgatish
• Global ilmdan milliy til orqali foydalanish

**Asosiy faoliyat:**
📺 "Dildan Suhbat" - 20 daqiqalik tahlillar
📚 Telegram kanalda muntazam ma'lumotlar
🎤 Trend mavzularda muhokamalar

**Qoidalar:**
✅ Faqat toza o'zbek tili
✅ 15+ yosh auditoriya
✅ Har bir fikr hurmat bilan"""
    
    await query.edit_message_text(text=text, reply_markup=main_menu_keyboard(), parse_mode='Markdown')

# Tadbirlar
async def show_events(query):
    text = """📅 **Yaqindagi Tadbirlar:**

🎤 **Dildan Suhbat:**
• Mavzu: "Sun'iy Intellekt va Kelajak"
• Sana: 25.12.2025, 18:00
• Joy: Onlayn

📚 **Ilm Seminari:**
• Mavzu: "Ilmiy Maqola yozish"
• Sana: 28.12.2025, 17:00

🤝 **Volonter Uchrashuvi:**
• Sana: 30.12.2025, 19:00

📍 Barcha tadbirlar onlayn bo'lib o'tadi!"""
    
    await query.edit_message_text(text=text, reply_markup=main_menu_keyboard(), parse_mode='Markdown')

# Volonter forması
async def volunteer_form(query):
    text = f"""🤝 **Volonter Bo'lish**

MIS loyihasida faoliyat yuritish uchun quyidagi forma orqali ariza topshiring:

🔗 **Google Forms:**
{GOOGLE_FORM_LINK}

**Volonter vazifalari:**
• Kontent yaratish
• Tadbirlar tashkiloti
• SMM menejmenti
• Texnik yordam

Ariza topshirgandan so'ng 48 soat ichida javob olasiz."""

    keyboard = [
        [InlineKeyboardButton("📝 Formani to'ldirish", url=GOOGLE_FORM_LINK)],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='back')]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# Savol berish
async def ask_question(query):
    await query.edit_message_text(
        text="❓ **Savol berish**\n\nHar qanday savolingizni yozing. Men DeepSeek AI yordamida javob beraman.\n\nYozing...",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data='back')]])
    )
    return 3

# AI javob berish
async def handle_ai_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    
    # MIS haqida maxsus javoblar
    if any(word in question.lower() for word in ['mis', 'milliy', 'volonter', 'loyiha']):
        response = """🤖 **MIS haqida:**

MIS - Milliy Ilm Suhbati o'zbek tilida ilmiy platforma.

• Volonter bo'lish: Google Forms orqali
• Dildan Suhbat: Har yakshanba
• Kanal: @MilliyIlmSuhbati
• Sayt: https://mis-uz.github.io/loyihasi/

Batafsil: /start"""
    else:
        # DeepSeek API
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": question}],
                "max_tokens": 300
            }
            
            resp = requests.post("https://api.deepseek.com/v1/chat/completions", 
                               json=data, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                response = resp.json()['choices'][0]['message']['content']
            else:
                response = "⚠️ Kechirasiz, hozir javob bera olmayman."
        except:
            response = "❌ AI xizmati vaqtincha ishlamayapti."
    
    await update.message.reply_text(response, reply_markup=main_menu_keyboard())
    return 2

# Havolalar
async def show_links(query):
    text = """🔗 **Foydali Havolalar:**

🌐 **Rasmiy Sayt:**
https://mis-uz.github.io/loyihasi/

📢 **Telegram Kanal:**
https://t.me/MilliyIlmSuhbati

📝 **Volonter Formasi:**
https://docs.google.com/forms/d/e/1FAIpQLScx_nMDO4PpanTSl_6iKgJen9pHiAk5J20-ZcJTOkri4BamuA/viewform

📧 **Email:**
milliyilmsuhbati@gmail.com"""

    keyboard = [
        [InlineKeyboardButton("🌐 Sayt", url="https://mis-uz.github.io/loyihasi/")],
        [InlineKeyboardButton("📢 Kanal", url="https://t.me/MilliyIlmSuhbati")],
        [InlineKeyboardButton("📝 Forma", url=GOOGLE_FORM_LINK)],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='back')]
    ]
    
    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))

# Orqaga qaytish
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="Asosiy menyu:",
        reply_markup=main_menu_keyboard()
    )
    return 2

# Asosiy funksiya
def main():
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(filters.TEXT, get_name)],
            2: [CallbackQueryHandler(handle_callback)],
            3: [MessageHandler(filters.TEXT, handle_ai_question)]
        },
        fallbacks=[]
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(back_to_menu, pattern='^back$'))
    
    print("🤖 Bot ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()
