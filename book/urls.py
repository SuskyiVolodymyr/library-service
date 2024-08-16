from rest_framework import routers

from book.views import BookViewSet


app_name = "books"

router = routers.DefaultRouter()
router.register("", BookViewSet, basename="books")

urlpatterns = router.urls
