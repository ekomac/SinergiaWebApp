from django.conf import settings
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Tuple, Union
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, Frame,  PageTemplate,
    Paragraph, TableStyle)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import Image
from reportlab.platypus.tables import LongTable
from reportlab.lib.styles import ParagraphStyle
from envios.utils import calculate_price, get_detail_readable
from summaries.models import ClientSummary, EmployeeSummary


class PDFSummaryReport():

    IMAGE_SIZE = 130
    WIDTH, HEIGHT = A4
    PADDING = 20
    HORIZONTAL_PADDING = 10
    TOP_PADDING = IMAGE_SIZE + PADDING
    UNIT = (WIDTH-21.5)/14
    COL_WIDTHS = [2 * UNIT, 5 * UNIT, 5 * UNIT, 2 * UNIT]
    CELL_BACKGROUND_COLOR = "#d9d9d9"
    LEFT_COLS_STYLE = ParagraphStyle("lcs", alignment=TA_CENTER)
    CENTER_COLS_STYLE = ParagraphStyle("ccs", alignment=TA_LEFT)
    RIGHT_COLS_STYLE = ParagraphStyle("rcs", alignment=TA_RIGHT)

    def __init__(
        self,
        filename: str,
        summary: Union[ClientSummary, EmployeeSummary],
    ) -> None:
        self.styles = getSampleStyleSheet()
        self.filename = filename
        self.summary = summary
        self.pdf = BaseDocTemplate(
            filename, pagesize=A4, leftMargin=0,
            rightMargin=0, topMargin=0, bottomMargin=0)
        self.base_frame = Frame(
            self.pdf.leftMargin, self.pdf.bottomMargin,
            self.WIDTH, self.HEIGHT,
            topPadding=self.TOP_PADDING,
            leftPadding=self.HORIZONTAL_PADDING,
            rightPadding=self.HORIZONTAL_PADDING,
            id='normal')
        self.template = PageTemplate(
            id='all_pages', frames=self.base_frame, onPage=self.__header)
        self.pdf.addPageTemplates([self.template])
        self.from_date = summary.date_from.strftime('%d/%m/%Y')
        self.to_date = summary.date_to.strftime('%d/%m/%Y')
        if isinstance(summary, ClientSummary):
            self.subject = summary.client.name
            self.subj_type = 'CLIENTE'
        if isinstance(summary, EmployeeSummary):
            self.subject = summary.employee.full_name
            self.subj_type = 'EMPLEADO'
        self.data = self.__table_headers_data()
        str(settings.BASE_DIR) + '/app/lib/reportlabs/fonts'
        print(settings.BASE_DIR)

    def __table_headers_data(self):
        HEADERS_STYLE = ParagraphStyle(
            'header', fontSize=9, textColor='white', alignment=TA_CENTER)
        return [
            [
                Paragraph('<b>FECHA</b>', HEADERS_STYLE),
                Paragraph('<b>DOMICILIO</b>', HEADERS_STYLE),
                Paragraph('<b>DETALLE</b>', HEADERS_STYLE),
                Paragraph('<b>VALOR</b>', HEADERS_STYLE)
            ],
        ]

    def __header(self, canvas, doc):
        canvas.saveState()
        image = Image(
            str(settings.BASE_DIR) +
            '\\static\\res\\images\\sinergia-logo-pdf.png',
            self.WIDTH-self.PADDING, self.IMAGE_SIZE, hAlign='CENTRE')
        image_width, image_height = image.wrap(doc.width, doc.topMargin)
        padding = (doc.width-image_width) / 2
        image.drawOn(canvas, doc.leftMargin+padding, doc.height +
                     doc.bottomMargin + doc.topMargin - image_height-padding)
        canvas.restoreState()

    def create(self):
        self.__process()
        self.pdf.build(
            [
                self.__info_date,
                self.__info_date_range,
                self.__info_subject,
                self.__total_periodo,
                self.__resumen_de_cuenta,
                self.__table,
            ])
        return self.pdf

    @property
    def __info_date(self) -> Paragraph:
        today = datetime.today().strftime('%d/%m/%Y')
        return Paragraph(f'<b>FECHA:</b> {today}', self.__info_paragraph_style)

    @property
    def __info_date_range(self) -> Paragraph:
        return Paragraph(
            f'<b>PERÍODO:</b> {self.from_date} al {self.to_date}',
            self.__info_paragraph_style)

    @property
    def __info_subject(self) -> Paragraph:
        return Paragraph(
            f'<b>{self.subj_type}:</b> {self.subject}',
            self.__info_paragraph_style)

    @property
    def __total_periodo(self):
        total = '{:,.2f}'.format(self.total)
        style = ParagraphStyle(
            'total_periodo',
            fontSize=16,
            leading=20,
            spaceBefore=10
        )
        base_str = ('<font backColor="#dee9c9" \
                    fontSize="16"><b>TOTAL PERÍODO:</b> ')
        data = f'{self.envios_count} entregas por $ {total}</font>'
        return Paragraph(base_str+data, style)

    @property
    def __info_paragraph_style(self) -> ParagraphStyle:
        info_style = ParagraphStyle(
            'info_style', spaceBefore=0, leftIndent=0, spaceAfter=2.5)
        info_style.textColor = 'black'
        info_style.alignment = TA_LEFT
        return info_style

    @property
    def __resumen_de_cuenta(self):
        return Paragraph(
            '<b>RESUMEN DE CUENTA</b>',
            ParagraphStyle('resumen_de_cuenta', fontSize=12,
                           spaceBefore=10,
                           alignment=TA_CENTER))

    @property
    def __table(self):
        table = LongTable(self.data, colWidths=self.COL_WIDTHS,
                          longTableOptimize=True, repeatRows=1, spaceBefore=5)
        table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.red),
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('INNERGRID', (0, 0), (-1, 0), 2, colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), self.CELL_BACKGROUND_COLOR),
            ('LINEABOVE', (0, 1), (-1, -1), 2, colors.white),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ]))
        return table

    def __process(
        self,
    ) -> Tuple[List[Dict[str, Any]], Decimal]:
        total = 0
        envios = []
        for envio in self.summary.envios_queried:
            envio_as_list, price = self.__parse_envios(envio)
            self.data.append(envio_as_list)
            envios.append(envio_as_list)
            total += price
        self.envios = envios
        self.total = round(total)
        self.envios_count = len(envios)
        return True

    def __parse_envios(self, envio) -> Tuple[List[Any], Decimal]:
        date = envio.date_delivered.strftime("%d/%m/%Y")
        price = calculate_price(envio)
        as_list = [
            Paragraph(date, self.LEFT_COLS_STYLE),
            Paragraph(envio.full_address, self.CENTER_COLS_STYLE),
            Paragraph(get_detail_readable(envio), self.CENTER_COLS_STYLE),
            Paragraph('$ {:,.2f}'.format(price), self.RIGHT_COLS_STYLE),
        ]
        return as_list, price
