from django.contrib import admin
from .models import Movie, Session, Employee, User, Ticket, Hall

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'duration')
    search_fields = ('title',)

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'hall', 'viewers', 'movie', 'start_time', 'end_time')
    search_fields = ('movie__title',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'work_position', 'age', 'hourly_salary')
    search_fields = ('first_name', 'last_name')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'birth_date')
    search_fields = ('first_name', 'last_name')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'expiration_time')
    search_fields = ('session__movie__title',)

@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'max_seats')
    search_fields = ('name',)