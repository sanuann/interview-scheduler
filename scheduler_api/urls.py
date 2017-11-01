# *****************************************************************************
# scheduler_api/urls.py
# *****************************************************************************

from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.routers import SimpleRouter

from scheduler import views

# *****************************************************************************
# urlpatterns
# *****************************************************************************

router = SimpleRouter()
router.register(r'calendars', views.InterviewCalendarViewSet)
router.register(r'interviews', views.InterviewViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
]
