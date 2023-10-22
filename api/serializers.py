from rest_framework import serializers

class YourDataSerializer(serializers.Serializer):
    description = serializers.CharField()
    category = serializers.CharField()
