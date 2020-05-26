from django.urls import include, path

from .me import views as me_views
from .auth import views as auth_views

from .views import IndexView
from .schema import ShemaView

app_name = 'api'
urlpatterns = [
    # path('', IndexView.as_view()), # swagger doesn't get it :/

    path('me/', me_views.MeView.as_view(), name='me'),
    path('me/password/', me_views.MePasswordView.as_view(), name='me-password'),
    path('me/passcode/', me_views.MePasscodeView.as_view(), name='me-passcode'),
    path('me/pushcode/', me_views.MePushcodeView.as_view(), name='me-pushcode'),

    path('signin/', auth_views.SigninView.as_view(), name='signin'),
    path('signup/', auth_views.SignupView.as_view(), name='signup'),
    path('signup/verification/', auth_views.SignupVerificationView.as_view(), name='signup-verification'),
    path('signup/verification/phone/', auth_views.SignupVerificationPhoneView.as_view(), name='signup-verification-phone'),
    path('signup/verification/email/', auth_views.SignupVerificationEmailView.as_view(), name='signup-verification-email'),
    path('signup/verification/email/<str:key>', auth_views.SignupVerificationEmailKeyView.as_view(), name='signup-verification-email-key'),

    # demo
    path('docs/', ShemaView.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
]
