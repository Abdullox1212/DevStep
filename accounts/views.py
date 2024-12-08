from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Product, PurchaseHistory, NewsImage, Direction, Month, Lesson
from django.contrib import messages
import requests

def login_view(request):
    if request.method == 'POST':
        modme_id = request.POST.get('modme_id')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(modme_id=modme_id)  # Foydalanuvchini modme_id orqali olish
            print(user.password)
            if password == user.password:  # Parolni tekshirish
                request.session['user_id'] = user.id  # Sessiyaga foydalanuvchini saqlash
                request.session['modme_id'] = modme_id
                return redirect('main')  # Muvaffaqiyatli kirish holatida yo'naltirish
            else:
                return render(request, 'login.html', {'error': 'Modme ID yoki parol noto‘g‘ri'})
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'Modme ID yoki parol noto‘g‘ri'})

    return render(request, 'login.html')


def logout(request):
    return login_view(request)

def main_view(request):
    images = NewsImage.objects.all()    
    modme_id = request.session.get('modme_id')
    if not modme_id:
        return redirect('login')  # Agar modme_id mavjud bo‘lmasa, login sahifasiga qaytaramiz



    try:
        user = User.objects.get(modme_id=modme_id)



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
            'images': images,
            'user': user,
        }
        return render(request, 'index.html', context)
    except User.DoesNotExist:
        return redirect('login')  # Agar user topilmasa, login sahifasiga qaytaramiz
    


def student_list(request):
    students = User.objects.all()
    return render(request, 'dashboard.html', {'students': students})

def update_coins(request, student_id, amount):
    student = User.objects.get(id=student_id)
    modme_id = request.POST.get('modme_id')

    if amount <= 2 and amount != 1:
        student.total_coins -= amount
        student.coins_today -= amount
        student.save()  
        return redirect('dashboard')
    else:
        student.total_coins += amount
        student.coins_today += amount
        student.save()
        return redirect('dashboard')


    

    
def shop_view(request):
    products = Product.objects.all()
    return render(request, 'shop.html', {'products': products})




def buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # user = get_object_or_404(User, id=request.user.id)  
    modme_id = request.session.get('modme_id')
    user = User.objects.get(modme_id=modme_id)  # Foydalanuvchini modme_id orqali olish


    if user.total_coins < product.price:
        messages.error(request, "")
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


    url = f"https://api.telegram.org/bot6824723033:AAGp5vLJnkuFgnLT9Xrrsy1nNea8ECRcDdw/sendPhoto"
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
    return render(request, 'okey.html', {'msg': f'{product.name}ni sotib oldingiz! ', 'ssg': f"Shanba kuni sizda {product.name}ni topshiramiz!" })




def history_view(request):
    modme_id = request.session.get('modme_id')
    if not modme_id:
        return redirect('login')
    

    user = User.objects.filter(modme_id=modme_id).first()
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



from django.core.mail import send_mail
from django.http import JsonResponse
import requests


def send_to_telegram(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {'chat_id': chat_id, 'text': message}
    requests.post(url, data=data)

def submit_task(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    modme_id = request.session.get('modme_id')
    user = User.objects.get(modme_id=modme_id)
    if request.method == "POST":
        zip_file = request.FILES.get('zip_file')
        link = request.POST.get('link')
        comment = request.POST.get('comment')
        
        # Adminga xabar yuborish
        admin_message = f"""
        Vazifa yuborildi:
        - O'quvchi: {user.name}
        - Dars: {lesson.title}
        - Guruh: {user.group.name}
        - Izoh: {comment}
        """
        if zip_file:
            admin_message += f"\nFayl: {zip_file.name}"
        if link:
            admin_message += f"\nLink: {link}"
        
        # Telegram botga yuborish yoki email jo'natish (masalan):
        send_to_telegram("7468217626:AAEI6PsD5wjUlXlRDcdftxi2vnn9udebj80", "7149602547", admin_message)
        
        # Sahifaga qaytarish
        return redirect('direction_list')
    
    return JsonResponse({'error': "Faqat POST so'rovlari qabul qilinadi!"})