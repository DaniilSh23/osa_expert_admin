from rest_framework import serializers


class GetSettingsSerializer(serializers.Serializer):
    """
    Сериалайзер для обработки запроса получения настроект
    """
    api_token = serializers.CharField(max_length=50)
    key = serializers.CharField(max_length=50)
