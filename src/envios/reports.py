from datetime import datetime
from reportlab.pdfgen import canvas
import os
import json
from reportlab.lib.units import inch
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate
from typing import Any, Iterable, List
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Frame, Table, TableStyle
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import Image
from reportlab.platypus import Flowable
from reportlab.graphics.barcode import qr
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from envios.models import Envio
from mysite import settings


MAX_ENTRANCE_CHARS = 200


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
    SINERGIA_WEB = "www.sinergiamensajeria.com"
    SINERGIA_TEL = "+54 9 11 2745-8276"
    SINERGIA_FOOTER = "www.sinergiamensajeria.com / +54 9 11 2745-8276"

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
        self.whatsapp_image = Image(os.path.join(
            settings.STATIC_ROOT, 'phone.png'), 12, 12)
        self.money_image = Image(os.path.join(
            settings.STATIC_ROOT, 'money.png'), 12, 12)
        self.link_image = Image(os.path.join(
            settings.STATIC_ROOT, 'link.png'), 12, 12)

    def create(self, data: List[Envio]):
        for envio in data:
            self.canvas.setFont("Helvetica-Oblique", 9)
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
        self.canvas.rect(x, y, self.BASE_FRAME_WIDTH, 12, stroke=1, fill=0)
        self.canvas.drawCentredString(
            x+self.BASE_FRAME_WIDTH//2, y+3, self.SINERGIA_FOOTER)
        frame = Frame(x, y,
                      self.BASE_FRAME_WIDTH,
                      self.BASE_FRAME_HEIGHT,
                      showBoundary=1, topPadding=0)
        story = self.get_story_from_data(envio)
        frame.addFromList(story, self.canvas)

    def get_story_from_data(self, envio: Envio) -> List[Any]:
        envio_type = "Mercado Envíos Flex" if envio.is_flex else "Mensajería"
        header = self.get_table_header(envio.client.name, envio_type)
        qr_code = self.get_qr_code(
            envio.tracking_id, envio.client.id, envio.town.id, envio.is_flex)
        table_below_qr_code = self.get_table_below_qr_code(
            envio.tracking_id,
            envio.town.name,
            envio.town.partido.name)
        final_table = self.get_final_table(
            name=envio.name,
            address=envio.street,
            zip_code=envio.zipcode,
            entrances=envio.remarks,
            phone=envio.phone,
            charge=envio.charge if envio.charge else None
        )
        return [header, qr_code, table_below_qr_code, final_table]

    def get_table_header(
        self,
        client_name: str = "",
        envio_type: str = ""
    ) -> Table:
        client_paragraph_style = self.stylesheet["Normal"]
        client_paragraph_style.alignment = 1
        client_paragraph_style.fontName = "Helvetica"
        client_paragraph = Paragraph(
            f"<strong>{client_name}<br/>{envio_type}</strong>",
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
        envio_tracking_id: int,
        client_id: int,
        town_id: int,
        is_flex: bool = False
    ) -> QRFlowable:
        qr_value = json.dumps({
            "envio_tracking_id": str(envio_tracking_id),
            "client_id": str(client_id),
            "town_id": str(town_id),
            "is_flex": str(is_flex),
        })
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
        keys = ['name', 'address', 'zip_code',
                'entrances', 'phone', 'charge', ]
        for key in keys:
            kwargs[key] = kwargs[key] if kwargs[key] else 'No especificado'

        styleN = self.stylesheet["BodyText"]
        styleN.alignment = TA_LEFT
        data = []
        styles = [
            ('TOPPADDING', (0, 0), (1, 0), 0),
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
            txt = f"<b>Referencias:</b> {kwargs['entrances']}"
            if len(txt) > MAX_ENTRANCE_CHARS:
                txt = txt[:200] + "..."
            data.append(["", Paragraph(
                txt, styleN),
                "", "", "", "", "", "", "", "", "", ""])
        if kwargs['phone'] != 'No especificado':
            data.append([self.phone_image, Paragraph(kwargs['phone'], styleN),
                        "", "", "", "", "", "", "", "", "", ""])
        if kwargs['charge'] != 'No especificado':
            txt = "<b>Cobrar</b>: %s,00.-" % str(kwargs['charge'])
            data.append([self.money_image, Paragraph(txt, styleN),
                        "", "", "", "", "", "", "", "", "", ""])

        for i in range(len(data)):
            styles.append(('SPAN', (1, i), (-1, i)))

        tstyle = TableStyle(styles)
        table = Table(data, self.BASE_FRAME_WIDTH/12, spaceBefore=6)
        table.setStyle(tstyle)
        return table


class PDFEnviosListReport:

    def __init__(
        self,
        response: HttpResponse,
        employee_name: str = ""
    ) -> None:
        self._response = response
        self._employee_name = employee_name
        self._is_for_employee = employee_name != ""

    def _envios_as_list(self, i: int, envio: Envio) -> list[str]:
        styleN = getSampleStyleSheet()["BodyText"]
        styleN.alignment = TA_LEFT
        phone = ""
        if envio.phone != "" and envio.phone is not None:
            phone = f"{envio.phone} (destino)"
        elif (phone == ""
              and envio.client
              and envio.client.contact_phone is not None
              and envio.client.contact_phone != ""
              ):
            phone = f"{envio.client.contact_phone} (cliente)"

        if "None" in phone:
            phone = ""

        ret = [
            str(i+1),
            Paragraph(envio.tracking_id, styleN),
            Paragraph(phone, styleN),
            # Paragraph(str(envio.get_status_display()), styleN),
            Paragraph("Flex" if envio.is_flex else "Mensajería", styleN),
            Paragraph(str(envio.client.name), styleN),
            Paragraph(str(envio.full_address), styleN),
        ]

        if not self._is_for_employee:
            print(f"{envio=}")
            loc_data = ""
            if envio.carrier is not None:
                loc_data = envio.carrier.full_name
            if envio.deposit is not None:
                loc_data = envio.deposit.name
            if envio.deposit is not None:
                loc_data = envio.deposit.name
            ret.append(Paragraph(loc_data, styleN))

        ret.extend([
            Paragraph(
                str(envio.max_delivery_date if (
                    envio.max_delivery_date is not None) else ""),
                styleN
            ),
            Paragraph(
                str(f'{envio.delivery_schedule} hs' if (
                    envio.delivery_schedule is not None) else ""),
                styleN
            ),
            Paragraph(
                f'$ {envio.charge}' if envio.charge else "", styleN),
        ])

        return ret

    def _parse_as_table_data(self, envios: Iterable[Envio]) -> list[list[str]]:
        return [self._envios_as_list(i, envio)
                for i, envio in enumerate(envios)]

    def _crete_envios_table(self, envios: Iterable[Envio]) -> Table:
        header = ['N.°', 'ID', 'Teléfono', 'Tipo', 'Cliente', 'Destino',
                  'Localización', 'Fecha límite',
                  'Horario entrega', 'A cobrar']
        colWidths = [inch*0.5] + [None]*3 + \
            [inch*1.4, inch*3, inch*1.2] + [None]*3

        if self._is_for_employee:
            header.pop(6)
            colWidths.pop(6)

        table_data = self._parse_as_table_data(envios)
        table_data.insert(0, header)

        ret = Table(table_data, hAlign='LEFT', colWidths=colWidths)

        style = TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
        ])
        ret.setStyle(style)
        return ret

    class MyCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            canvas.Canvas.__init__(self, *args, **kwargs)
            self.pages = []

        def showPage(self):
            self.pages.append(dict(self.__dict__))
            self._startPage()

        def draw_page_number(self, page_count, date):
            # Modify the content and styles according to the requirement
            page = "Página {curr_page} de {total_pages}".format(
                curr_page=self._pageNumber, total_pages=page_count)
            self.setFont("Helvetica", 10)
            date = f'Fecha creación: {date}'
            # txt = f'{date} - {page}'
            self.drawRightString(A4[1]-10, A4[0]-15, date)
            self.drawRightString(A4[1]-10, 5, page)

        def save(self):
            page_count = len(self.pages)
            for page in self.pages:
                self.__dict__.update(page)
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.draw_page_number(page_count, date)
                canvas.Canvas.showPage(self)

            canvas.Canvas.save(self)

    def create(self, envios: Iterable[Envio], date: str) -> HttpResponse:
        cm = 2.54
        doc = SimpleDocTemplate(
            self._response, pagesize=landscape(A4),
            rightMargin=0.5 * cm, leftMargin=0.5 * cm,
            topMargin=20, bottomMargin=20
        )

        contents = []

        if self._employee_name != "":
            contents.append(Paragraph(f"Portados por {self._employee_name}"))

        contents.append(self._crete_envios_table(envios))

        doc.build(contents, canvasmaker=self.MyCanvas)

        return self._response
