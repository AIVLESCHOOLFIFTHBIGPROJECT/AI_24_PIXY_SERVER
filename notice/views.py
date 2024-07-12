from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Notice
from notice.serializers import NoticeSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])  # 어드민 유저만 공지사항 작성 가능
@authentication_classes([JWTAuthentication])  # JWT 토큰 확인
def notice_create(request):
    serializer = NoticeSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        # JWT 인증 사용시 인증객체를 통해 인증을 진행하고 사용자 정보를 request.user 객체에 저장
        # 인증정보가 없거나 일치하지않으면 AnonymousUser를 저장
        serializer.save(user=request.user)
        return Response({"공지사항 정보": serializer.data}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])  # 글 확인은 로그인 없이 가능
def notice_list(request):
    notice_list = Notice.objects.all()
    paginator = PageNumberPagination()

    # 페이지 사이즈를 주면 해당 사이즈로 지정
    # 값이 없으면 기본 사이즈로 설정(settings.py안에)
    page_size = request.GET.get('size') # request.GET['size']를 써도 되지만 size가 없다면 에러를 발생시킴
    if not page_size == None:           # request.GET.get('size')로 작성시 size가 없으면 None을 반환
        paginator.page_size = page_size

    result = paginator.paginate_queryset(notice_list, request)
    serializers = NoticeSerializer(result, many=True)
    return paginator.get_paginated_response(serializers.data)


@api_view(['GET'])
@permission_classes([AllowAny])  # 글 확인은 로그인 없이 가능
def notice_detail(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    serializer = NoticeSerializer(notice)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])  # 어드민 유저만 공지사항 수정 가능
@authentication_classes([JWTAuthentication])  # JWT 토큰 확인
def notice_update(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    # instance를 지정해줘야 수정될 때 해당 정보가 먼저 들어간 뒤 수정(안정적이다)
    serializer = NoticeSerializer(instance=notice, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])  # 어드민 유저만 공지사항 삭제 가능
@authentication_classes([JWTAuthentication])  # JWT 토큰 확인
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    notice.delete()
    return Response({"messages": "공지사항 삭제를 완료하였습니다."}, status=status.HTTP_200_OK)