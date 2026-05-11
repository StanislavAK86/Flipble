from django.urls import path
from . import views

urlpatterns = [
    path('flip/', views.CoinFlipAPIView.as_view(), name='flip'),
    path('flip-cached/', views.CoinFlipWithCacheAPIView.as_view(), name='flip_cached'),
    path('therapy/start/', views.TherapyStartAPIView.as_view(), name='therapy_start'),
    path('therapy/chat/', views.TherapyChatAPIView.as_view(), name='therapy_chat'),
    path('therapy/conclusion/', views.TherapyConclusionAPIView.as_view(), name='therapy_conclusion'),
]