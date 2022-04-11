PLAIN_TICKET_CREATED = """
Se ha creado un nuevo ticket en el sistema.\n\n
Ticket #{pk}: {subject} con prioridad {prioridad}\n
Mensaje: {msg}\n\n
Autor: {created_by}\n\n
"""

HTML_TICKET_CREATED = """
<h1>Se ha creado un <a href='{url}'>nuevo ticket</a> en el sistema.</h1>
<h3>Ticket #{pk}: {subject} con prioridad {prioridad}</h3>
<p><b>Mensaje</b>: {msg}</p>
<p><b>Autor</b>: <a href='{user_url}'>{author} ({author_name})</a></p>
"""

PLAIN_TICKET_CLOSED_FOR_SUPERUSER = """
Se {action} un ticket.\n\n
Ticket #{pk}: {subject} con prioridad {prioridad}\n
Motivo: {closed_reason}\n\n
Mensaje: {closed_message}\n\n
Autor: {created_by}\n\n
"""

HTML_TICKET_CLOSED_FOR_SUPERUSER = """
<h1>{author1} {action} un <a href='{url}'>ticket</a>.</h1>
<h3>Ticket #{pk}: {subject} con prioridad {prioridad}</h3>
<p><b>Motivo</b>: {closed_reason}</p>
<p><b>Mensaje</b>: {closed_message}</p>
<p><b>Autor</b>: <a href='{user_url}'>{author2} ({author_name})</a></p>
"""

PLAIN_NEW_MESSAGE_IN_TICKET = """
Se ha registrado un nuevo mensaje en el ticket "{ticket}".\n\n
{user} escribió:\n
"{msg}"\n\n
{date}\n\n
"""

HTML_NEW_MESSAGE_IN_TICKET = """
<h1>Se ha registrado un nuevo mensaje en el ticket "<a href="{ticket_url}">\
    {ticket_subject}</a>".</h1>
<div style="border: 1px solid grey; padding: 1rem; margin: auto;">
<p><a href="{author_url}">@{author_username}</a> escribió:</p>
<p>"{msg}"</p>
<p>El {date} a las {time}</p>
</div>
"""

PLAIN_TICKET_CLOSED_FOR_USER = """
Se cerró un ticket creado por vos.\n\n
Ticket #{pk}: {subject} con prioridad {prioridad}\n
Motivo: {closed_reason}\n\n
Mensaje: {closed_message}\n\n
Autor: {created_by}\n\n
"""

HTML_TICKET_CLOSED_FOR_USER = """
<h1>Se cerró un <a href='{url}'>ticket</a> creado por vos.</h1>
<h3>Ticket #{pk}: {subject} con prioridad {prioridad}</h3>
<p><b>Motivo</b>: {closed_reason}</p>
<p><b>Mensaje</b>: {closed_message}</p>
<p><b>Autor</b>: <a href='{user_url}'>{author} ({author_name})</a></p>
"""
messages = {
    'PLAIN_TICKET_CREATED': PLAIN_TICKET_CREATED,
    'HTML_TICKET_CREATED': HTML_TICKET_CREATED,
    'PLAIN_TICKET_CLOSED_FOR_SUPERUSER': PLAIN_TICKET_CLOSED_FOR_SUPERUSER,
    'HTML_TICKET_CLOSED_FOR_SUPERUSER': HTML_TICKET_CLOSED_FOR_SUPERUSER,
    'PLAIN_NEW_MESSAGE_IN_TICKET': PLAIN_NEW_MESSAGE_IN_TICKET,
    'HTML_NEW_MESSAGE_IN_TICKET': HTML_NEW_MESSAGE_IN_TICKET,
    'PLAIN_TICKET_CLOSED_FOR_USER': PLAIN_TICKET_CLOSED_FOR_USER,
    'HTML_TICKET_CLOSED_FOR_USER': HTML_TICKET_CLOSED_FOR_USER
}
