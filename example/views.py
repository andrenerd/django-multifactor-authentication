from django.shortcuts import render


def handler403(request, template_name='403.html'):
    response = render(request, template_name)
    response.status_code = 403
    return response


def handler404(request, template_name='404.html'):
    response = render(request, template_name)
    response.status_code = 404
    return response


def handler500(request, template_name='500.html'):
    response = render(request, template_name)
    response.status_code = 500
    return response
