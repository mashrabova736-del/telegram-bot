from aiogram import F, Router, html
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
import app.db_setup as db
import sqlite3
from app import keyboards as kb  # Klaviatura tugmalari uchun

router = Router()

# Foydalanuvchi ro'yxatdan o'tish holati
class Registration(StatesGroup):
    first_name = State()

# Admin FSM holatlari (Parol bosqichi qo'shildi)
class AdminStates(StatesGroup):
    waiting_for_password = State()  # Parol kutish holati
    waiting_for_code = State()
    waiting_for_name = State()
    waiting_for_genre = State()
    waiting_for_video = State()

# Doimiy admin paroli
ADMIN_PASSWORD = "billioner"

# ================= FOYDALANUVChI QISMI =================

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await db.check_user(message.from_user.id)
    if user:
        await message.answer(
            f"👋 Assalomu alaykum, {html.bold(user[1])}! Xush kelibsiz 🍿\n\n"
            f"🎬 Kino ko'rish uchun uning kodini yuboring.",
            reply_markup=kb.main_menu
        )
    else:
        await message.answer("🤖 Botdan foydalanish uchun ro'yxatdan o'tishingiz kerak!\n\n📝 Iltimos, ismingizni kiriting:")
        await state.set_state(Registration.first_name)

@router.message(Registration.first_name)
async def first_name(message: Message, state: FSMContext):
    name = message.text.strip()
    tg_id = message.from_user.id

    await db.create_user(
        first_name=name,
        last_name="",
        tg_id=tg_id,
        phone_number=""
    )
    await state.clear()
    await message.answer("🎉 Muvaffaqiyatli ro'yxatdan o'tdingiz!", reply_markup=kb.main_menu)

@router.message(F.text == "Mening ma'lumotlarim")
async def info(message: Message, state: FSMContext):
    user = await db.check_user(message.from_user.id)
    if user:
        text = f"👤 <b>Ism:</b> {user[1]}\n🆔 <b>Telegram ID:</b> {user[3]}"
        await message.answer(text, reply_markup=kb.main_menu)
    else:
        await message.answer("❌ Siz ro'yxatdan o'tmagansiz")
        await state.set_state(Registration.first_name)

@router.message(F.text == "Kino qidirish 🎬")
async def search_info(message: Message):
    await message.answer("🍿 Kino kodini kiriting:")

# ================= ADMIN PANEL QISMI (PAROL BILAN) =================

# 1. /admin yozilganda parol so'rash
@router.message(F.text == "/admin")
async def admin_panel(message: Message, state: FSMContext):
    await message.answer("🔒 Admin panelga kirish uchun maxfiy parolni kiriting:")
    await state.set_state(AdminStates.waiting_for_password)

# 2. Kiritilgan parolni tekshirish
@router.message(AdminStates.waiting_for_password)
async def check_admin_password(message: Message, state: FSMContext):
    if message.text.strip() == ADMIN_PASSWORD:
        await message.answer(
            "👨‍💻 <b>Parol to'g'ri! Admin panelga xush kelibsiz!</b>\n\n"
            "🆕 Yangi kino qo'shish uchun /addmovie buyrug'ini yuboring.\n"
            "📊 Bot statistikasini ko'rish uchun /stat buyrug'ini yuboring."
        )
        await state.clear()  # Parol to'g'ri bo'lsa holatdan chiqamiz
    else:
        await message.answer("❌ Noto'g'ri parol! Admin panelga kirish rad etildi.")
        await state.clear()  # Noto'g'ri bo'lsa ham holatni tozalaymiz

# Statistika ko'rish qismi
@router.message(F.text == "/stat")
async def show_bot_stats(message: Message):
    users_count = await db.get_users_count()
    await message.answer(f"📊 <b>Bot statistikasi:</b>\n\n👥 Umumiy foydalanuvchilar soni: <b>{users_count}</b> ta")

# 3. Kino qo'shishni boshlash
@router.message(F.text == "/addmovie")
async def add_movie_start(message: Message, state: FSMContext):
    await message.answer("🔢 Kino uchun <b>KOD</b> kiriting (Faqat son bo'lishi shart):")
    await state.set_state(AdminStates.waiting_for_code)

@router.message(AdminStates.waiting_for_code)
async def process_code(message: Message, state: FSMContext):
    code = message.text.strip()

    if not code.isdigit():
        await message.answer("⚠️ Xatolik! Kino kodi faqat <b>sonlardan</b> iborat bo'lishi kerak. Qayta kiriting:")
        return

    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM movies WHERE movie_code = ?", (code,))
    exists = cursor.fetchone()
    conn.close()

    if exists:
        await message.answer("⚠️ Bu kod band! Boshqa son kiriting:")
        return

    await state.update_data(movie_code=code)
    await message.answer("🎬 Endi kinoning <b>NOMINI</b> kiriting:")
    await state.set_state(AdminStates.waiting_for_name)

@router.message(AdminStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(movie_name=message.text.strip())
    await message.answer("🍿 Endi kinoning <b>JANRINI</b> kiriting (masalan: Jangari / Tarjima):")
    await state.set_state(AdminStates.waiting_for_genre)

@router.message(AdminStates.waiting_for_genre)
async def process_genre(message: Message, state: FSMContext):
    await state.update_data(movie_genre=message.text.strip())
    await message.answer("📹 Endi kinoning <b>O'ZINI (videoni)</b> yuboring:")
    await state.set_state(AdminStates.waiting_for_video)

@router.message(AdminStates.waiting_for_video)
async def process_video(message: Message, state: FSMContext):
    if not message.video:
        await message.answer("⚠️ Iltimos, faqat video fayl yuboring:")
        return

    data = await state.get_data()
    video_id = message.video.file_id

    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO movies (movie_code, movie_name, movie_genre, video_id)
        VALUES (?, ?, ?, ?)
    """, (data["movie_code"], data["movie_name"], data["movie_genre"], video_id))
    conn.commit()
    conn.close()

    await message.answer(
        f"✅ <b>Kino muvaffaqiyatli bazaga qo'shildi!</b>\n\n"
        f"🔑 Kod: {data['movie_code']}\n"
        f"🎥 Nomi: {data['movie_name']}\n"
        f"🍿 Janr: {data['movie_genre']}"
    )
    await state.clear()

# ================= DINAMIK KINO QIDIRISh =================

@router.message(F.text)
async def search_movie(message: Message):
    user = await db.check_user(message.from_user.id)
    if not user:
        await message.answer("⚠️ Kino ko'rishdan oldin ro'yxatdan o'tishingiz shart!")
        return

    movie = await db.get_movie(message.text.strip())
    
    if movie:
        caption_text = (
            f"🔑 <b>Kino kodi:</b> {message.text.strip()}\n\n"
            f"🎬 <b>Nomi:</b> {movie[0]}\n"
            f"🍿 <b>Janr:</b> {movie[2]}\n\n"
            f"✨ <i>Yoqimli tomosha tilaymiz!</i>"
        )
        await message.answer_video(video=movie[1], caption=caption_text, parse_mode="HTML")
    else:
        await message.answer("🔍 Kechirasiz, bu kod bilan hech qanday kino topilmadi. Qayta tekshirib ko'ring!")
