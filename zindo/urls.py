from rest_framework.routers import DefaultRouter

from . import viewsets

# Initialize default router
router = DefaultRouter()

# Route viewsets
router.register(
    "students",
    viewsets.StudentViewSet,
)
router.register(
    "textbooks",
    viewsets.TextBookViewSet,
)
router.register(
    "sheets",
    viewsets.SheetViewSet,
)
router.register(
    "records",
    viewsets.RecordViewSet,
)

urlpatterns = router.urls
