from importlib import import_module, util
from django.urls import include, path
from django.contrib.auth import get_user_model

UserModel = get_user_model()


def get_url_modules(package):
  modules = []
  device_module_short_names = [
      x.__module__.split('.')[-1] for x in UserModel.get_device_classes()
  ]

  for name in device_module_short_names:
      try:
          modules.append(import_module('..' + name + '.urls', package=package))
      except (ModuleNotFoundError, ImportError):
          pass

  return modules


urlpatterns = [
    path(r'^', include(x)) for x in get_url_modules(__name__)
]
