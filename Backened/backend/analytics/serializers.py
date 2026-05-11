"""Serializers for analytics responses."""
from rest_framework import serializers

from .models import DashboardMetrics


class DashboardMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardMetrics
        fields = '__all__'
