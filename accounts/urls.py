from django.urls import path, re_path
from .views import login_view, main_view, update_coins, group_list, shop_view, buy_product, logout, history_view, direction_list, month_list, lesson_detail, lesson_list, submit_task, student_list, update_payment_status, not_working

urlpatterns = [
    path('', login_view, name='login'),
    path('main/', main_view, name='main'),
    path('dashboard/', group_list, name='group_list'),
    path('dashboard/group/<int:group_id>/', student_list, name='group_students'),
    path('dashboard/<int:student_id>/<int:amount>/', update_coins, name='dashboard'),

    path('shop/', shop_view, name='shop'),
    path('shop/buy/<int:product_id>/', buy_product, name='buy_product'),
    path('logout/', logout, name='logout'),
    path('history/', history_view, name='history'),
    path('learn/', direction_list, name='direction_list'),
    path('learn/<int:direction_id>/', month_list, name='month_list'),
    path('learn/<int:direction_id>/<int:month_id>/', lesson_list, name='lesson_list'),
    path('learn/<int:direction_id>/<int:month_id>/<int:lesson_id>/', lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/submit/', submit_task, name='submit_task'),    
    path('update_payment_status/<int:student_id>/', update_payment_status, name='update_payment_status'),
]
# urlpatterns = [
#     path('', not_working, name='login'),
#     path('main/', not_working, name='main'),
#     path('dashboard/', not_working, name='group_list'),
#     path('dashboard/group/<int:group_id>/', not_working, name='group_students'),
#     path('dashboard/<int:student_id>/<int:amount>/', not_working, name='dashboard'),

#     path('shop/', not_working, name='shop'),
#     path('shop/buy/<int:product_id>/', not_working, name='buy_product'),
#     path('logout/', not_working, name='logout'),
#     path('history/', not_working, name='history'),
#     path('learn/', not_working, name='direction_list'),
#     path('learn/<int:direction_id>/', not_working, name='month_list'),
#     path('learn/<int:direction_id>/<int:month_id>/', not_working, name='lesson_list'),
#     path('learn/<int:direction_id>/<int:month_id>/<int:lesson_id>/', not_working, name='lesson_detail'),
#     path('lesson/<int:lesson_id>/submit/', not_working, name='submit_task'),    
#     path('update_payment_status/<int:student_id>/', not_working, name='update_payment_status'),
# ]


