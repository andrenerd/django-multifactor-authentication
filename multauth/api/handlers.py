from django.conf import settings

from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.views import exception_handler


# TODO: modularize inside
def api_exception_handler(exc, context):

    # set response
    response = exception_handler(exc, context)

    if response is None:
        if settings.DEBUG:
            return response # it's not an api exception (certainly the bug)

    # set error details
    error = {
        'reason': exc.__class__.__name__,
        'code': response.status_code if response else status.HTTP_400_BAD_REQUEST
    }

    details = exc.get_full_details() \
        if isinstance(exc, exceptions.APIException) else {}

    if isinstance(exc, exceptions.ValidationError):
        # yes, to use exc, not details here
        non_field_errors = exc.pop('non_field_errors', []) \
            if isinstance(exc, dict) else []
        non_field_errors = map(lambda s: str(s), non_field_errors) # stringify values

        # TODO: comment the code here...
        error['message'] = ' '.join(non_field_errors) or 'Validation errors'

        if details:
            error['errors'] = details

        if isinstance(response.data, dict):
            response.data.pop('non_field_errors', None)

        # experimental 
        # custom status codes
        for name in details:
            for item in details[name]:
                if type(item) is dict and item['code'] == 'unique':
                    error['code'] = status.HTTP_409_CONFLICT

    else:
        if isinstance(details, (tuple, list, dict)):
            all_errors = map(lambda s: str(s), details) # stringify values
            error['message'] = ' '.join(all_errors) or 'Uknown error'
            error['errors'] = details

        else:
            error['message'] = str(details) or 'Uknown error'

    response = Response({'error': error}, status=error['code'])

    return response
