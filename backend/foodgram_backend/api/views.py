import io

from django.db.models import Sum
from django.http import FileResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, exceptions, status, mixins
from rest_framework.exceptions import AuthenticationFailed
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


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = (filters.SearchFilter,)
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ('author',)
    permission_classes = (AuthorOrReadOnly,)
    ordering = ('-pub_date',)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        tags_slug = self.request.query_params.get('tags')
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.\
            get('is_in_shopping_cart')
        if tags_slug is not None:
            queryset = queryset.filter(tags__slug=tags_slug)
        if is_favorited is not None:
            user = User.objects.get(username=self.request.user)
            if is_favorited == '1':
                queryset = queryset.filter(favorite__user=user.id)
            elif is_favorited == '0':
                queryset = queryset.exclude(favorite__user=user.id)
        if is_in_shopping_cart is not None:
            user = User.objects.get(username=self.request.user)
            if is_in_shopping_cart == '1':
                queryset = queryset.filter(shopping__user=user.id)
            elif is_in_shopping_cart == '0':
                queryset = queryset.exclude(shopping__user=user.id)
        return queryset


class SubscriptionViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        subscriber = self.request.user
        return User.objects.filter(subscribing__subscriber=subscriber)


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        subscribing = get_object_or_404(User, id=self.kwargs.get('user_id'))
        subscriber = self.request.user
        if subscriber.is_anonymous:
            raise AuthenticationFailed()
        if (subscriber == subscribing or Subscription.objects.filter(
                subscriber=subscriber,
                subscribing=subscribing).exists()):
            raise exceptions.ValidationError(
                'Подписка уже есть/ Подписка на себя невозможна')
        serializer = self.get_serializer(instance=subscribing)
        Subscription.objects.create(subscriber=subscriber,
                                    subscribing=subscribing)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def destroy(self, request, *args, **kwargs):
        subscribing = get_object_or_404(User, id=self.kwargs.get('user_id'))
        subscriber = self.request.user
        if subscriber.is_anonymous:
            raise AuthenticationFailed()
        if not Subscription.objects.filter(subscriber=subscriber,
                                           subscribing=subscribing).exists():
            raise exceptions.ValidationError(
                'Нет подписки на этого пользователя')
        Subscription.objects.filter(subscriber=subscriber,
                                    subscribing=subscribing).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeShortSerializer
    queryset = Recipe.objects.all()

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        user = self.request.user
        if Favourite.objects.filter(user=user,
                                    recipe=recipe).exists():
            raise exceptions.ValidationError('Рецепт уже есть в избранном')
        serializer = self.get_serializer(instance=recipe)
        Favourite.objects.create(user=user, recipe=recipe)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def destroy(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        user = self.request.user
        if not Favourite.objects.filter(user=user,
                                        recipe=recipe).exists():
            raise exceptions.ValidationError('Рецепта нет в избранном')
        Favourite.objects.filter(user=user,
                                 recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeShortSerializer
    queryset = Recipe.objects.all()

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.is_anonymous:
            raise AuthenticationFailed()
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        if ShoppingCart.objects.filter(user=user,
                                       recipe=recipe).exists():
            raise exceptions.ValidationError('Рецепт уже есть'
                                             'в списке покупок')
        serializer = self.get_serializer(instance=recipe)
        ShoppingCart.objects.create(user=user, recipe=recipe)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def destroy(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        user = request.user
        if user.is_anonymous:
            raise AuthenticationFailed()
        if not ShoppingCart.objects.filter(user=user,
                                           recipe=recipe).exists():
            raise exceptions.ValidationError('Рецепта нет в списке покупок')
        ShoppingCart.objects.filter(user=user,
                                    recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        current_user = request.user
        recipes = ShoppingCart.objects.filter(user=current_user).\
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
