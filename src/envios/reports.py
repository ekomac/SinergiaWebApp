import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Table, TableStyle, Frame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import Image, Spacer
import PIL
from mysite import settings


class PDFReport(object):

    MAX_WIDTH, MAX_LENGTH = A4
    HALF_WIDTH = MAX_WIDTH / 2
    HALF_LENGTH = MAX_LENGTH / 2
    stylesheet = getSampleStyleSheet()

    def __init__(
        self,
        buffer,
        title,
        expiration_date,
        id,
        date,
        customer_info: dict,
        order_items: list,
        results: dict,
    ) -> None:
        self.buffer = buffer
        self.title = title
        self.expiration_date = expiration_date
        self.id = id
        self.date = date
        self.customer_info = customer_info
        self.order_items = order_items
        self.results = results
        self.pdf = None

    def create_pdf(self):
        self.pdf = canvas.Canvas(self.buffer, pagesize=A4)
        self.pdf.setTitle(self.title)
        self.paddings = self.get_paddings()
        self.set_header()
        self.set_footer(self.expiration_date)

        # total width - paddings (2x20)
        frame_width = self.MAX_WIDTH - 40
        # total width - padding top (30) & bottom (20)
        frame_height = self.MAX_LENGTH - 50
        f = Frame(self.paddings['start'], self.paddings['bottom'],
                  frame_width, frame_height, showBoundary=0)

        story = []
        table_info_1 = self.get_info_part_1_table(self.date, self.id)
        table_info_2 = self.get_info_part_2_table()
        table_order = self.get_order_table()
        table_result = self.get_results_table()
        parts = [
            table_info_1, Spacer(0, 5), table_info_2, Spacer(0, 10),
            table_order, Spacer(0, 10), table_result,
        ]

        story = [part for part in parts]

        f.addFromList(story, self.pdf)
        self.pdf.showPage()
        self.pdf.save()
        return

    def get_paddings(self):
        return {
            'top': self.MAX_LENGTH - 30,
            'start': 20,
            'end': self.MAX_WIDTH - 20,
            'bottom': 20,
        }

    def set_header(self):
        rect_width = self.HALF_WIDTH - 75
        self.pdf.setFillColorRGB(0, 0, 0)
        self.pdf.rect(self.paddings['start'], self.paddings['top'],
                      rect_width, 9, stroke=0, fill=1)
        self.pdf.rect(self.paddings['end'], self.paddings['top'],
                      -(rect_width), 9, stroke=0, fill=1)
        self.pdf.setFont("Helvetica", 12)
        self.pdf.setFillColorRGB(0, 0, 0)
        self.pdf.drawCentredString(
            x=self.MAX_WIDTH / 2,
            y=self.paddings['top'] + 0.6,
            text="PRESUPUESTO")
        return

    def set_footer(self, expiration_date):
        rect_width = self.HALF_WIDTH-80
        self.pdf.rect(self.paddings['start'], self.paddings['bottom'],
                      rect_width, 9, stroke=0, fill=1)
        self.pdf.rect(self.paddings['end'], self.paddings['bottom'],
                      -(rect_width), 9, stroke=0, fill=1)
        self.pdf.setFont("Helvetica", 12)
        self.pdf.drawCentredString(
            (self.MAX_WIDTH/2) + 7.5,
            20.5,
            "/entretelas.mlh"
        )
        ig = PIL.Image.open(os.path.join(
            settings.STATIC_ROOT, 'instagram.jpg'))
        x_ig, y_ig = self.HALF_WIDTH - 53, 18
        w_ig, h_ig = 13, 13
        self.pdf.drawInlineImage(ig, x_ig, y_ig, w_ig, h_ig)

        textobject = self.pdf.beginText()
        textobject.setTextOrigin(20, 55)
        textobject.setFont("Helvetica", 11)
        textobject.textLines(
            f"""
            * Este presupuesto tiene validez hasta el día {expiration_date}.
            ** Una vez confirmado, se abona una seña del 50% del total.
            """)
        self.pdf.drawText(textobject)
        return

    def tabler(self, data, colWidths, rowHeights=None, style=None):
        table = Table(data, colWidths, rowHeights, style)
        table.wrapOn(self.pdf, self.MAX_WIDTH, self.HALF_LENGTH)
        return table

    def get_info_part_1_table(self, date, id):
        data = [
            ["FECHA: ", str(date), "NÚMERO: ", f'#{id}'],
        ]
        style = TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica'),
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTNAME', (3, 0), (3, 0), 'Helvetica'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ('ALIGN', (3, 0), (3, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (0, 0), 20),
            ('LEFTPADDING', (2, 0), (2, 0), 20),
            ('RIGHTPADDING', (3, 0), (3, 0), 22),
        ])
        colWidths = [55, self.HALF_WIDTH-55, self.HALF_WIDTH-70, 70]
        return self.tabler(data, colWidths, style=style)

    def get_info_logo(self):
        w, h = 139.074, 141.113
        return Image(os.path.join(settings.STATIC_ROOT, 'pdf_logo.png'), w, h)

    def get_p_info_style(self):
        styleP = self.stylesheet["Normal"]
        styleP.alignment = TA_JUSTIFY
        styleP.fontName = "Helvetica"
        return styleP

    def get_corp_info(self, style):
        text = """
        <strong>María Loreto Henning</strong><br/>
        <br/>
        Tel. +54 9 11 5972-2765<br/>
        entretelas.mlh@gmail.com<br/>
        Bella Vista<br/>
        Buenos Aires (Argentina)<br/>
        """
        return Paragraph(text, style)

    def get_client_info(self, style):
        first = self.customer_info.get('first')
        last = self.customer_info.get('last')
        tel = self.customer_info.get('tel')
        email = self.customer_info.get('email')
        city = self.customer_info.get('city')
        zip_code = self.customer_info.get('zip_code')
        state = self.customer_info.get('state')
        text = f"""
            CLIENTE<br/>
            <br/>
            <strong>{first} {last}</strong><br/>
            <br/>
            {tel}<br/>
            {email}<br/>
            {city} ({zip_code})<br/>
            {state}<br/>
            <br/>
            <br/>
            """
        return Paragraph(text, style)

    def get_info_part_2_table(self):
        paragraph_style = self.get_p_info_style()
        logo = self.get_info_logo()
        corp = self.get_corp_info(paragraph_style)
        client = self.get_client_info(paragraph_style)

        data = [
            [logo, corp, client],
            ["", "", ""]
        ]

        style = [
            # TOP LINE
            ('LINEABOVE', (0, 0), (2, 0), 1, colors.black),

            # CORP-CLIENT DIVIDER
            ('LINEBEFORE', (2, 0), (2, 1), 1, colors.black),

            # VALIGN ALL CELL IN MIDDLE
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # ALIGN LOGO LEFT
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),

            # PAD LEFT LOGO
            ('LEFTPADDING', (0, 0), (0, 0), 15),

            # ALIGN CORP & CLIENT CENTER
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),

            # ADD TOP PADDING TO LOGO
            ('TOPPADDING', (0, 0), (0, 0), 20),

            # ADD LEFT PADDING TO CLIENT INFO
            ('LEFTPADDING', (2, 0), (2, 1), 30),
        ]

        col_size = (self.MAX_WIDTH-40)/3
        colWidths = [col_size, col_size-25, col_size+25]
        rowHeights = [141.113, 20]
        return self.tabler(data, colWidths, rowHeights, style)

    def get_order_table(self):
        data = [
            ["CONCEPTO", "CANTIDAD", "VALOR", "IMPORTE"], ]

        for item in self.order_items:
            data.append(item)

        style = [

            # TABLE HEADER
            ('GRID', (0, 0), (3, 0), 2, colors.white),
            ('BACKGROUND', (0, 0), (3, 0), colors.black),
            ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (3, 0), 9),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.white),

            # Align concept column (0) to the left
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),

            # Align quentity column (1) to the center
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),

            # Align value and amount columns (2, 3) to the right
            ('ALIGN', (2, 1), (3, -1), 'RIGHT'),

            # Align value and amount headers to the center
            ('ALIGN', (2, 0), (3, 0), 'CENTER'),

            # TABLE BODY
            ('BOX', (0, 1), (-1, -1), 2, colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),

            # VALIGN ALL CELLS IN MIDDLE
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]

        col_size = (self.MAX_WIDTH-40)/20
        colWidths = [col_size*9, col_size*3, col_size*4, col_size*4]
        return self.tabler(data, colWidths, style=style)

    def get_results_table(self):

        subtotal = self.results.get('subtotal')
        discount_percentage = self.results.get('discount_percentage')
        discount_amount = self.results.get('discount_amount')
        total = self.results.get('total')

        lsubtotal = ["", "SUBTOTAL", f'$ {subtotal}']
        ldiscount = ["", f'DESCUENTO {discount_percentage}% Confección',
                     f'$ -{discount_amount}']
        ltotal = ["", "TOTAL PRESUPUESTO", f'$ {total}']

        data = [lsubtotal, ldiscount, ltotal, ]

        style = [

            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),

            ('FONTSIZE', (0, 0), (1, 1), 11),

            # Last rows bigger size
            ('FONTSIZE', (0, 2), (1, 2), 13),

            # TOP LINE
            ('LINEABOVE', (1, 0), (2, 0), 0.25, colors.black),

            ('LINEBELOW', (1, 1), (2, 1), 1, colors.black),

            # VALIGN ALL CELLS IN MIDDLE
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # ADD TOP PADDING TO LOGO
            ('TOPPADDING', (1, 0), (2, 0), 15),

            # ADD TOP PADDING TO LOGO
            ('BOTTOMPADDING', (1, 1), (2, 1), 15),

            # Align left column to the left
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),

        ]
        col_size = (self.MAX_WIDTH-40)/20
        colWidths = [col_size*9, col_size*5.5, col_size*5.5]
        rowHeights = [30, 30, 40]
        return self.tabler(data, colWidths, rowHeights, style)
