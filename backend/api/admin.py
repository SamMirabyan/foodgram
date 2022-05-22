from django.contrib import admin

from .models import IngredientType, Recipe, Tag, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
    )
    list_editable = (
        "first_name",
        "last_name",
    )
    list_filter = (
        "username",
        "email",
    )


@admin.register(IngredientType)
class IngredientTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "measurement_unit",
    )
    list_editable = (
        "name",
        "measurement_unit",
    )
    list_filter = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
        "color",
    )
    list_editable = (
        "name",
        "slug",
        "color",
    )
    list_filter = (
        "slug",
        "color",
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "text",
        "pub_date",
        "image",
        "author",
        "favorites_count",
    )
    list_editable = (
        "name",
        "text",
        "image",
    )
    list_filter = ("name", "author", "tags")
