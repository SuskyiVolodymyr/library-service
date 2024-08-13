from django.urls import include, path
from rest_framework import routers

from book.views import BookViewSet

app_name = "books"

router = routers.DefaultRouter()
router.register("book", BookViewSet)

urlpatterns = [path("", include(router.urls))]
