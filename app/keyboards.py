from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

remove_menu = ReplyKeyboardRemove()

# Registratsiyadan o'tgan foydalanuvchilar ko'radigan menyu
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Mening ma'lumotlarim")],
        [KeyboardButton(text="Kino qidirish 🎬")]
    ],
    resize_keyboard=True
)

# Telefon raqam olish tugmasi (O'zingiz yozgan kod)
phone_number = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Telefon raqamni yuborish", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)





