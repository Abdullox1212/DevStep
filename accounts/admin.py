from django.contrib import admin
from .models import User, Group, Product, NewsImage
from .models import Direction, Month, Lesson, Video

admin.site.register(User)

admin.site.register(Group)

admin.site.register(Product)

admin.site.register(NewsImage)


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Month)
class MonthAdmin(admin.ModelAdmin):
    list_display = ('name', 'direction')
    list_filter = ('direction',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'month', 'link', 'zip_file')
    list_filter = ('month',)
    search_fields = ('title',)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'video_id')
    list_filter = ('category',)
    search_fields = ('title', 'video_id')    