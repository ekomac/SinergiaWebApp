from reportlab.lib.units import inch, cm
import os
from typing import Any, Dict, List
from django.conf import settings

# Reportlab
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Frame, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.flowables import Image
from reportlab.platypus import Flowable
from reportlab.graphics.barcode import qr
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from reportlab.platypus.tables import LongTable


# from envios.models import Envio


# class PDFReport(object):

#     LOGO_BASE_SCALAR = 0.68
#     LOGO_BASE_WIDTH = 189.86
#     LOGO_BASE_HEIGHT = 35.796

#     def __init__(self, buffer, **kwargs):
#         self.COLS = 12 if not kwargs.get("cols", None) else kwargs["cols"]
#         self.ROWS = 16 if not kwargs.get("rows", None) else kwargs["rows"]
#         self.MAX_WIDTH, self.MAX_HEIGHT = A4
#         self.PADDING = 15 if not kwargs.get(
#             "padding", None) else kwargs["padding"]
#         available_width = int(self.MAX_WIDTH) - self.PADDING * 3
#         available_height = int(self.MAX_HEIGHT) - self.PADDING * 3
#         self.BASE_FRAME_WIDTH = available_width/2
#         self.BASE_FRAME_HEIGHT = available_height/2
#         self.TABLE_HIEGHT_UNIT = self.BASE_FRAME_HEIGHT/self.ROWS
#         self.stylesheet = getSampleStyleSheet()
#         self.canvas = Canvas(buffer)
#         self.create_images()
#         self.current_position = 1

#     def create_images(self):
#         self.logo = Image(os.path.join(
#             settings.STATIC_ROOT, 'logo_color.png'),
#             self.LOGO_BASE_WIDTH*self.LOGO_BASE_SCALAR,
#             self.LOGO_BASE_HEIGHT*self.LOGO_BASE_SCALAR
#         )

#     def create(self, data: List[Dict[str, Any]]):
#         for envio in data:
#             self.create_frame(envio)
#             self.update_position()
#         return self.canvas.save()

#     def update_position(self):
#         if self.current_position < 4:
#             self.current_position += 1
#         else:
#             self.current_position = 1
#             self.canvas.showPage()

#     def create_frame(self, envio: Envio) -> None:
#         x = y = self.PADDING
#         if self.current_position == 1:
#             y = self.MAX_HEIGHT - self.PADDING - self.BASE_FRAME_HEIGHT
#         if self.current_position == 2:
#             x = self.MAX_WIDTH - self.PADDING - self.BASE_FRAME_WIDTH
#             y = self.MAX_HEIGHT - self.PADDING - self.BASE_FRAME_HEIGHT
#         if self.current_position == 4:
#             x = self.MAX_WIDTH - self.PADDING - self.BASE_FRAME_WIDTH
#         frame = Frame(x, y,
#                       self.BASE_FRAME_WIDTH,
#                       self.BASE_FRAME_HEIGHT,
#                       showBoundary=1, topPadding=0)
#         story = self.get_story_from_data(envio)
#         frame.addFromList(story, self.canvas)

#     def get_story_from_data(self, envio: Envio) -> List[Any]:
#         envio_type = "Mercado Envíos Flex" if envio.is_flex else "Mensajería"
#         header = self.get_table_header(envio.client.name, envio_type)
#         qr_code = self.get_qr_code(
#             envio.id, envio.client.id, envio.town.id)
#         table_below_qr_code = self.get_table_below_qr_code(
#             envio.id,
#             envio.town.name,
#             envio.town.partido.name)
#         final_table = self.get_final_table(
#             name=envio.name,
#             address=envio.street,
#             zip_code=envio.zipcode,
#             entrances=envio.remarks,
#             phone=envio.phone
#         )
#         return [header, qr_code, table_below_qr_code, final_table]

#     def get_table_header(
#         self,
#         client_name: str = "",
#         envio_type: str = ""
#     ) -> Table:
#         client_paragraph_style = self.stylesheet["Normal"]
#         client_paragraph_style.alignment = 1
#         client_paragraph_style.fontName = "Helvetica"
#         client_paragraph = Paragraph(
#             f"<strong>{client_name}<br/>{envio_type}</strong>",
#             client_paragraph_style)
#         header_data = [[self.logo, client_paragraph]]
#         table_header_style = TableStyle([
#             ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.black),
#             ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTRE'),
#             ('TOPPADDING', (0, 0), (-1, -1), 10),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
#         ])
#         table = Table(
#             header_data, self.BASE_FRAME_WIDTH/2, self.TABLE_HIEGHT_UNIT*1.5)
#         table.setStyle(table_header_style)
#         return table

#     def get_table_below_qr_code(
#         self,
#         envio_id: str = "",
#         envio_town: str = "",
#         envio_partido: str = ""
#     ) -> Table:
#         data = [
#             [envio_id],
#             [envio_town],
#             [envio_partido],
#             ["Destino"],
#         ]
#         table_style = TableStyle([
#             ('TOPPADDING', (0, 0), (0, 0), 0),
#             ('BOTTOMPADDING', (0, 2), (0, 2), 10),
#             ('FONTNAME', (0, 0), (0, 2), "Helvetica-Bold"),
#             ('FONTSIZE', (0, 0), (0, 2), 12),
#             ('ALIGN', (0, 0), (0, 2), "CENTRE"),
#             ('FONTNAME', (0, 3), (0, 3), "Helvetica-Bold"),
#             ('FONTSIZE', (0, 3), (0, 3), 10),
#             ('LINEABOVE', (0, 3), (0, 3), 0.5, colors.black),
#             ('LINEBELOW', (0, 3), (0, 3), 0.5, colors.black),
#             ('VALIGN', (0, 0), (0, 3), "MIDDLE"),
#             ('LEFTPADDING', (-1, -1), (-1, -1), 10),
#         ])
#         table = Table(data, self.BASE_FRAME_WIDTH)
#         table.setStyle(table_style)
#         return table

#     def get_final_table(
#         self,
#         **kwargs
#     ) -> Table:
#         """
#         This are the kwargs for the data:
#         name, address, zip_code, reference, phone.
#         By default, they are initialized as 'No especificado'.
#         """
#         keys = ['name', 'address', 'zip_code', 'entrances', 'phone']
#         for key in keys:
#             kwargs[key] = kwargs[key] if kwargs[key] else 'No especificado'

#         styleN = self.stylesheet["BodyText"]
#         styleN.alignment = TA_LEFT
#         data = []
#         styles = [
#             ('TOPPADDING', (0, 0), (1, 0), 6),
#             ('LEFTPADDING', (0, 0), (0, -1), 10),
#             ('ALIGN', (1, 0), (-1, -1), "LEFT"),
#             ('VALIGN', (0, 0), (-1, -1), "TOP"),
#         ]
#         if kwargs['name'] != 'No especificado':
#             data.append([self.person_image, Paragraph(kwargs['name'], styleN),
#                         "", "", "", "", "", "", "", "", "", ""])
#         data.append([self.maps_image, Paragraph(
#             f"<b>{kwargs['address']}</b>", styleN),
#             "", "", "", "", "", "", "", "", "", ""])
#         if kwargs['zip_code'] != 'No especificado':
#             data.append(["", Paragraph(
#                 f"<b>CP:</b> {kwargs['zip_code']}", styleN),
#                 "", "", "", "", "", "", "", "", "", ""])
#         if kwargs['entrances'] != 'No especificado':
#             data.append(["", Paragraph(
#                 f"<b>Referencias:</b> {kwargs['entrances']}", styleN),
#                 "", "", "", "", "", "", "", "", "", ""])
#         if kwargs['phone'] != 'No especificado':
#             data.append([self.phone_image, Paragraph(kwargs['phone'], styleN),
#                         "", "", "", "", "", "", "", "", "", ""])

#         for i in range(len(data)):
#             styles.append(('SPAN', (1, i), (-1, i)))

#         tstyle = TableStyle(styles)
#         table = Table(data, self.BASE_FRAME_WIDTH/12, spaceBefore=6)
#         table.setStyle(tstyle)
#         return table


def main():
    stylesheet = getSampleStyleSheet()
    canvas = Canvas("ejemplo.pdf")
    story = []
    style = stylesheet["Normal"]
    style.alignment = 1
    style.fontName = "Helvetica"
    PADDING = 15
    MAX_WIDTH, MAX_HEIGHT = A4
    available_width = int(MAX_WIDTH) - (PADDING * 3)
    available_height = int(MAX_HEIGHT) - (PADDING * 3)

    logo = Image(
        'C:\\Users\\jcmac\\Projects\\eko-software\\sinergia\\SinergiaDjangoWebApp\\src\\static\\res\\images\\sinergia-logo-pdf.png',
        available_width, 130
    )
    story.append(logo)
    # bold_style = normal_style = stylesheet["Normal"]
    # bold_style.alignment, normal_style.alignment = 1, 1
    # bold_style.fontName, normal_style.fontName = "Helvetica", "Helvetica Bold"
    # bold_style = Paragraph(
    #     f"<strong>{client_name}<br/>{envio_type}</strong>", client_paragraph_style)
    data = [
        ['FECHA:', '10/1/2022'],
        ['PERÍODO:', '1/1/2022 al 10/1/2022'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        # ['CLIENTE:', 'Bulonera Mitre S.A.',
        #     'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
    ]

    info = LongTable(data, style=[
        ('FONTNAME', (0, 0), (0, 2), "Helvetica-Bold"),
        ('FONTSIZE', (0, 0), (0, 2), 12),
        ('FONTNAME', (1, 0), (-1, -1), "Helvetica"),
        ('FONTSIZE', (1, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ])
    # BASE_FRAME_WIDTH/2 TABLE_HIEGHT_UNIT*1.5
    # table.setStyle(table_header_style)
    story.append(info)
    frame = Frame(
        x1=PADDING, y1=PADDING,
        width=MAX_WIDTH - (PADDING * 2),
        height=MAX_HEIGHT - (PADDING * 2),
        showBoundary=1, topPadding=0
    )
    frame.addFromList(story, canvas)
    canvas.showPage()
    canvas.save()


def main2():
    elements = []
    doc = SimpleDocTemplate("ejemplo2.pdf", pagesize=A4, )
    data = [
        ['FECHA:', '10/1/2022'],
        ['PERÍODO:', '1/1/2022 al 10/1/2022',
            '1/1/2022 al 10/1/2022', '1/1/2022 al 10/1/2022'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
        ['CLIENTE:', 'Bulonera Mitre S.A.',
            'Bulonera Mitre S.A.', 'Bulonera Mitre S.A.'],
    ]

    t = LongTable(data, colWidths=[2 * cm, 5 *
                  cm, 5 * cm, 2 * cm], longTableOptimize=True)
    t.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                           ]))
    elements.append(t)
    doc.build(elements)


if __name__ == "__main__":
    main()
    main2()
