from aiogram import F, Router, html
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, FSInputFile

from app import keyboards as kb
import app.db_setup as db

router = Router()

KANAL_1_ID = -1001234567890
KANAL_2_ID = -1000987654321


class Registration(StatesGroup):
    first_name = State()
    last_name = State()
    phone_number = State()


async def check_subscription(bot, user_id):
    try:
        member1 = await bot.get_chat_member(chat_id=KANAL_1_ID, user_id=user_id)
        member2 = await bot.get_chat_member(chat_id=KANAL_2_ID, user_id=user_id)

        statuslar = ['member', 'administrator', 'creator']
        if member1.status in statuslar and member2.status in statuslar:
            return True
        return False
    except Exception:
        return False


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await db.check_user(message.from_user.id)
    if user:
        await message.answer(
            f"Assalomu alaykum, {html.bold(user[1])} {html.bold(user[2])}! Xush kelibsiz. 🍿\n\n"
            f"Kino ko'rish uchun uning {html.bold('kodini')} yuboring.",
            reply_markup=kb.main_menu
        )
    else:
        await message.answer("Botdan foydalanish uchun ro'yxatdan o'tishingiz kerak!\n\nIsmingizni kiriting:")
        await state.set_state(Registration.first_name)


@router.message(Registration.first_name)
async def first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text, tg_id=message.from_user.id)
    await message.answer("Familiyangizni kiriting:")
    await state.set_state(Registration.last_name)


@router.message(Registration.last_name)
async def last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=kb.phone_number)
    await state.set_state(Registration.phone_number)


@router.message(Registration.phone_number, F.contact)
async def phone(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.contact.phone_number)
    data = await state.get_data()

    await db.create_user(
        first_name=data["first_name"],
        last_name=data["last_name"],
        tg_id=data["tg_id"],
        phone_number=data["phone_number"]
    )
    await state.clear()
    await message.answer("Muvaffaqiyatli ro'yxatdan o'tdingiz! 🎉", reply_markup=kb.main_menu)


@router.message(Registration.phone_number)
async def wrong_phone(message: Message):
    await message.answer("Iltimos, telefon raqamni yuborish tugmasini bosing!", reply_markup=kb.phone_number)


@router.message(F.text == "Mening ma'lumotlarim")
async def info(message: Message, state: FSMContext):
    user = await db.check_user(message.from_user.id)
    if user:
        text = f"👤 <b>Ism:</b> {user[1]}\n👥 <b>Familiya:</b> {user[2]}\n📞 <b>Tel:</b> +{user[4]}"
        await message.answer(text, reply_markup=kb.main_menu)
    else:
        await message.answer("Siz ro'yxatdan o'tmagansiz")
        await state.set_state(Registration.first_name)


@router.message(F.text == "Kino qidirish 🎬")
async def search_info(message: Message):
    await message.answer("Kino kodini kiriting:")


@router.message(F.text == '77')
async def video1(message: Message):
    user = await db.check_user(message.from_user.id)
    if not user:
        await message.answer("Kino ko'rishdan oldin ro'yxatdan o'tishingiz shart!")
        return

    is_subscribed = await check_subscription(message.bot, message.from_user.id)
    if not is_subscribed:
        await message.answer("❌ Botdan foydalanish uchun homiy kanallarga obuna bo'lishingiz shart!",
                             reply_markup=kb.sub_keyboard)
        return

    video = FSInputFile('./videos/forsaj10.mp4')
    await message.answer_video(video=video, caption='Forsaj 10')


@router.message(F.text == '105')
async def video2(message: Message):
    user = await db.check_user(message.from_user.id)
    if not user:
        await message.answer("Kino ko'rishdan oldin ro'yxatdan o'tishingiz shart!")
        return

    is_subscribed = await check_subscription(message.bot, message.from_user.id)
    if not is_subscribed:
        await message.answer("❌ Botdan foydalanish uchun homiy kanallarga obuna bo'lishingiz shart!",
                             reply_markup=kb.sub_keyboard)
        return

    video = FSInputFile('./videos/avatar2.mp4')
    await message.answer_video(video=video, caption='Avatar 2')