from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Host(models.Model):
    name = models.CharField(max_length=20)


class Type(models.Model):
    name = models.CharField(max_length=20)


class Option(models.Model):
    name = models.CharField(max_length=50)


class Room(models.Model):
    room_name = models.CharField(max_length=50)
    room_lat = models.DecimalField(max_digits=9, decimal_places=6)
    room_long = models.DecimalField(max_digits=9, decimal_places=6)
    room_address = models.CharField(max_length=50)
    room_des = models.TextField()
    room_max = models.IntegerField()
    room_type = models.ForeignKey(Type, blank=True, related_name='type_room', on_delete=models.CASCADE)
    room_option = models.ManyToManyField(Option, blank=True, related_name='options_room')
    room_booked = models.ManyToManyField(get_user_model(), null=True, through='Book', related_name='user_room')
    room_reviews = models.ManyToManyField(get_user_model(), null=True, through='Review', related_name='review_room')
    room_like_users = models.ManyToManyField(get_user_model(), related_name='like_rooms')
    room_host_name = models.ForeignKey(Host, on_delete=models.CASCADE)
    room_price = models.IntegerField()
    room_created_at = models.DateTimeField(auto_now_add=True)
    room_updated_at = models.DateTimeField(auto_now=True)

class Book(models.Model):
    book_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='booked_user')
    book_room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='booked_room')
    book_check_in = models.DateField()
    book_check_out = models.DateField()
    book_guest_count = models.IntegerField()

class Review(models.Model):
    review_author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_reviewed')
    review_room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_reviewed')
    review_score = models.FloatField()
    review_content = models.TextField()
    review_created_at = models.DateTimeField(auto_now_add=True)
    review_updated_at = models.DateTimeField(auto_now=True)


class Room_image(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_images')
    image_url = models.TextField(blank=True)






