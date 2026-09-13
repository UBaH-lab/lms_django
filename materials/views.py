from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer, SubscriptionSerializer
from users.permissions import IsOwner, IsNotModerator, IsModeratorOrOwner
from .paginators import CoursePaginator, LessonPaginator


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD для курса через ViewSet."""
    queryset = Course.objects.all().order_by('id')
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsNotModerator()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsModeratorOrOwner()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), IsNotModerator(), IsOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.request.user.groups.filter(name='moderators').exists():
            return Course.objects.all().order_by('id')
        return Course.objects.filter(owner=self.request.user).order_by('id')

    def get_serializer_context(self):
        """Передаём request в сериализатор для is_subscribed."""
        context = super().get_serializer_context()
        return context


class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all().order_by('id')
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsNotModerator()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.request.user.groups.filter(name='moderators').exists():
            return Lesson.objects.all().order_by('id')
        return Lesson.objects.filter(owner=self.request.user).order_by('id')


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsNotModerator(), IsOwner()]
        elif self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated(), IsModeratorOrOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)


class SubscriptionCreateAPIView(generics.CreateAPIView):
    """Подписка на курс."""
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')
        course = Course.objects.get(id=course_id)
        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            course=course
        )
        return Response(
            {'message': 'Подписка оформлена'},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class SubscriptionDestroyAPIView(generics.DestroyAPIView):
    """Отписка от курса."""
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        course_id = self.kwargs.get('course_id')
        return Subscription.objects.get(
            user=self.request.user,
            course_id=course_id
        )
