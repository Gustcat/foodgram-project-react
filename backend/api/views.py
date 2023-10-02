import io

from django.db.models import Sum
from django.http import FileResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    viewsets, filters, status, mixins, exceptions, permissions)
from rest_framework.response import Response
from rest_framework.decorators import action
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from recipes.models import (
    Ingredient, Tag, Recipe, Favourite, ShoppingCart, RecipeIngredient)
from users.models import Subscription
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    SubscribeSerializer,
    RecipeShortSerializer,
    SubscriptionSerializer,
    FavoriteSerializer,
    ShoppingSerializer)
from .permissions import AuthorOrReadOnly
from .filters import RecipeFilter, IngredientFilter
from .paginations import ShoppingCartPagination


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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing recipes
    This ViewSet provides endpoints for creating, reading,
    updating, and deleting recipes and also downloading,
    adding to favourites, shopping.
    It supports filtering, ordering, and permissions.
    """
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    permission_classes = (AuthorOrReadOnly,)
    ordering = ('-pub_date',)
    pagination_class = ShoppingCartPagination

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @staticmethod
    def add_recipe_for_user(ser_class, pk, request):
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {'user': request.user.id, 'recipe': pk}
        serializer = ser_class(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer_recipe = RecipeShortSerializer(recipe)
        return Response(serializer_recipe.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_recipe_for_user(model, pk, request, message):
        delete_object = model.objects.filter(
            user=request.user,
            recipe=pk)
        if not delete_object.exists():
            raise exceptions.ValidationError(f'Этого рецепта нет в {message}')
        delete_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, url_path='favorite', url_name='favorite',
            serializer_class=FavoriteSerializer, methods=['post', 'delete'])
    def create_and_destroy_favorite(self, request, pk):
        if request.method == 'POST':
            return RecipeViewSet.add_recipe_for_user(
                self.serializer_class, pk, request)
        if request.method == 'DELETE':
            return RecipeViewSet.delete_recipe_for_user(
                Favourite, pk, request, 'избранном')

    @action(detail=True, url_path='shopping_cart', url_name='shopping_cart',
            serializer_class=ShoppingSerializer, methods=['post', 'delete'])
    def create_and_destroy_shopping(self, request, pk):
        if request.method == 'POST':
            return RecipeViewSet.add_recipe_for_user(
                self.serializer_class, pk, request)
        if request.method == 'DELETE':
            return RecipeViewSet.delete_recipe_for_user(
                ShoppingCart, pk, request, 'покупках')

    @action(detail=False, url_path='download_shopping_cart',
            url_name='download_shopping_cart',
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_list(self, request):
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
        pdfmetrics.registerFont(TTFont('Calibri', '/app/api/calibri.ttf'))
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


class SubscriptionViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
    ViewSet getting user subscription list.
    """
    serializer_class = SubscribeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        current_user = self.request.user
        return User.objects.filter(
            subscribing__in=current_user.subscriber.all())


class SubscribeViewSet(viewsets.ModelViewSet):
    """
    ViewSet provides to add and remove subscription on a user.
    """
    serializer_class = SubscriptionSerializer

    def create(self, request, *args, **kwargs):
        subscribing_id = int(self.kwargs.get('user_id'))
        subscribing = get_object_or_404(User, id=subscribing_id)
        data = {'subscriber': request.user.id, 'subscribing': subscribing_id}
        create_serializer = self.get_serializer(
            data=data, context={'request': request})
        create_serializer.is_valid(raise_exception=True)
        create_serializer.save()
        serializer = SubscribeSerializer(
            instance=subscribing, context={'request': request})
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        subscribing = get_object_or_404(User, id=self.kwargs.get('user_id'))
        subscription = Subscription.objects.filter(
            subscriber=request.user,
            subscribing=subscribing)
        if not subscription.exists():
            raise exceptions.ValidationError(
                'Нет подписки на этого пользователя')
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
