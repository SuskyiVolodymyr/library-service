from rest_framework.routers import DefaultRouter
from borrowing.views import BorrowingViewSet

app_name = "borrowings"

router = DefaultRouter()
router.register("", BorrowingViewSet, basename="borrowing")

urlpatterns = router.urls
