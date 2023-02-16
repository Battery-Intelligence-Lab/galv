from rest_framework.pagination import PageNumberPagination, BasePagination


class Unpaginatable(PageNumberPagination):
    def paginate_queryset(self, queryset, request, view=None):
        s: str = request.query_params.get('all', "")
        falsy = ['false', 'f', '0', 'no', 'n']
        if s.lower() in falsy:
            return super(Unpaginatable, self).paginate_queryset(queryset, request, view=view)

        return None
