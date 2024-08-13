from rest_framework.routers import DefaultRouter
from borrowing.views import BorrowingViewSet

app_name = "borrowings"

router = DefaultRouter()
router.register("borrowings", BorrowingViewSet)

urlpatterns = router.urls
