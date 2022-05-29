# coding: utf-8

import os

from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def link_callback(uri, rel):
    """
    Стандарный метод из документации для того, чтобы xhtml2pdf
    имел доступ к глобальным настройкам.
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        static_url = settings.STATIC_URL  # Typically /static/
        static_root = (
            settings.STATIC_ROOT
        )  # Typically /home/userX/project_static/
        media_url = settings.MEDIA_URL  # Typically /media/
        media_root = (
            settings.MEDIA_ROOT
        )  # Typically /home/userX/project_static/media/

        if uri.startswith(media_url):
            path = os.path.join(media_root, uri.replace(media_url, ""))
        elif uri.startswith(static_url):
            path = os.path.join(static_root, uri.replace(static_url, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            f"media URI must start with {static_url} or {media_url}"
        )
    return path


def render_pdf(request, context, template_path):
    """
    Метод рендера html шаблона в пдф.
    """
    #    template_path = 'user_printer.html'
    # context = extract_request_variables(request)

    response = HttpResponse(content_type="application/pdf")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="shopping_list_{request.user}.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    if request.POST.get("show_html", ""):
        response["Content-Type"] = "application/text"
        response["Content-Disposition"] = 'attachment; filename="report.txt"'
        response.write(html)
    else:
        pisa_status = pisa.CreatePDF(
            html, dest=response,
            link_callback=link_callback,
            encoding='utf-8'
        )
        if pisa_status.err:
            return HttpResponse(
                "We had some errors with code %s <pre>%s</pre>"
                % (pisa_status.err, html)
            )
    return response
