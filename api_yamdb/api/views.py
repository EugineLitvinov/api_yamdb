from api.filters import TitleFilter

from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg

from rest_framework import (filters,
                            mixins,
                            permissions,
                            status,
                            viewsets,
                            pagination)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Title, Genre, Category, Review, Title
from users.models import User
from api.permissions import (AnonReadOnly,
                             IsSuperUserOrAdminAndIsAuth,
                             IsSuperUserOrAdminOrModerOrAuthorAndIsAuth)
from api.serializers import (TitleChangeSerializer,
                             TitleReadSerializer,
                             GenreSerializer,
                             CategorySerializer,
                             CommentSerializer,
                             ReviewSerializer,
                             UserSerializer,
                             UserCreateSerializer,
                             UserReceiveTokenSerializer)

from api.utils import send_confirmation_code


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUserOrAdminAndIsAuth,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = pagination.PageNumberPagination

    @action(
        detail=False,
        methods=['get', 'patch', 'delete'],
        url_path=r'(?P<username>[\w.@+-]+)',
        url_name='get_user'
    )
    def get_user_by_username(self, request, username):
        user = get_object_or_404(User, username=username)
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_me_data(self, request):
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data,
                partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serializer = UserCreateSerializer(data=request.data)
        username = request.data.get('username')
        email = request.data.get('email')
        if serializer.is_valid() or User.objects.filter(
            username=username,
            email=email
        ).exists():
            user, _ = User.objects.get_or_create(
                username=username,
                email=email
            )
            confirmation_code = default_token_generator.make_token(user)
            send_confirmation_code(
                email=user.email,
                confirmation_code=confirmation_code
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserReceiveTokenViewSet(mixins.CreateModelMixin,
                              viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserReceiveTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = UserReceiveTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            message = {'confirmation_code': 'Код подтверждения невалиден!'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        message = {'token': str(AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        Avg('reviews__score')
    ).order_by('name')
    permission_classes = (AnonReadOnly | IsSuperUserOrAdminAndIsAuth,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'head', 'delete', 'patch']
    pagination_class = pagination.PageNumberPagination

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return TitleReadSerializer
        else:
            return TitleChangeSerializer


class GenreCategoryViewSet(mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet,):
    permission_classes = (AnonReadOnly | IsSuperUserOrAdminAndIsAuth,)
    filter_backends = (filters.SearchFilter,)
    filterset_class = TitleFilter
    search_fields = ('name', 'slug',)
    lookup_field = 'slug'
    pagination_class = pagination.PageNumberPagination


class GenreViewSet(GenreCategoryViewSet,):
    queryset = Genre.objects.all().order_by('pk')
    serializer_class = GenreSerializer


class CategoryViewSet(GenreCategoryViewSet):
    queryset = Category.objects.all().order_by('pk')
    serializer_class = CategorySerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsSuperUserOrAdminOrModerOrAuthorAndIsAuth,)
    pagination_class = pagination.PageNumberPagination
    http_method_names = ['get', 'post', 'head', 'delete', 'patch']

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsSuperUserOrAdminOrModerOrAuthorAndIsAuth,)
    pagination_class = pagination.PageNumberPagination
    http_method_names = ['get', 'post', 'head', 'delete', 'patch']

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())
