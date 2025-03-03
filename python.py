import os
import edge_tts
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from PyPDF2 import PdfReader

TOKEN = "7859740182:AAG5KjnsZ97qc6FyWXhP2uPt3-_27hmGlBY"  # Telegram bot tokenini kiriting

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Maksimal fayl hajmi (20MB)
MAX_FILE_SIZE = 20 * 1024 * 1024  

# Yuklab olingan fayllarni saqlash uchun papka
DOWNLOAD_DIR = "./downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_pdf(message: Message):
    """PDF faylni yuklab olish va ovozli faylga aylantirish"""
    
    # Fayl hajmini tekshirish
    if message.document.file_size > MAX_FILE_SIZE:
        await message.answer("❌ Fayl hajmi juda katta! Iltimos, 20MB dan kichik PDF yuboring.")
        return

    file_path = os.path.join(DOWNLOAD_DIR, message.document.file_name)
    
    # Faylni yuklab olish
    await message.document.download(destination_file=file_path)
    await message.answer("✅ PDF yuklab olindi. Matnni ovozga aylantirish jarayoni...")

    # PDF dan matn chiqarish
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        if not text.strip():
            await message.answer("❌ PDF ichida matn topilmadi.")
            return

        # Ovozga aylantirish (Edge TTS orqali)
        audio_path = file_path.replace(".pdf", ".mp3")
        voice = "uz-UZ-MadinaNeural"  # O‘zbek tili ovozi
        await text_to_speech(text, audio_path, voice)

        # Ovozli faylni yuborish
        with open(audio_path, "rb") as audio:
            await message.answer_audio(audio, caption="🔊 Matn ovozga aylandi!")

        # Fayllarni o‘chirish
        os.remove(file_path)
        os.remove(audio_path)

    except Exception as e:
        await message.answer(f"⚠ Xatolik yuz berdi: {e}")

async def text_to_speech(text, audio_path, voice="uz-UZ-MadinaNeural"):
    """Edge TTS orqali matnni ovozga aylantirish"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(audio_path)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
