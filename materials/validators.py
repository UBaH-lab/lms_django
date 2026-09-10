from rest_framework import serializers


class YouTubeValidator:
    """Валидатор: разрешает только ссылки на youtube.com."""

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        url = value.get(self.field, '')
        if url and 'youtube.com' not in url:
            raise serializers.ValidationError(
                f'Разрешены только ссылки на youtube.com. '
                f'Поле: {self.field}'
            )
