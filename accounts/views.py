from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import User
from .serializers import CustomUserDetailsSerializer
import os
from rooms.models import Room
from rooms.serializers import RoomListSerializer
from django.contrib.auth import get_user_model


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update(request):
	serializer = CustomUserDetailsSerializer(request.user, data=request.data, partial=True)
	if serializer.is_valid(raise_exception=True):
		serializer.save()
		return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def likes(request):
	user = get_user_model().objects.get(id=request.user.id)
	rooms = user.like_rooms.all()
	serializer = RoomListSerializer(rooms, many=True)
	return Response(serializer.data)
