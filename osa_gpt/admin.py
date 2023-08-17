from django.contrib import admin

from osa_gpt.models import BotUser, BotSettings, Applications


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "tlg_id",
        "tlg_username",
        "start_bot_at",
    )
    list_display_links = (
        "pk",
        "tlg_id",
        "tlg_username",
        "start_bot_at",
    )


@admin.register(BotSettings)
class BotSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "key",
        "value",
    )
    list_display_links = (
        "pk",
        "key",
        "value",
    )


@admin.register(Applications)
class ApplicationsAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "phone_number",
        "created_at",
        "bot_user",
    )
    list_display_links = (
        "pk",
        "name",
        "phone_number",
        "created_at",
        "bot_user",
    )
