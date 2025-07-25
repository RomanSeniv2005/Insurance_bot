from reportlab.pdfgen import canvas 
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import date

def generate_insurance_pdf(passport_result: dict, car_doc_result: dict, price: int | float) -> str:
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    full_name = f"{passport_result.get('surname', '')} {passport_result.get('given_names', '')}".strip() or "Невідомо"
    vin_code = car_doc_result.get("vin_code", "Невідомо")
    registration_number = car_doc_result.get("registration_number", "Невідомо")
    car_brand = car_doc_result.get("car_brand", "Невідомо")
    car_model = car_doc_result.get("car_model", "")
    year = car_doc_result.get("year_of_manufacture", "Невідомо")

    try:
        year = str(int(float(year)))
    except:
        year = str(year)

    file_path = f"insurance_policies/Поліс_{full_name.replace(' ', '_')}.pdf"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    c = canvas.Canvas(file_path, pagesize=A4)
    c.setFont("DejaVuSans", 12)

    width, height = A4

    # 🏢 Логотип
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 50, height - 100, width=60, height=60, mask='auto')

    # 🏢 Назва компанії
    c.setFont("DejaVuSans", 18)
    c.drawCentredString(width / 2 + 30, height - 60, "ТОВ 'УКРСТРАХГАРАНТ'")
    c.setFont("DejaVuSans", 13)
    c.drawCentredString(width / 2 + 30, height - 80, "ПОЛІС СТРАХУВАННЯ АВТОТРАНСПОРТНОГО ЗАСОБУ")

    # 📄 Основна інформація
    data = [
        ["ПІБ власника:", full_name],
        ["VIN-код:", vin_code],
        ["Номерний знак:", registration_number],
        ["Марка та модель авто:", f"{car_brand} {car_model}".strip()],
        ["Рік випуску:", year],
        ["Оціночна вартість авто:", f"{price} USD"],
        ["Дата початку дії:", date.today().strftime("%d.%m.%Y")],
        ["Дата закінчення дії:", (date.today().replace(year=date.today().year + 1)).strftime("%d.%m.%Y")],
        ["Страхова сума:", f"{price} USD"],
        ["Тип страхування:", "КАСКО (всі ризики)"],
        ["Франшиза:", "0%"],
    ]

    table = Table(data, colWidths=[180, 360])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    table.wrapOn(c, 50, 400)
    table.drawOn(c, 50, height - 360)

    # 📜 Умови страхування
    text_y = height - 420 - (len(data) * 20)
    c.setFont("DejaVuSans", 11)
    c.drawString(50, text_y, "Умови страхування:")
    conditions = [
        "- Страховка діє на території України.",
        "- Виплата у разі ДТП, викрадення, стихійного лиха.",
        "- Виплати здійснюються протягом 10 робочих днів після подання заяви.",
        "- При втраті поліса його можна відновити за заявою власника.",
    ]
    y = text_y - 20
    for condition in conditions:
        c.drawString(60, y, condition)
        y -= 18

    # ✍️ Підпис і дата
    c.setFont("DejaVuSans", 12)
    c.drawString(50, y - 30, "Підпис страховика: ____________________")
    c.drawString(50, y - 50, "Дата оформлення: " + date.today().strftime("%d.%m.%Y"))

    c.save()
    return file_path
