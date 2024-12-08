from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=100)
    time = models.CharField(max_length=30)
    teacher = models.CharField(max_length=100)


    def __str__(self):
        return self.name
    


class User(models.Model):
    name = models.CharField(max_length=100)
    modme_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    level = models.IntegerField(default=1)
    last_visit = models.DateField(default=0)
    total_coins = models.IntegerField(default=0)
    coins_today = models.IntegerField(default=0)

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='groups', null=True, blank=True)
    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)


    def __str__(self):
        return f"{self.modme_id} {self.name}"




class Product(models.Model):
    name = models.CharField(max_length=100)  # Mahsulot nomi
    price = models.IntegerField()  # Mahsulot narxi
    photo = models.ImageField(upload_to='products/')  # Mahsulot rasmi
    stock = models.IntegerField(default=0)  # Zaxiradagi soni

    def __str__(self):
        return self.name
    

class PurchaseHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_histories')
    product = models.ForeignKey(Product, related_name='product', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.product.name} ({self.quantity})"



class NewsImage(models.Model):
    title = models.CharField(max_length=100)  # Rasm nomi
    photo = models.ImageField(upload_to='news_images/')  # Rasm joylashuvi

    def __str__(self):
        return self.title
    


class Direction(models.Model):  # Yo'nalish
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Month(models.Model):  # Oylik kurslar
    name = models.CharField(max_length=50)
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name="months")

    def __str__(self):
        return f"{self.name} ({self.direction.name})"


class Lesson(models.Model):  # Darslar
    title = models.CharField(max_length=100)
    description = models.TextField()
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name="lessons")
    zip_file = models.FileField(upload_to="lessons/zips/", blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.month.name})"    