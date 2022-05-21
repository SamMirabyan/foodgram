from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class PageLimitPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'
    max_page_size = 10


class RecipesLimitPagination(LimitOffsetPagination):
    default_limit = 6
    limit_query_param = 'recipes_limit'

    def get_offset(self, request):
        '''
        Всегда возвращаем 0, чтобы рецепты в выдаче шли с самого начала.
        '''
        return 0
