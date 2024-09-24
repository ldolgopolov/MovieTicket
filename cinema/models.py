from django.db import models

# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.DurationField()
    def __str__(self):
        return self.title

class Hall(models.Model):
    name = models.CharField(max_length=100)
    max_seats = models.PositiveBigIntegerField(default=100)
    def __str__(self):
        return self.name


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    viewers = models.PositiveIntegerField(default=0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.end_time:
            self.end_time = self.start_time + self.movie.duration
            super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.movie.title} {self.start_time}'
    
class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    work_position = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    hourly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.work_position}'
    
class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    tickets = models.ManyToManyField('Ticket', related_name='users')
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
class Ticket(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    seat = models.PositiveIntegerField(null=True)
    purchase_time = models.DateTimeField(auto_now_add=True, null=True)
    expiration_time = models.DateTimeField()
    def __str__(self):
        return f'Ticket for {self.session.movie.title} (Session: {self.session.start_time})'