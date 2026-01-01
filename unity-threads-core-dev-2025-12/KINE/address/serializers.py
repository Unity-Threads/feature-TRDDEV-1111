# address/serializers.py
from rest_framework import serializers
from .models import Address, Order

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'user', 'full_name', 'mobile_number', 'address_line1', 'address_line2',
            'city', 'state', 'country', 'pincode', 'is_default'
        ]
        read_only_fields = ['user']

class OrderSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), write_only=True, source='address'
    )

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'address', 'address_id', 'order_date',
            'status', 'expected_delivery_date', 'tracking_id', 'total_amount'
        ]
        read_only_fields = ['user', 'order_date', 'tracking_id']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
