from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
import aiohttp
from PIL import Image
from mindee_local.passport import process_passport
from mindee_local.car_docs import process_car_doc
import os
import traceback
from pdf_creation.pdf_creation import generate_insurance_pdf
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import re
from openai_local.openai_interaction import ask_openai


router = Router()

class waiting_for_data(StatesGroup):
    waiting_for_passport = State()
    waiting_for_car_doc_front = State()
    waiting_for_car_doc_back = State()
    waiting_for_data_confirmation = State()
    waiting_for_price_confirmation = State()
    fixing_data_choice = State()
    manual_data_entry = State()

confirm_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✅ Так"), KeyboardButton(text="❌ Ні")]],
    resize_keyboard=True
)


main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚗 Оформити страховку")],
        [KeyboardButton(text="🔄 Розпочати все знову"), KeyboardButton(text="❌ Скасувати")],
    ],
    resize_keyboard=True
)

input_method_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📸 Надіслати фото заново")],
        [KeyboardButton(text="✍️ Ввести дані вручну")],
    ],
    resize_keyboard=True
)

# Handler for the /start command. Greets the user, explains bot features, and shows the main menu.
@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Вітаю вас у боті *UKRSTRAKHGARANT*!\n\n"
        "Я допоможу вам швидко та зручно оформити автострахування онлайн 🚗💼\n\n"
        "Що я вмію:\n"
        "• Приймати фото ваших документів (паспорт, техпаспорт)\n"
        "• Автоматично розпізнавати дані\n"
        "• Показувати ціну та генерувати PDF-поліс\n"
        "• Відповідати на ваші питання щодо страхування\n\n"
        "Щоб розпочати, натисніть кнопку *«Оформити страховку»* \n\n"
        "ℹ️ Якщо виникає якесь питання можете задавати його прямо в чат.\n\n"
        "Бажаю вам безпечних доріг та гарного дня! 🌟",
        parse_mode="Markdown",
        reply_markup=main_menu_kb
    )

@router.message(F.text == "🚗 Оформити страховку")
async def start_insurance(message: Message, state: FSMContext):
    await message.answer("👋 Привіт! Надішли, будь ласка, фото паспорта власника авто 📷", reply_markup=main_menu_kb)
    await state.set_state(waiting_for_data.waiting_for_passport)

# Handler for restarting the process from the beginning when user clicks 'Restart'.
@router.message(F.text == "🔄 Розпочати все знову")
async def restart_all(message: Message, state: FSMContext):
    # Clears all state and prompts the user to start the insurance process from the beginning.
    await state.clear()
    await message.answer(
        "Ви можете почати оформлення автострахування знову. Надішліть, будь ласка, фото паспорта власника авто 📷",
        reply_markup=main_menu_kb  
    )
    await state.set_state(waiting_for_data.waiting_for_passport)

# Handler for canceling the current operation.
@router.message(F.text == "❌ Скасувати")
async def cancel(message: Message, state: FSMContext):
    # Cancels the current operation, clears state, and returns the user to the main menu.
    await state.clear()
    await message.answer("Операцію скасовано. Ви можете почати знову.", reply_markup=main_menu_kb)

# Handler for receiving the passport photo from the user.
@router.message(waiting_for_data.waiting_for_passport, F.photo)
async def handle_passport(message: Message, state: FSMContext):
    # Saves the passport photo and prompts for the front side of the car document.
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(passport_photo_id=file_id)
    await message.answer("✅ Паспорт отримано. Тепер надішли фото ПЕРЕДНЬОЇ сторони техпаспорта авто 📷",reply_markup=main_menu_kb)
    await state.set_state(waiting_for_data.waiting_for_car_doc_front)

# Handler for receiving the front side of the car document.
@router.message(waiting_for_data.waiting_for_car_doc_front, F.photo)
async def handle_car_doc_front(message: Message, state: FSMContext):
    # Saves the front side of the car document and prompts for the back side.
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(car_doc_front_photo_id=file_id)
    await message.answer("✅ Передня сторона техпаспорта отримана. Тепер надішли фото ЗАДНЬОЇ сторони техпаспорта авто 📷", reply_markup=main_menu_kb)
    await state.set_state(waiting_for_data.waiting_for_car_doc_back)

# Handler for receiving the back side of the car document, launching Mindee integration and showing extracted data.
@router.message(waiting_for_data.waiting_for_car_doc_back, F.photo)
async def handle_car_doc_back(message: Message, state: FSMContext):
    # Downloads all photos, creates a PDF, processes with Mindee, saves results, and asks the user to confirm extracted data.
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(car_doc_back_photo_id=file_id)

    data = await state.get_data()
    bot = message.bot

    passport_path = "passport.jpg"
    front_path = "front.jpg"
    back_path = "back.jpg"
    pdf_path = "car_doc_combined.pdf"

    async def download(file_id, path):
        file = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                with open(path, "wb") as f:
                    f.write(await resp.read())

    try:
        # download files
        await download(data["passport_photo_id"], passport_path)
        await download(data["car_doc_front_photo_id"], front_path)
        await download(data["car_doc_back_photo_id"], back_path)

        # create pdf for photos
        front = Image.open(front_path).convert("RGB")
        back = Image.open(back_path).convert("RGB")
        front.save(pdf_path, save_all=True, append_images=[back])

        # 🧠 Integrate mindee
        passport_result = process_passport(passport_path)
        car_doc_result = process_car_doc(pdf_path)

        await message.answer("Дякую за дані. Будь ласка зачекайте декілька секунд дані обробляються...")

        # save result in state 
        await state.update_data(passport_result=passport_result, car_doc_result=car_doc_result)

        # send to users for check
        await message.answer(
            f"📄 *Прізвище та ім'я власника авто:*\n`{passport_result['surname']} {passport_result['given_names']}`\n\n"
            f"🚗 *VIN-код авто:*\n`{car_doc_result['vin_code']}`\n\n"
            f"🚗 *Реєстраційний номер:*\n`{car_doc_result['registration_number']}`\n\n"
            f"🚗 *Марка, модель, колір:*\n`{car_doc_result['car_brand']} {car_doc_result['car_model']} {car_doc_result['color']}`\n\n"
            f"🚗 *Рік випуску:*\n`{int(float(car_doc_result['year_of_manufacture']))}`\n\n"
            "Все правильно?",
            reply_markup=confirm_kb,
            parse_mode="Markdown"
        )

        await state.set_state(waiting_for_data.waiting_for_data_confirmation)

    except Exception as e:
        print(f"Mindee error: {e}")
        traceback.print_exc()
        await message.answer("❌ Помилка під час обробки документів. Спробуй ще раз або звернись до підтримки.", reply_markup=main_menu_kb)

    finally:
        for path in [passport_path, front_path, back_path, pdf_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass


# Handler for confirming the extracted data and moving to price confirmation.
@router.message(waiting_for_data.waiting_for_data_confirmation, F.text.lower() == "✅ так")
async def confirmed(message: Message, state: FSMContext):
    # User confirms the extracted data; proceed to price confirmation step.
    await message.answer(
        "✅ Дані підтверджено.\n\n"
        "💵 Вартість автострахування — *100 USD*.\n"
        "Ви згодні з ціною?",
        reply_markup=confirm_kb,
        parse_mode="Markdown"
    )
    await state.set_state(waiting_for_data.waiting_for_price_confirmation)
    
# Handler for when the user rejects the extracted data and chooses how to correct it.
@router.message(waiting_for_data.waiting_for_data_confirmation, F.text.lower() == "❌ ні")
async def rejected(message: Message, state: FSMContext):
    # User rejects the extracted data; offer to re-upload photos or enter data manually.
    await message.answer(
        "Як ви хочете виправити дані?",
        reply_markup=input_method_kb
    )
    await state.set_state(waiting_for_data.fixing_data_choice)

# Handler for when the user chooses to re-upload photos to correct data.
@router.message(waiting_for_data.fixing_data_choice, F.text == "📸 Надіслати фото заново")
async def fix_by_photos(message: Message, state: FSMContext):
    # User chooses to re-upload photos; restart from passport photo step.
    await message.answer("Окей, надішліть фото паспорта ще раз.", reply_markup=main_menu_kb)
    await state.set_state(waiting_for_data.waiting_for_passport)

router.message(waiting_for_data.waiting_for_passport)

@router.message(waiting_for_data.fixing_data_choice, F.text == "✍️ Ввести дані вручну")
async def manual_input(message: Message, state: FSMContext):
    template = (
        "Будь ласка, введіть дані у наступному форматі:\n\n"
        "Прізвище та ім'я: Іваненко Іван\n"
        "VIN: WVWZZZ1JZXW000000\n"
        "Реєстраційний номер: АА1234ВС\n"
        "Марка: Volkswagen\n"
        "Модель: Passat\n"
        "Колір: Чорний\n"
        "Рік випуску: 2016"
    )
    await message.answer(template, reply_markup=ReplyKeyboardRemove())
    await state.set_state(waiting_for_data.manual_data_entry)


@router.message(waiting_for_data.manual_data_entry)
async def parse_manual_data(message: Message, state: FSMContext):
    text = message.text

    try:
        surname_and_name = re.search(r"Прізвище та ім'я:\s*(.+)", text).group(1)
        vin = re.search(r"VIN:\s*(.+)", text).group(1)
        reg_num = re.search(r"Реєстраційний номер:\s*(.+)", text).group(1)
        brand = re.search(r"Марка:\s*(.+)", text).group(1)
        model = re.search(r"Модель:\s*(.+)", text).group(1)
        color = re.search(r"Колір:\s*(.+)", text).group(1)
        year = int(re.search(r"Рік випуску:\s*(\d{4})", text).group(1))

        # Розділяємо прізвище і ім’я
        split_name = surname_and_name.strip().split(" ", 1)
        surname = split_name[0]
        given_names = split_name[1] if len(split_name) > 1 else ""

        await state.update_data(
            passport_result={
                "surname": surname,
                "given_names": given_names,
            },
            car_doc_result={
                "vin_code": vin,
                "registration_number": reg_num,
                "car_brand": brand,
                "car_model": model,
                "color": color,
                "year_of_manufacture": year,
            }
        )

        confirm_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="✅ Так"), KeyboardButton(text="❌ Ні")]],
            resize_keyboard=True
        )

        await message.answer(
            f"📄 *Прізвище та ім'я власника авто:*\n`{surname} {given_names}`\n\n"
            f"🚗 *VIN-код авто:*\n`{vin}`\n\n"
            f"🚗 *Реєстраційний номер:*\n`{reg_num}`\n\n"
            f"🚗 *Марка, модель, колір:*\n`{brand} {model} {color}`\n\n"
            f"🚗 *Рік випуску:*\n`{year}`\n\n"
            "Все правильно?",
            reply_markup=confirm_kb,
            parse_mode="Markdown"
        )

        await state.set_state(waiting_for_data.waiting_for_price_confirmation)

    except Exception as e:
        await message.answer(
            "⚠️ Дані не вдалося розпізнати. Перевірте правильність формату. "
            "Кожне поле має бути на окремому рядку згідно з шаблоном.", reply_markup=input_method_kb)


@router.message(waiting_for_data.waiting_for_price_confirmation, F.text.lower() == "✅ так")
async def price_accepted(message: Message, state: FSMContext):
    data = await state.get_data()
    passport_result = data.get("passport_result")
    car_doc_result = data.get("car_doc_result")

    await message.answer("🧾 Чудово! Зараз надішлю вам pdf-файл вашої страхівки")

    pdf_path = generate_insurance_pdf(passport_result, car_doc_result, price=100)
    input_file = FSInputFile(path=pdf_path, filename="Поліс_страхування.pdf")
    await message.answer_document(input_file, caption="Ось ваша страхівка 📄")

    # Delete the file after sending
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    await state.clear()



@router.message(waiting_for_data.waiting_for_price_confirmation, F.text.lower() == "❌ ні")
async def price_rejected(message: Message, state: FSMContext):
    await message.answer(
        "😔 Вибачте, але ціна *100 USD* — фіксована і не підлягає зміні.\n"
        "Якщо зміните думку — я завжди тут!",
        parse_mode="Markdown",
        reply_markup= main_menu_kb
    )
    await state.clear()

@router.message(F.text)
async def handle_text(message: Message):
    user_input = message.text

    try:
        response = await ask_openai(user_input)
        await message.answer(response,reply_markup= main_menu_kb)
    except Exception as e:
        print(f"OpenAI error: {e}")
        traceback.print_exc()
        await message.answer("⚠️ Не вдалося обробити ваше повідомлення. Спробуйте пізніше.", reply_markup=main_menu_kb)