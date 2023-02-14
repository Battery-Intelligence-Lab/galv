from rest_framework.pagination import PageNumberPagination, BasePagination


class Unpaginatable(PageNumberPagination):
    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get('all', False) == 'true':
            return None

        return super(Unpaginatable, self).paginate_queryset(queryset, request, view=view)
