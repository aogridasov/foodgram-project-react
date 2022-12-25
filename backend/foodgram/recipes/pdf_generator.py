import io

import reportlab
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# регистрируем кириллицу
reportlab.rl_config.TTFSearchPath.append(
    str(settings.BASE_DIR) + '/recipes/fonts'
)
pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))


def parse_data(data):
    parsed_data = []
    for key, value in data.items():
        pdf_string = [
            key.name,
            key.measurement_unit,
            value,
        ]
        parsed_data.append(pdf_string)
    return parsed_data


def generate(data):
    buffer = io.BytesIO()
    file = canvas.Canvas(buffer, pagesize=A4)

    file.setFont('FreeSans', 15, leading=None)
    file.drawString(200, 800, 'Foodgram by Anton Gridasov')
    file.line(0, 780, 1000, 780)
    file.drawString(200, 750, 'Список покупок:')

    parsed_data = parse_data(data)
    x = 100
    y = 660

    for string in parsed_data:
        file.setFont('FreeSans', 10, leading=None)
        file.drawString(
            x,
            y,
            f'- {string[0]} ({string[1]}) - {str(string[2])}'
        )
        y += 15

    file.showPage()
    file.save()
    buffer.seek(0)
    return buffer
