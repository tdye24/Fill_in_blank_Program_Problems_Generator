"""Fill_in_blank_Program_Problems_Generator URL Configuration

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
from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import view

urlpatterns = [
    url(r'^$', view.index),
	url(r'^getProblemList$', view.get_problem_list),
	url(r'^getProblemById$', view.get_problem_by_id),
	url(r'^getProblemByTheme$', view.get_problem_by_theme),
	url(r'^getProblemByKeyword$', view.get_problem_by_keyword),
	url(r'^getStatusList$', view.get_status_list),
	url(r'^getRanklist$', view.get_ranklist),
    url(r'^register$', view.register),
	url(r'^user$', view.user),
	url(r'^teacher$', view.teacher),
	url(r'^upload$', view.upload),
	url(r'^generation$', view.generation),
	url(r'^submit$', view.submit),
	url(r'^admin$', view.admin),
]


urlpatterns += staticfiles_urlpatterns()
