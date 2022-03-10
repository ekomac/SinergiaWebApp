from django.conf import settings
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Tuple
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
from transactions.models import Transaction


class PDFTransactionsReport():

    IMAGE_SIZE = 130
    WIDTH, HEIGHT = A4
    PADDING = 20
    HORIZONTAL_PADDING = 10
    TOP_PADDING = IMAGE_SIZE + PADDING
    UNIT = (WIDTH-21.5)/28
    COL_WIDTHS = [4 * UNIT, 6 * UNIT, 12 * UNIT, 6 * UNIT]
    CELL_BACKGROUND_COLOR = "#d9d9d9"
    CENTER_COLS_STYLE = ParagraphStyle("lcs", alignment=TA_CENTER)
    LEFT_COLS_STYLE = ParagraphStyle("ccs", alignment=TA_LEFT)
    RIGHT_COLS_STYLE = ParagraphStyle("rcs", alignment=TA_RIGHT)

    def __init__(
        self,
        filename: str,
        transactions: List[Transaction],
        date_from: datetime,
        date_to: datetime,
    ) -> None:
        self.styles = getSampleStyleSheet()
        self.filename = filename
        self.transactions = transactions
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
        self.from_date = date_from.strftime('%d/%m/%Y')
        self.to_date = date_to.strftime('%d/%m/%Y')
        self.data = self.__table_headers_data()

    def __table_headers_data(self):
        HEADERS_STYLE = ParagraphStyle(
            'header', fontSize=9, textColor='white', alignment=TA_CENTER)
        return [
            [
                Paragraph('<b>FECHA</b>', HEADERS_STYLE),
                Paragraph('<b>CATEGORIA</b>', HEADERS_STYLE),
                Paragraph('<b>DESCRIPCION</b>', HEADERS_STYLE),
                Paragraph('<b>IMPORTE</b>', HEADERS_STYLE)
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
        data = f'{self.transactions_count} movimientos por $ {total}</font>'
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
        total = Decimal(0)
        result = []
        for transaction in self.transactions:
            transaction_as_list, amount = self.__parse_transaction(transaction)
            self.data.append(transaction_as_list)
            result.append(transaction_as_list)
            total += amount
        self.resulting_transactions = result
        self.total = round(total)
        self.transactions_count = len(result)
        return True

    def __parse_transaction(self, transaction) -> Tuple[List[str], Decimal]:
        date = transaction.date.strftime("%d/%m/%Y")
        return [
            Paragraph(date, self.CENTER_COLS_STYLE),
            Paragraph(transaction.get_category_display(),
                      self.LEFT_COLS_STYLE),
            Paragraph(transaction.description, self.LEFT_COLS_STYLE),
            Paragraph('$ {:,.2f}'.format(transaction.amount),
                      self.RIGHT_COLS_STYLE),
        ], transaction.amount
