from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Product, PurchaseHistory, NewsImage, Direction, Month, Lesson, Group
from django.contrib import messages
import requests
import sqlite3



def get_telegram_id_by_modme_id(modme_id):
    # SQLite ulanishini yaratish
    connection = sqlite3.connect('db.sqlite3')
    cursor = connection.cursor()

    # `modme_id` bilan tekshirish
    cursor.execute("SELECT telegram_bot_register FROM accounts_user WHERE modme_id = ?", (modme_id,))
    result = cursor.fetchone()

    # Ulanishni yopish
    connection.close()

    # Agar natija mavjud bo'lsa, uni qaytarish, aks holda None
    if result:
        return result[0]
    return "aaaaaaaaaaaaaaaaaaaa"


from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
@csrf_protect
def login_view(request):
    if request.method == 'POST':
        modme_id = request.POST.get('modme_id')
        password = request.POST.get('password')

        user = User.objects.filter(modme_id=modme_id).first()  # Foydalanuvchini topish
        if user and user.password == password:  # Parolni tekshirish
            if user.payment_status == 'paid':
                request.session['user_id'] = user.id  # Foydalanuvchini sessiyada saqlash
                user.last_visit = timezone.now()  # Kirgan vaqtini yangilash
                user.save()
                
                return redirect('main')
            else:
                return render(request, 'login.html', {'error': f'{user.name}, To‘lovni amalga oshirmagansiz!'})

        else:
            return render(request, 'login.html', {'error': 'Modme ID yoki parol noto‘g‘ri'})
    return render(request, 'login.html')


def logout(request):
    request.session.flush()  # Sessiyani tozalash
    return redirect('login')


def main_view(request):
    user_id = request.session.get('user_id')  # Sessiyadan foydalanuvchi ID ni olish
    if not user_id:
        return redirect('login')  # Foydalanuvchi sessiyasiz bo'lsa, login sahifasiga qaytarish

    user = User.objects.filter(id=user_id).first()
    if not user:
        request.session.flush()  # Agar user topilmasa, sessiyani o'chirish
        return redirect('login')

    # Levelni hisoblash
    if user.total_coins < 100:
        user.level = 1
    elif user.total_coins < 200:
        user.level = 2
    elif user.total_coins < 300:
        user.level = 3
    elif user.total_coins < 400:
        user.level = 4
    elif user.total_coins < 500:
        user.level = 5

    context = {
        'images': NewsImage.objects.all(),
        'user': user,
    }
    return render(request, 'index.html', context)



def group_list(request):
    user_id = request.session.get('user_id')  # Sessiyadan foydalanuvchi ID ni olish
    if not user_id:
        return redirect('login')  # Sessiya mavjud emas

    user = User.objects.filter(id=user_id).first()  # Foydalanuvchini olish
    if not user:  
        request.session.flush()  # Yaroqsiz sessiya tozalanadi
        return redirect('login')

    # Admin sifatida tekshirish (masalan, maxsus modme_id orqali)
    if user.is_admin:
        groups = Group.objects.all()  # Barcha guruhlarni olish
        return render(request, 'group_dashboard.html', {'groups': groups})

    # Huquqsiz foydalanuvchini qaytarish
    return redirect('login')


def student_list(request, group_id):
    group = get_object_or_404(Group, id=group_id) 
    students = User.objects.filter(group=group)
    return render(request, 'dashboard.html', {'students': students})



def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot7468217626:AAEI6PsD5wjUlXlRDcdftxi2vnn9udebj80/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:

        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Xabar yuborildi!")
        else:
            print(f"Xatolik: {response.status_code}, javob: {response.text}")
    except Exception as e:
        print(f"Xabar yuborishda xatolik: {e}")




def update_coins(request, student_id, amount):
    student = User.objects.get(id=student_id)


    if amount <= 2 and amount != 1:
        student.total_coins -= amount
        student.save()  
            
        return redirect('group_list')
    else:
        student.total_coins += amount
        student.save()

        return redirect('group_list')






    
def shop_view(request):
    products = Product.objects.all()
    return render(request, 'shop.html', {'products': products})




def buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user_id = request.session.get('user_id')  # Sessiyadan foydalanuvchi ID ni olish
    if not user_id:
        return redirect('login') 
    

    user = User.objects.filter(id=user_id).first() # Foydalanuvchini modme_id orqali olish


    if user.total_coins < product.price:
        return render(request, 'okey.html', {'msg': 'Coinlaringiz yetarli emas!'})
        # return redirect('shop')  # Mablag‘ yetarli bo‘lmasa shop sahifasiga qaytaradi

    if product.stock <= 0:
        return render(request, 'okey.html', {'msg': f'Mahsulot qolmadi!'})
        # return redirect('shop')

    # Coinlarni kamaytirish va mahsulot zaxirasini yangilash
    user.total_coins -= product.price
    user.save()
    product.stock -= 1
    product.save()

    # Adminga xabar yuborish (admin pochta orqali xabardor qilinishi mumkin)
    # Adminga email yuborish kerak bo'lsa shu yerda yozing

    PurchaseHistory.objects.create(user=user, product=product, quantity=1)


    image = product.photo.path

    message = f"""
📃 Yangi buyurtma❗️\n\n
🤵 Foydalanuvchi: {user.name}\n
👥 Guruhi: {user.group.name}\n
📦 Mahsulot: {product.name}\n
💸 Narxi: {product.price} 🪙\n
💸 Qolgan Coinlar: {user.total_coins} 🪙\n"""


    url = f"https://api.telegram.org/bot7468217626:AAEI6PsD5wjUlXlRDcdftxi2vnn9udebj80/sendPhoto"
    with open(image, "rb") as file:
        response = requests.post(
            url,
            data={"chat_id": 7149602547, "caption": message},
            files={"photo": file},
        )


    if response.status_code == 200:
        print("Xabar muvaffaqiyatli yuborildi!")
    else:
        print(f"Xato: {response.text}")
    return render(request, 'okey.html', {'msg': f'{product.name}ni sotib oldingiz! ', 'ssg': f"Shanba kuni sizga {product.name}ni topshiramiz!" })




def history_view(request):
    user_id = request.session.get('user_id')  # Sessiyadan foydalanuvchi ID ni olish
    if not user_id:
        return redirect('login') 
    

    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect('login')
    else:
        histories = PurchaseHistory.objects.filter(user=user).order_by('-purchased_at')

    return render(request, 'history.html', {'histories': histories})




def direction_list(request):
    directions = Direction.objects.all()
    return render(request, 'direction_list.html', {'directions': directions})


def month_list(request, direction_id):
    direction = get_object_or_404(Direction, pk=direction_id)
    months = direction.months.all()
    return render(request, 'month_list.html', {'direction': direction, 'months': months})

def lesson_list(request, direction_id, month_id):
    # Yo'nalish va oy obyektlarini topamiz
    direction = get_object_or_404(Direction, id=direction_id)
    month = get_object_or_404(Month, id=month_id)
    
    # Shu oyga tegishli barcha darslarni olamiz
    lessons = Lesson.objects.filter(month=month)
    
    return render(request, 'lesson_list.html', {
        'direction': direction,
        'month': month,
        'lessons': lessons
    })


def lesson_detail(request, direction_id, month_id, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    if request.method == 'POST':
        download_type = request.POST.get('download_type')
        user_info = {
            'user': request.user,
            'lesson': lesson,
            'type': download_type,
        }
        # Bu yerda adminga xabar yuborish mexanizmini amalga oshiring
    return render(request, 'lesson_detail.html', {'lesson': lesson})





import os
import requests
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from .models import Lesson, User

# Telegramga fayl yoki link yuborish funksiyasi
def send_file_to_telegram(bot_token, chat_id, file_path=None, caption=None):
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument" if file_path else f"https://api.telegram.org/bot{bot_token}/sendMessage"
    if file_path:
        with open(file_path, 'rb') as file:
            files = {'document': file}
            data = {'chat_id': chat_id, 'caption': caption}
            response = requests.post(url, files=files, data=data)
    else:
        data = {'chat_id': chat_id, 'text': caption}
        response = requests.post(url, data=data)
    return response

# Vazifa jo'natish funksiyasi
def submit_task(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    user_id = request.session.get('user_id')  # Sessiyadan foydalanuvchi ID ni olish
    if not user_id:
        return redirect('login')  # Sessiya mavjud emas
    
    user = get_object_or_404(User, id=user_id)  # Foydalanuvchini olish

    if request.method == "POST":
        zip_file = request.FILES.get('zip_file')  # Foydalanuvchi yuklagan fayl
        link = request.POST.get('link')  # Foydalanuvchi yuborgan link
        comment = request.POST.get('comment')  # Izoh

        # Faylni vaqtincha saqlash va yuborish
        if zip_file:
            file_path = f"/tmp/{zip_file.name}"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'wb') as f:
                for chunk in zip_file.chunks():
                    f.write(chunk)

            # Telegramga yuboriladigan caption
            caption = f"""
Vazifa yuborildi:
- O'quvchi: {user.name}
- Yo'nalish: {lesson.month.direction.name}
- Dars: {lesson.title}
- Guruh: {user.group.name}
- Izoh: {comment or "Yo'q"}
            """
            send_file_to_telegram(
                bot_token="7468217626:AAEI6PsD5wjUlXlRDcdftxi2vnn9udebj80",
                chat_id="7149602547",
                file_path=file_path,
                caption=caption.strip()
            )
            messages.success(request, "Fayl muvaffaqiyatli yuborildi!")
            return redirect("direction_list")

        # Linkni yuborish
        elif link:
            caption = f"""
Yangi vazifa yuborildi:
- O'quvchi: {user.name}
- Yo'nalish: {lesson.month.direction.name}
- Dars: {lesson.title}
- Guruh: {user.group.name}
- Izoh: {comment or "Yo'q"}
- Link: {link}
            """
            send_file_to_telegram(
                bot_token="7468217626:AAEI6PsD5wjUlXlRDcdftxi2vnn9udebj80",
                chat_id="7149602547",
                caption=caption.strip()
            )
            messages.success(request, "Link muvaffaqiyatli yuborildi!")
            return redirect("direction_list")

        # Ikkalasi ham yo'q bo'lsa
        else:
            messages.error(request, "Fayl yoki link yuborilmadi! Iltimos, qayta urining.")
            return render(request, "lesson_detail.html", {"lesson": lesson})

    return render(request, "lesson_detail.html", {"lesson": lesson})


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def update_payment_status(request, student_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        payment_status = data.get('payment_status')

        user = User.objects.filter(id=student_id).first()
        if user:
            user.payment_status = payment_status  # To‘lov holatini yangilash
            user.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Talaba topilmadi'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Noto‘g‘ri so‘rov'}, status=400)


from django.core.management.base import BaseCommand
from accounts.models import User
from django.utils import timezone

class Command(BaseCommand):
    help = 'Reset payment status to unpaid for all students'

    def handle(self, *args, **kwargs):
        students = User.objects.all()
        for student in students:
            student.payment_status = 'unpaid'
            student.save()
        self.stdout.write(self.style.SUCCESS('Successfully reset payment status for all students'))



def not_working(request):
    return render(request, 'not_working.html')        