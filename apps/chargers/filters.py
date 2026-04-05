import django_filters

from .models import Charger, ChargerStatus


class ChargerFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=ChargerStatus.choices)
    location = django_filters.UUIDFilter(field_name="location__id")

    class Meta:
        model = Charger
        fields = ["status", "location"]
