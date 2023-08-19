from django.contrib import admin

from osa_gpt.models import BotUser, BotSettings, Applications, KnowledgeBaseChunks, PromptsAI


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


@admin.register(KnowledgeBaseChunks)
class KnowledgeBaseChunksAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "text_short",
    )
    list_display_links = (
        "pk",
        "text_short",
    )

    def text_short(self, obj: KnowledgeBaseChunks):
        """
        Метод, который возвращает сокращенное описание, если оно длиннее 48 символов.
        """
        if len(obj.text) < 48:
            return obj.text
        return ''.join([obj.text[:48], '...'])


@admin.register(PromptsAI)
class PromptsAIAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "prompt_short",
    )
    list_display_links = (
        "pk",
        "name",
        "prompt_short",
    )

    def prompt_short(self, obj: PromptsAI):
        """
        Метод, который возвращает сокращенное описание, если оно длиннее 48 символов.
        """
        if len(obj.prompt) < 48:
            return obj.prompt
        return ''.join([obj.prompt[:48], '...'])