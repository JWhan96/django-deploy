from django.urls import path
from . import views

app_name = 'rooms'
urlpatterns = [
    path('', views.index),
    path('<int:room_id>/', views.detail),
    path('<int:room_id>/likes/', views.likes),
    path('<int:room_id>/create_review/', views.create_review),
    path('<int:user_id>/book_list/', views.book_list),
    path('book/<int:book_id>/', views.book_detail),
    path('<int:book_id>/kakaopay/', views.kakaopay),
    path('<int:book_id>/kakaopay/approval/', views.approval)
    # path('create/', views.create),
    # path('<int:pk>/delete/', views.delete),
    # path('<int:pk>/update/', views.update),
]
