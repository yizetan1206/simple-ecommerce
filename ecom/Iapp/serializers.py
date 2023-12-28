from rest_framework import serializers 


class ProductSearchSerializer(serializers.Serializer): 
  id = serializers.IntegerField()
  name = serializers.CharField()
  description = serializers.CharField() 