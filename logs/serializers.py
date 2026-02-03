from rest_framework import serializers

from .models import LogbookTrip

class LogSerializers(serializers.ModelSerializer):
    class Meta:
        model = LogbookTrip
        fields = "__all__"