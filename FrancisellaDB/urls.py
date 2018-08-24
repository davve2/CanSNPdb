"""FrancisellaDB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from django.contrib.auth import views as auth_views

from francisella_web.views import (
    HomeView,
    WikiView,
    SubmitView,
    AnalysisView,
    FormView,
    get_tree_data,
    ProcessView,
    databaseRequest
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name="home"),
    path('wiki/', WikiView.as_view(), name="wiki"),
    path('submission/', SubmitView.as_view(success_url="/processSubmission/"), name="submission"),
    path('analysis/', AnalysisView.as_view(), name="analysis"),
    #path('submission/', FormView.as_view(), name="submission"),
    path('get_tree/', get_tree_data, name="analysis"),
    path('databaseRequest/', databaseRequest, name="databaseRequest"),
    path('processSubmission/',ProcessView.as_view(),name="processSubmission"),
    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout, {'next_page': '/'}, name='logout')
    
    
]

from django.conf.urls.static import static
from django.conf import settings

if settings.DEBUG:
	pass #urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)