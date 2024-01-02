from django.shortcuts import render, redirect
from .models import Room, Review, Book
from .serializers import RoomListSerializer, RoomSerializer, ReviewSerializer, BookSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import JsonResponse, HttpResponseForbidden
from datetime import timedelta, datetime
from django.db.models import Q
import requests



# Create your views here.

@api_view(['GET',])
def index(request):
    rooms = Room.objects.all()
    room_option = request.GET.getlist('option')
    room_type = request.GET.get('type')
    place = request.GET.getlist('place')
    count_p = request.GET.get('count_p')
    book_check_in = request.GET.get('book_check_in')
    book_check_out = request.GET.get('book_check_out')
    filtered_rooms = rooms

    if room_type:
        filtered_rooms = filtered_rooms.filter(room_type=room_type)

    if room_option:
        for option in room_option:
            filtered_rooms = filtered_rooms.filter(room_option__id__in=option)

    if place:  
        for p in place:
            filtered_rooms = filtered_rooms.filter(room_address__contains=p)

    if count_p:
        filtered_rooms = filtered_rooms.filter(room_max__gte=count_p)
    # 이상: __gte, 초과: __gt, 이하:__lte, 미만:__lt
    if book_check_in and book_check_out:
        check_in = datetime.strptime(book_check_in, "%Y-%m-%d")
        check_out = datetime.strptime(book_check_out, "%Y-%m-%d")
        
        booked_room_ids = Book.objects.filter(
            Q(book_check_in__lte=check_out, book_check_out__gte=check_in) |
            Q(book_check_in__gte=check_in, book_check_out__lte=check_out) |
            Q(book_check_in__lte=check_in, book_check_out__gte=check_out)
        ).values_list('book_room_id', flat=True)

        filtered_rooms = Room.objects.exclude(id__in=booked_room_ids)

    
    serializer = RoomListSerializer(filtered_rooms, many=True)
    if serializer.data:
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"message": "아쉽지만 맞는 숙소가 없네용"}, status=status.HTTP_204_NO_CONTENT)


# 두 날짜 사이의 모든 날짜를 list에 넣는 함수
def get_date_range(start_date, end_date, date_list):
    """
    Return a list of dates between start_date and end_date (inclusive).
    """
    # timedelta를 사용하여 날짜 간의 차이를 계산합니다.
    delta = timedelta(days=1)
    current_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += delta
    
    return date_list



@api_view(['GET', 'POST',])
def detail(request, room_id):
    room = Room.objects.get(id=room_id)
    room_serializer = RoomSerializer(room)

    if request.method == 'GET':
        return Response(room_serializer.data)
    
    # POST 로 보낼 시 create_book 기능
    elif request.method == 'POST':
        if request.user.is_authenticated:
            serializer = BookSerializer(data=request.data)
            current_date_list = []
            check_in_date = request.data.get('book_check_in')
            check_out_date = request.data.get('book_check_out')
            get_date_range(check_in_date, check_out_date, current_date_list)

            date_list = room_serializer.data['room_booked']

            print(current_date_list, date_list)

            if not set(current_date_list) & set(date_list):
                if serializer.is_valid():
                    serializer.save(book_user=request.user, book_room=room)
                    request.user.save()
                    return Response(serializer.data)
            else:
                return JsonResponse({'message': '이미 예약 완료된 날짜입니다.'})
    


@api_view(['POST',])
def create_review(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    books = get_list_or_404(Book, book_user=request.user, book_room=room_id)
    if books:
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(review_author=request.user, review_room=room)
            return Response(serializer.data)
    return HttpResponseForbidden('사용자는 해당 숙소에 예약되어 있지 않습니다.')

    

@api_view(['GET',])
def book_list(request, user_id):
    user = get_user_model().objects.get(id=user_id)
    books = Book.objects.filter(book_user=user)
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'DELETE':
        book.delete()
        return Response({"message": "Book deleted successfully."})
    

@api_view(['POST',])
@permission_classes([IsAuthenticated])
def likes(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.user in room.room_like_users.all():
        room.room_like_users.remove(request.user)
        is_like = False
    else:
        room.room_like_users.add(request.user)
        is_like = True

    # serializer = ArticleSerializer(article)
    return Response({'is_like': is_like})



@api_view(['POST',])
def kakaopay(request, book_id):
    User = get_user_model()
    user = get_object_or_404(User, id=request.user.id)
    book = get_object_or_404(Book, id=book_id)
    room = book.book_room
    print(request.data)
    if request.method == "POST":    
        URL = 'https://kapi.kakao.com/v1/payment/ready'
        headers = {
            "Authorization": "KakaoAK " + "c326394b30b7ffcdd06071217e622ef5",   # 서비스 어드민 키
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",  
        }
        params = {
            "cid": "TC0ONETIME",    # 변경불가. 실제로 사용하려면 카카오와 가맹을 맺어야함. 현재 코드는 테스트용 코드
            "partner_order_id": book_id,     # 주문번호 (스토어 번호_주문 번호)
            "partner_user_id": user.id,    # 유저 아이디
            "item_name": room.room_name,        # 구매 물품 이름
            "quantity": 1,                # 구매 물품 수량
            "total_amount": room.room_price,  # 구매 물품 가격
            "tax_free_amount": "0",         # 구매 물품 비과세 (0으로 고정)
            "approval_url": f"http://127.0.0.1:8000/rooms/{book_id}/kakaopay/approval/",    # 결제 성공 시 이동할 url
            "cancel_url": f"http://127.0.0.1:8000/rooms/",               # 결제 취소 시 이동할 url
            "fail_url": f"http://127.0.0.1:8000/rooms/",                 # 결제 실패 시 이동할 url
        }

        res = requests.post(URL, headers=headers, params=params)
        print(res.json())
        request.session['tid'] = res.json()['tid']  # 결제 승인시 사용할 tid를 세션에 저장
        request.session['order_id'] = book_id
        request.session['store_pk'] = room.id
        next_url = res.json()['next_redirect_pc_url']  # 결제 페이지로 넘어갈 url을 저장

        return redirect(next_url)


@api_view(['GET', 'POST',])
def approval(request, book_id):
    print(request.data)
    User = get_user_model()
    user = get_object_or_404(User, pk=request.user.pk)

    URL = 'https://kapi.kakao.com/v1/payment/approve'
    headers = {
        "Authorization": "KakaoAK " + "c326394b30b7ffcdd06071217e622ef5",   # 서비스 어드민 키
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",  # 변경불가
    }
    params = {
        "cid": "TC0ONETIME",    # 변경불가. 실제로 사용하려면 카카오와 가맹을 맺어야함. 현재 코드는 테스트용 코드
        "tid": request.session['tid'],  # 결제 요청시 세션에 저장한 tid
        "partner_order_id": request.session['order_id'],     # 주문번호
        "partner_user_id": user.id,    # 유저 아이디
        "pg_token": request.GET.get("pg_token"),     # 쿼리 스트링으로 받은 pg토큰
    }

    res = requests.post(URL, headers=headers, params=params)

    res = res.json()
    print(res)

    return JsonResponse({'message': 'kakaopay is completed.'})