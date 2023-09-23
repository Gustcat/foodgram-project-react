import io

from django.db.models import Sum
from django.http import FileResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status, mixins, exceptions
from rest_framework.response import Response
from rest_framework import permissions
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from recipes.models import (Ingredient,
                            Tag,
                            Recipe,
                            Favourite,
                            ShoppingCart,
                            RecipeIngredient)
from users.models import Subscription
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeReadSerializer,
                          RecipeWriteSerializer,
                          SubscribeSerializer,
                          RecipeShortSerializer)
from .permissions import AuthorOrReadOnly
from .filters import RecipeFilter


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for getting tag list or tag details.
    """
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for getting ingredient list or ingredient details.
    It supports searching by name.
    """
    filter_backends = (filters.SearchFilter,)
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing recipes.
    This ViewSet provides endpoints for creating, reading,
    updating, and deleting recipes.
    It supports filtering, ordering, and permissions.
    """
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    permission_classes = (AuthorOrReadOnly,)
    ordering = ('-pub_date',)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer


class SubscriptionViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
    ViewSet getting user subscription list.
    """
    serializer_class = SubscribeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        subscriber = self.request.user
        return User.objects.filter(subscribing__subscriber=subscriber)


class SubscribeViewSet(viewsets.ModelViewSet):
    """
    ViewSet provides to add and remove subscription on a user.
    """
    serializer_class = SubscribeSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        subscribing = get_object_or_404(User, id=self.kwargs.get('user_id'))
        serializer = self.get_serializer(instance=subscribing)
        Subscription.objects.create(subscriber=request.user,
                                    subscribing=subscribing)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def destroy(self, request, *args, **kwargs):
        subscribing = get_object_or_404(User, id=self.kwargs.get('user_id'))
        try:
            subscription = Subscription.objects.get(
                subscriber=request.user,
                subscribing=subscribing)
        except Subscription.DoesNotExist:
            raise exceptions.ValidationError(
                'Нет подписки на этого пользователя')
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    """
        ViewSet provides to add and remove recipe to favorites.
    """
    serializer_class = RecipeShortSerializer
    queryset = Recipe.objects.all()

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        serializer = self.get_serializer(instance=recipe)
        Favourite.objects.create(user=self.request.user, recipe=recipe)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def destroy(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        try:
            favorite = Favourite.objects.get(
                user=self.request.user,
                recipe=recipe)
        except Favourite.DoesNotExist:
            raise exceptions.ValidationError('Этого рецепта нет в избранном')
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """
        ViewSet provides to add and remove recipe to shopping cart.
    """
    serializer_class = RecipeShortSerializer
    queryset = Recipe.objects.all()

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        serializer = self.get_serializer(instance=recipe)
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def destroy(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        try:
            shopping = ShoppingCart.objects.get(user=self.request.user,
                                                recipe=recipe)
        except ShoppingCart.DoesNotExist:
            raise exceptions.ValidationError('Этого рецепта нет в покупках')
        shopping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """
    ViewSet provides to download list of ingredients
    and their quantities required for recipes.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        recipes = ShoppingCart.objects.filter(user=request.user).\
            values('recipe')
        ingredients = RecipeIngredient.objects.filter(recipe__in=recipes).\
            values('ingredient__name', 'ingredient__measurement_unit').\
            annotate(quantity=Sum('amount'))
        records = ["СПИСОК ПОКУПОК"]
        for ingredient in ingredients:
            records.append([ingredient['ingredient__name'],
                            str(ingredient['quantity']),
                            ingredient['ingredient__measurement_unit']])

        buf = io.BytesIO()
        canv = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        text = canv.beginText()
        text.setTextOrigin(cm, cm)
        pdfmetrics.registerFont(TTFont('Calibri', 'calibri.ttf'))
        text.setFont('Calibri', 12)

        for record in records:
            line = '- '
            for part in record:
                line += part + ' '
            text.textLine(line.encode("utf-8"))

        canv.drawText(text)
        canv.showPage()
        canv.save()
        buf.seek(0)
        return FileResponse(buf,
                            as_attachment=True,
                            filename='shopping_list.pdf')
