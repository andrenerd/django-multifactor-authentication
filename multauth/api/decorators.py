# https://www.djaodjin.com/blog/django-rest-framework-api-docs.blog

try:
    from drf_yasg.utils import swagger_auto_schema

except ImportError:
    from functools import wraps
    from django.utils.decorators import available_attrs

    def swagger_auto_schema(function=None, **kwargs):
        """
        Dummy decorator when drf_yasg is not present.
        """
        def decorator(view_func):
            @wraps(view_func, assigned=available_attrs(view_func))
            def _wrapped_view(request, *args, **kwargs):
                return view_func(request, *args, **kwargs)
            return _wrapped_view

        if function:
            return decorator(function)

        return decorator
