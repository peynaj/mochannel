"""project1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from rest_framework_jwt import views as jwt_views
from rest_framework_swagger.views import get_swagger_view
from django.conf import settings
from django.conf.urls.static import static


schema_view = get_swagger_view(title='Mobtaker Channels API')

urlpatterns = [
    # admin
    #path('admin/', admin.site.urls),
    
    # api doc
    path('api-doc/', schema_view),

    # login & logout for using protected APIs by swagger UI
    path('accounts/login/', LoginView.as_view()),
    path('accounts/logout/', LogoutView.as_view()),

    # auth
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # jwt 
    path('auth/token/', jwt_views.ObtainJSONWebToken.as_view(), name='token_obtain'),
    path('auth/token/refresh/', jwt_views.RefreshJSONWebToken.as_view(), name='token_refresh'),
    path('auth/token/verify/', jwt_views.VerifyJSONWebToken.as_view(), name='token_verify'),
    
    # user
    path('user/', include('app.user.urls')),

    # channel
    path('channel/', include('app.channel.urls')),

    # past
    path('post/', include('app.post.urls')),
]

# serve uploaded files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
