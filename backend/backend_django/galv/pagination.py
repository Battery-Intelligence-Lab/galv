# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

from rest_framework.pagination import PageNumberPagination, BasePagination


class Unpaginatable(BasePagination):
    def paginate_queryset(self, queryset, request, view=None):
        # s: str = request.query_params.get('all', "")
        # falsy = ['false', 'f', '0', 'no', 'n']
        # if s.lower() in falsy or request.query_params.get('page', None):
        #     page_num = PageNumberPagination
        #     return page_num.paginate_queryset(
        #         PageNumberPagination(),
        #         queryset=queryset,
        #         request=request,
        #         view=view
        #     )

        return None
