from rest_framework import serializers
from .models import Room, Review, Type, Option, Book, Room_image
from django.db.models import Avg
from datetime import timedelta, date


class ReviewSerializer(serializers.ModelSerializer):
    review_author = serializers.CharField(source='review_author.nickname', read_only=True)

    class Meta():
        model = Review
        fields = ['review_author', 'review_score', 'review_content', 'review_created_at', 'review_updated_at',]


class TypeSerializer(serializers.ModelSerializer):
    class Meta():
        model = Type
        fields = ['name',]


class OptionSerializer(serializers.ModelSerializer):
    class Meta():
        model = Option
        fields = ['name',]


class RoomImageSerializer(serializers.ModelSerializer):
    class Meta():
        model = Room_image
        fields = ['image_url',]


class RoomListSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(source='id', read_only=True)
    room_score = serializers.SerializerMethodField()
    room_reviews_count = serializers.IntegerField(source='room_reviewed.count', read_only=True)
    room_host = serializers.CharField(source='room_host_name.name', read_only=True)
    room_images = serializers.SerializerMethodField()
    room_booked = serializers.SerializerMethodField()

    class Meta():
        model = Room
        exclude = ['id', 'room_lat', 'room_long', 'room_des', 'room_reviews', 'room_host_name', 'room_created_at', 'room_updated_at',]
    
    def get_room_score(self, obj):
        av = Review.objects.filter(review_room=obj.id).aggregate(Avg('review_score')).get('review_score__avg')

        if av is None:
            return 0
        return round(av, 1)
    
    def get_room_images(self, obj):
        if obj.room_images.all():
            return [img.image_url for img in obj.room_images.all()]
        else:
            return "https://media.istockphoto.com/id/1454186576/ko/%EB%B2%A1%ED%84%B0/%EC%9D%B4%EB%AF%B8%EC%A7%80-%EC%B6%9C%EC%8B%9C-%EC%98%88%EC%A0%95-%EC%82%AC%EC%A7%84-%EA%B8%B0%ED%98%B8%EA%B0%80-%EC%97%86%EC%8A%B5%EB%8B%88%EB%8B%A4-%EC%82%AC%EC%9A%A9-%EA%B0%80%EB%8A%A5%ED%95%9C-%EC%8D%B8%EB%84%A4%EC%9D%BC%EC%9D%B4-%EC%97%86%EC%8A%B5%EB%8B%88%EB%8B%A4-%EA%B8%B0%EB%B3%B8-%EC%B6%95%EC%86%8C%ED%8C%90%EC%9D%84-%EC%82%AC%EC%9A%A9%ED%95%A0-%EC%88%98-%EC%9E%88%EC%8A%B5%EB%8B%88%EB%8B%A4-%EC%9D%B4%EB%AF%B8%EC%A7%80%EB%A5%BC-%EC%82%AC%EC%9A%A9%ED%95%A0-%EC%88%98-%EC%97%86%EC%9D%8C-%EC%95%84%EC%9D%B4%EC%BD%98%EC%9E%85%EB%8B%88%EB%8B%A4-%ED%94%84%EB%A1%9C%ED%95%84-%EC%82%AC%EC%A7%84-%EB%B2%A1%ED%84%B0-%EC%8A%A4%ED%86%A1-%EA%B7%B8%EB%A6%BC%EC%9E%85%EB%8B%88%EB%8B%A4.jpg?s=1024x1024&w=is&k=20&c=vXhGWLi02G8izNY-dAHP0E6tpfLOYQNw1jkHh_OJbKY="

    def get_room_booked(self, obj):
        books = Book.objects.filter(book_room_id=obj.id)
        date_list = []
        for book in books:
            get_date_range(book.book_check_in, book.book_check_out, date_list)

        return date_list

class BookSerializer(serializers.ModelSerializer):
    class Meta():
        model = Book
        fields = '__all__'
        read_only_fields = ('book_user', 'book_room',)

def get_date_range(start_date, end_date, date_list):
    """
    Return a list of dates between start_date and end_date (inclusive).
    """
    # timedelta를 사용하여 날짜 간의 차이를 계산합니다.
    delta = timedelta(days=1)
    
    # 시작 날짜부터 끝 날짜까지의 모든 날짜를 생성합니다.
    current_date = start_date
    
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += delta
    
    return date_list

class RoomSerializer(serializers.ModelSerializer):
    room_score = serializers.SerializerMethodField()
    room_score_count = serializers.SerializerMethodField()
    room_reviews_count = serializers.IntegerField(source='room_reviewed.count', read_only=True)
    host_name = serializers.CharField(source='room_host_name.name', read_only=True)
    room_type = serializers.CharField(source='room_type.name', read_only=True)
    room_option = serializers.SerializerMethodField()
    room_reviews = ReviewSerializer(source='room_reviewed', many=True, read_only=True)
    room_booked = serializers.SerializerMethodField()
    room_thumbnail = serializers.SerializerMethodField()
    room_images = serializers.SerializerMethodField()
    # image_url로 API작성 되어 있는데 어떻게 할지 회의


    class Meta():
        model = Room
        fields = '__all__'
    
    def get_room_score(self, obj):
        av = Review.objects.filter(review_room=obj.id).aggregate(Avg('review_score')).get('review_score__avg')

        if av is None:
            return 0
        return round(av, 2)
    

    def get_room_score_count(self, obj):
        score_list = []
        for i in range(1, 6):
            score_list.append(Review.objects.filter(review_room=obj.id, review_score=i).count())

        return score_list

    
    def get_room_option(self, obj):
        return [option.name for option in obj.room_option.all()]
    

    def get_room_thumbnail(self, obj):
        if not obj.room_images.all():
            return "https://media.istockphoto.com/id/1454186576/ko/%EB%B2%A1%ED%84%B0/%EC%9D%B4%EB%AF%B8%EC%A7%80-%EC%B6%9C%EC%8B%9C-%EC%98%88%EC%A0%95-%EC%82%AC%EC%A7%84-%EA%B8%B0%ED%98%B8%EA%B0%80-%EC%97%86%EC%8A%B5%EB%8B%88%EB%8B%A4-%EC%82%AC%EC%9A%A9-%EA%B0%80%EB%8A%A5%ED%95%9C-%EC%8D%B8%EB%84%A4%EC%9D%BC%EC%9D%B4-%EC%97%86%EC%8A%B5%EB%8B%88%EB%8B%A4-%EA%B8%B0%EB%B3%B8-%EC%B6%95%EC%86%8C%ED%8C%90%EC%9D%84-%EC%82%AC%EC%9A%A9%ED%95%A0-%EC%88%98-%EC%9E%88%EC%8A%B5%EB%8B%88%EB%8B%A4-%EC%9D%B4%EB%AF%B8%EC%A7%80%EB%A5%BC-%EC%82%AC%EC%9A%A9%ED%95%A0-%EC%88%98-%EC%97%86%EC%9D%8C-%EC%95%84%EC%9D%B4%EC%BD%98%EC%9E%85%EB%8B%88%EB%8B%A4-%ED%94%84%EB%A1%9C%ED%95%84-%EC%82%AC%EC%A7%84-%EB%B2%A1%ED%84%B0-%EC%8A%A4%ED%86%A1-%EA%B7%B8%EB%A6%BC%EC%9E%85%EB%8B%88%EB%8B%A4.jpg?s=1024x1024&w=is&k=20&c=vXhGWLi02G8izNY-dAHP0E6tpfLOYQNw1jkHh_OJbKY="
        else:
            return [img.image_url for img in obj.room_images.all()][0]

    def get_room_images(self, obj):
        img_cnt = obj.room_images.all().count() - 1

        if img_cnt >= 1:
            return [img.image_url for img in obj.room_images.all()][1:] + ["https://media.istockphoto.com/id/1454186576/ko/%EB%B2%A1%ED%84%B0/%EC%9D%B4%EB%AF%B8%EC%A7%80-%EC%B6%9C%EC%8B%9C-%EC%98%88%EC%A0%95-%EC%82%AC%EC%A7%84-%EA%B8%B0%ED%98%B8%EA%B0%80-%EC%97%86%EC%8A%B5%EB%8B%88%EB%8B%A4-%EC%82%AC%EC%9A%A9-%EA%B0%80%EB%8A%A5%ED%95%9C-%EC%8D%B8%EB%84%A4%EC%9D%BC%EC%9D%B4-%EC%97%86%EC%8A%B5%EB%8B%88%EB%8B%A4-%EA%B8%B0%EB%B3%B8-%EC%B6%95%EC%86%8C%ED%8C%90%EC%9D%84-%EC%82%AC%EC%9A%A9%ED%95%A0-%EC%88%98-%EC%9E%88%EC%8A%B5%EB%8B%88%EB%8B%A4-%EC%9D%B4%EB%AF%B8%EC%A7%80%EB%A5%BC-%EC%82%AC%EC%9A%A9%ED%95%A0-%EC%88%98-%EC%97%86%EC%9D%8C-%EC%95%84%EC%9D%B4%EC%BD%98%EC%9E%85%EB%8B%88%EB%8B%A4-%ED%94%84%EB%A1%9C%ED%95%84-%EC%82%AC%EC%A7%84-%EB%B2%A1%ED%84%B0-%EC%8A%A4%ED%86%A1-%EA%B7%B8%EB%A6%BC%EC%9E%85%EB%8B%88%EB%8B%A4.jpg?s=1024x1024&w=is&k=20&c=vXhGWLi02G8izNY-dAHP0E6tpfLOYQNw1jkHh_OJbKY="] * (4 - img_cnt)
        else:
            return ["https://media.istockphoto.com/id/1454186576/ko/%EB%B2%A1%ED%84%B0/%EC%9D%B4%EB%AF%B8%EC%A7%80-%EC%B6%9C%EC%8B%9C-%EC%98%88%EC%A0%95-%EC%82%AC%EC%A7%84-%EA%B8%B0%ED%98%B8%EA%B0%80-%EC%97%86%EC%8A%B5%EB%8B%88%EB%8B%A4-%EC%82%AC%EC%9A%A9-%EA%B0%80%EB%8A%A5%ED%95%9C-%EC%8D%B8%EB%84%A4%EC%9D%BC%EC%9D%B4-%EC%97%86%EC%8A%B5%EB%8B%88%EB%8B%A4-%EA%B8%B0%EB%B3%B8-%EC%B6%95%EC%86%8C%ED%8C%90%EC%9D%84-%EC%82%AC%EC%9A%A9%ED%95%A0-%EC%88%98-%EC%9E%88%EC%8A%B5%EB%8B%88%EB%8B%A4-%EC%9D%B4%EB%AF%B8%EC%A7%80%EB%A5%BC-%EC%82%AC%EC%9A%A9%ED%95%A0-%EC%88%98-%EC%97%86%EC%9D%8C-%EC%95%84%EC%9D%B4%EC%BD%98%EC%9E%85%EB%8B%88%EB%8B%A4-%ED%94%84%EB%A1%9C%ED%95%84-%EC%82%AC%EC%A7%84-%EB%B2%A1%ED%84%B0-%EC%8A%A4%ED%86%A1-%EA%B7%B8%EB%A6%BC%EC%9E%85%EB%8B%88%EB%8B%A4.jpg?s=1024x1024&w=is&k=20&c=vXhGWLi02G8izNY-dAHP0E6tpfLOYQNw1jkHh_OJbKY="] * 4
    
    def get_room_booked(self, obj):
        books = Book.objects.filter(book_room_id=obj.id)
        date_list = []
        for book in books:
            get_date_range(book.book_check_in, book.book_check_out, date_list)

        return date_list









