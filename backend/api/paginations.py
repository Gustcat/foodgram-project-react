from rest_framework.pagination import PageNumberPagination


class ShoppingCartPagination(PageNumberPagination):
    page_size = 6

    def get_page_size(self, request):
        if 'is_in_shopping_cart' in request.query_params:
            user = request.user
            return user.shopping.all().count()
        return self.page_size
