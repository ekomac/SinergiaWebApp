# Basic Python
import os
from typing import Any, List

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
        available_width = int(self.MAX_WIDTH) - self.PADDING * 3
        available_height = int(self.MAX_HEIGHT) - self.PADDING * 3
        self.BASE_FRAME_WIDTH = available_width/2
        self.BASE_FRAME_HEIGHT = available_height/2
        self.TABLE_HIEGHT_UNIT = self.BASE_FRAME_HEIGHT/self.ROWS
        self.stylesheet = getSampleStyleSheet()
        self.canvas = Canvas(buffer)
        self.create_images()
        self.current_position = 1

    def create_images(self):
        self.logo = Image(os.path.join(
            settings.STATIC_ROOT, 'logo_color.png'),
            self.LOGO_BASE_WIDTH*self.LOGO_BASE_SCALAR,
            self.LOGO_BASE_HEIGHT*self.LOGO_BASE_SCALAR
        )
        self.person_image = Image(os.path.join(
            settings.STATIC_ROOT, 'account.png'), 12, 12)
        self.maps_image = Image(os.path.join(
            settings.STATIC_ROOT, 'map-marker.png'), 12, 12)
        self.phone_image = Image(os.path.join(
            settings.STATIC_ROOT, 'phone.png'), 12, 12)

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

    def create_frame(self, envio: Envio) -> None:
        x = y = self.PADDING
        if self.current_position == 1:
            y = self.MAX_HEIGHT - self.PADDING - self.BASE_FRAME_HEIGHT
        if self.current_position == 2:
            x = self.MAX_WIDTH - self.PADDING - self.BASE_FRAME_WIDTH
            y = self.MAX_HEIGHT - self.PADDING - self.BASE_FRAME_HEIGHT
        if self.current_position == 4:
            x = self.MAX_WIDTH - self.PADDING - self.BASE_FRAME_WIDTH
        frame = Frame(x, y,
                      self.BASE_FRAME_WIDTH,
                      self.BASE_FRAME_HEIGHT,
                      showBoundary=1, topPadding=0)
        story = self.get_story_from_data(envio)
        frame.addFromList(story, self.canvas)

    def get_story_from_data(self, envio: Envio) -> List[Any]:
        header = self.get_table_header(envio.client.name, envio.client.id)
        qr_code = self.get_qr_code(
            envio.id, envio.client.id, envio.town.id)
        table_below_qr_code = self.get_table_below_qr_code(
            envio.id,
            envio.town.name,
            envio.town.partido.name)
        final_table = self.get_final_table(
            name=envio.name,
            address=envio.street,
            zip_code=envio.zipcode,
            entrances=envio.remarks,
            phone=envio.phone
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
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTRE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
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
        inner_envio = f'"envio_id": "{envio_id}",'
        inner_cliente = f'"client_id":"{client_id}",'
        inner_town = f'"town_id":"{town_id}"'
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
            ('LEFTPADDING', (-1, -1), (-1, -1), 10),
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
        name, address, zip_code, reference, phone.
        By default, they are initialized as 'No especificado'.
        """
        keys = ['name', 'address', 'zip_code', 'entrances', 'phone']
        for key in keys:
            kwargs[key] = kwargs[key] if kwargs[key] else 'No especificado'

        styleN = self.stylesheet["BodyText"]
        styleN.alignment = TA_LEFT
        data = []
        styles = [
            ('TOPPADDING', (0, 0), (1, 0), 6),
            ('LEFTPADDING', (0, 0), (0, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), "LEFT"),
            ('VALIGN', (0, 0), (-1, -1), "TOP"),
        ]
        if kwargs['name'] != 'No especificado':
            data.append([self.person_image, Paragraph(kwargs['name'], styleN),
                        "", "", "", "", "", "", "", "", "", ""])
        data.append([self.maps_image, Paragraph(
            f"<b>{kwargs['address']}</b>", styleN),
            "", "", "", "", "", "", "", "", "", ""])
        if kwargs['zip_code'] != 'No especificado':
            data.append(["", Paragraph(
                f"<b>CP:</b> {kwargs['zip_code']}", styleN),
                "", "", "", "", "", "", "", "", "", ""])
        if kwargs['entrances'] != 'No especificado':
            data.append(["", Paragraph(
                f"<b>Referencias:</b> {kwargs['entrances']}", styleN),
                "", "", "", "", "", "", "", "", "", ""])
        if kwargs['phone'] != 'No especificado':
            data.append([self.phone_image, Paragraph(kwargs['phone'], styleN),
                        "", "", "", "", "", "", "", "", "", ""])

        for i in range(len(data)):
            styles.append(('SPAN', (1, i), (-1, i)))

        tstyle = TableStyle(styles)
        table = Table(data, self.BASE_FRAME_WIDTH/12, spaceBefore=6)
        table.setStyle(tstyle)
        return table
