from rest_framework.pagination import PageNumberPagination


class CoursePaginator(PageNumberPagination):
    """Пагинация для курсов."""
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20


class LessonPaginator(PageNumberPagination):
    """Пагинация для уроков."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
