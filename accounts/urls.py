from django.urls import path, re_path
from .views import login_view, main_view, update_coins, student_list, shop_view, buy_product, logout, history_view, direction_list, month_list, lesson_detail, lesson_list, submit_task

urlpatterns = [
    path('', login_view, name='login'),
    path('main/', main_view, name='main'),
    path('dashboard/', student_list, name='student_list'),

    path('dashboard/<int:student_id>/<int:amount>/', update_coins, name='dashboard'),
    # re_path(r'^dashboard/(?P<student_id>[0-9])/(?P<amount>-?[0-9])/$', decrease_coins, name='dashboard'),
    re_path(r'^dashboard/(?P<student_id>[0-9])/(?P<amount>-?[0-9])/$', update_coins, name='dashboard'),

    # path('dashboard/<int:student_id>/<int:amount>/', decrease_coins, name='dashboard'),


    path('shop/', shop_view, name='shop'),
    path('shop/buy/<int:product_id>/', buy_product, name='buy_product'),
    path('logout/', logout, name='logout'),
    path('history/', history_view, name='history'),
    path('learn/', direction_list, name='direction_list'),
    path('learn/<int:direction_id>/', month_list, name='month_list'),
    path('learn/<int:direction_id>/<int:month_id>/', lesson_list, name='lesson_list'),
    path('learn/<int:direction_id>/<int:month_id>/<int:lesson_id>/', lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/submit/', submit_task, name='submit_task'),
]
