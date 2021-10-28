# Basic Python
import os
from typing import Any, List
import PIL
# Reportlab
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Frame, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import Image
from reportlab.platypus import Flowable
from reportlab.graphics.barcode import qr
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing

# Project related
from envios.models import Envio
from mysite import settings


class QRFlowable(Flowable):
    """
    Thanks to christophe31 at StackOverflow
    This class implementation has been found at:
    https://stackoverflow.com/a/18714402/10860780
    usage :
    story.append(QRFlowable("http://google.fr"))
    """

    def __init__(self, qr_value, wrap_by: int = 1):
        # init and store rendering value
        Flowable.__init__(self)
        self.qr_value = qr_value
        self.wrap_by = wrap_by
        self.hAlign = 'CENTRE'

    def wrap(self, availWidth, availHeight):
        # optionnal, here I ask for the biggest square available
        self.width = self.height = min(
            availWidth*self.wrap_by, availHeight*self.wrap_by)
        return self.width, self.height

    def draw(self):
        # here standard and documented QrCodeWidget usage on
        # Flowable canvas
        qr_code = qr.QrCodeWidget(self.qr_value)
        bounds = qr_code.getBounds()
        qr_width = bounds[2] - bounds[0]
        qr_height = bounds[3] - bounds[1]
        w = float(self.width)
        d = Drawing(w, w, transform=[w/qr_width, 0, 0, w/qr_height, 0, 0])
        d.add(qr_code)
        renderPDF.draw(d, self.canv, 0, 0)


class PDFReport(object):

    LOGO_BASE_SCALAR = 0.68
    LOGO_BASE_WIDTH = 189.86
    LOGO_BASE_HEIGHT = 35.796

    def __init__(self, buffer, **kwargs):
        self.COLS = 12 if not kwargs.get("cols", None) else kwargs["cols"]
        self.ROWS = 16 if not kwargs.get("rows", None) else kwargs["rows"]
        self.MAX_WIDTH, self.MAX_HEIGHT = A4
        self.PADDING = 15 if not kwargs.get(
            "padding", None) else kwargs["padding"]
        self.AVAILABLE_WIDTH = int(self.MAX_WIDTH) - self.PADDING * 3
        self.AVAILABLE_HEIGHT = int(self.MAX_HEIGHT) - self.PADDING * 3
        self.BASE_FRAME_WIDTH = self.AVAILABLE_WIDTH/2
        self.BASE_FRAME_HEIGHT = self.AVAILABLE_HEIGHT/2
        self.TABLE_WIDTH_UNIT = self.BASE_FRAME_WIDTH/self.COLS
        self.TABLE_HIEGHT_UNIT = self.BASE_FRAME_HEIGHT/self.ROWS
        self.stylesheet = getSampleStyleSheet()
        self.buffer = buffer
        self.canvas = Canvas(self.buffer)
        self.logo = Image(
            PIL.Image.open(os.path.join(
                settings.STATIC_ROOT, 'logo_color.png')),
            self.LOGO_BASE_WIDTH*self.LOGO_BASE_SCALAR,
            self.LOGO_BASE_HEIGHT*self.LOGO_BASE_SCALAR
        )
        self.person_image = Image(PIL.Image.open(os.path.join(
            settings.STATIC_ROOT, 'account.png')), 12, 12)
        self.maps_image = Image(PIL.Image.open(os.path.join(
            settings.STATIC_ROOT, 'map-marker.png')), 12, 12)
        self.phone_image = Image(PIL.Image.open(os.path.join(
            settings.STATIC_ROOT, 'phone.png')), 12, 12)
        self.current_position = 1

    def create(self, data: List[Envio]):
        for envio in data:
            self.create_frame(envio)
            self.update_position()
        return self.canvas.save()

    def update_position(self):
        if self.current_position < 4:
            self.current_position += 1
        else:
            self.current_position = 1
            self.canvas.showPage()

    def create_page(self):
        pass

    def create_frame(self, envio: Envio) -> None:
        x = y = self.PADDING
        if self.current_position == 1:
            y = self.MAX_HEIGHT - self.PADDING - self.BASE_FRAME_HEIGHT
        if self.current_position == 2:
            x = self.MAX_WIDTH - self.PADDING - self.BASE_FRAME_WIDTH,
            y = self.MAX_HEIGHT - self.PADDING - self.BASE_FRAME_HEIGHT
        if self.current_position == 4:
            x = self.MAX_WIDTH - self.PADDING - self.BASE_FRAME_WIDTH
        frame = Frame(x, y,
                      self.BASE_FRAME_WIDTH,
                      self.BASE_FRAME_HEIGHT,
                      showBoundary=1)
        frame.addFromList(self.get_story_from_data(envio), self.canvas)

    def get_story_from_data(self, envio: Envio) -> List[Any]:
        header = self.get_table_header(envio.client.name, envio.client.id)
        qr_code = self.get_qr_code(
            envio.id, envio.client.id, envio.recipient_town.id)
        table_below_qr_code = self.get_table_below_qr_code(
            envio.id,
            envio.recipient_town.name,
            envio.recipient_town.partido.name)
        final_table = self.get_final_table(
            envio_recipient=envio.recipient_name,
            envio_address=envio.recipient_address,
            envio_zip_code=envio.recipient_zipcode,
            envio_reference=envio.recipient_entrances,
            envio_phone=envio.recipient_phone
        )
        return [header, qr_code, table_below_qr_code, final_table]

    def get_table_header(
        self,
        client_name: str = "",
        client_id: str = ""
    ) -> Table:
        client_paragraph_style = self.stylesheet["Normal"]
        client_paragraph_style.alignment = 1
        client_paragraph_style.fontName = "Helvetica"
        client_paragraph = Paragraph(
            f"<strong>{client_name}<br/>{client_id}</strong>",
            client_paragraph_style)
        header_data = [[self.logo, client_paragraph]]
        table_header_style = TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEBEFORE', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEAFTER', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTRE'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ])
        table = Table(
            header_data, self.BASE_FRAME_WIDTH/2, self.TABLE_HIEGHT_UNIT*1.5)
        table.setStyle(table_header_style)
        return table

    def get_qr_code(
        self,
        envio_id: int,
        client_id: int,
        town_id: int
    ) -> QRFlowable:
        inner_envio = f"'envio_id': '{envio_id}',"
        inner_cliente = f"'client_id':'{client_id}',"
        inner_town = f"'town_id':'{town_id}'"
        qr_value = "{" + inner_envio + inner_cliente + inner_town + "}"
        return QRFlowable(qr_value, 0.55)

    def get_table_below_qr_code(
        self,
        envio_id: str = "",
        envio_town: str = "",
        envio_partido: str = ""
    ) -> Table:
        data = [
            [envio_id],
            [envio_town],
            [envio_partido],
            ["Destino"],
        ]
        table_style = TableStyle([
            ('TOPPADDING', (0, 0), (0, 0), 0),
            ('BOTTOMPADDING', (0, 2), (0, 2), 10),
            ('FONTNAME', (0, 0), (0, 2), "Helvetica-Bold"),
            ('FONTSIZE', (0, 0), (0, 2), 12),
            ('ALIGN', (0, 0), (0, 2), "CENTRE"),
            ('FONTNAME', (0, 3), (0, 3), "Helvetica-Bold"),
            ('FONTSIZE', (0, 3), (0, 3), 10),
            ('LINEABOVE', (0, 3), (0, 3), 0.5, colors.black),
            ('LINEBELOW', (0, 3), (0, 3), 0.5, colors.black),
            ('VALIGN', (0, 0), (0, 3), "MIDDLE"),
        ])
        table = Table(data, self.BASE_FRAME_WIDTH)
        table.setStyle(table_style)
        return table

    def get_final_table(
        self,
        **kwargs
    ) -> Table:
        """
        This are the kwargs for the data:
        envio_recipient, envio_address, envio_zip_code
        envio_reference, envio_phone.
        By default, they are initialized as 'No especificado'.
        """

        styleN = self.stylesheet["BodyText"]
        styleN.alignment = TA_LEFT

        envio_recipient = kwargs.get('recipient', 'No especificado')
        envio_address = kwargs.get('address', 'No especificado')
        envio_zip_code = kwargs.get('zip_code', 'No especificado')
        envio_reference = kwargs.get('reference', 'No especificado')
        envio_phone = kwargs.get('phone', 'No especificado')

        data = [
            [self.person_image, Paragraph(envio_recipient, styleN),
                "", "", "", "", "", "", "", "", "", ""],
            [self.maps_image, Paragraph(envio_address, styleN),
                "", "", "", "", "", "", "", "", "", ""],
            ["", Paragraph(f"<b>CP:</b> {envio_zip_code}", styleN),
                "", "", "", "", "", "", "", "", "", ""],
            ["", Paragraph(f"<b>Referencias:</b> {envio_reference}", styleN),
                "", "", "", "", "", "", "", "", "", ""],
            [self.phone_image, Paragraph(envio_phone, styleN),
                "", "", "", "", "", "", "", "", "", ""],
        ]
        tstyle = TableStyle([
            ('SPAN', (1, 0), (-1, 0)),
            ('SPAN', (1, 1), (-1, 1)),
            ('SPAN', (1, 2), (-1, 2)),
            ('SPAN', (1, 3), (-1, 3)),
            ('SPAN', (1, 4), (-1, 4)),
            ('ALIGN', (1, 0), (-1, -1), "LEFT"),
            ('VALIGN', (0, 0), (-1, -1), "TOP"),
        ])
        table = Table(data, self.BASE_FRAME_WIDTH/12)
        table.setStyle(tstyle)
        return table
