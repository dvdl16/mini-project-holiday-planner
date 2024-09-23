from django.db import models


class Destination(models.Model):
    DESTINATION_TYPE_CHOICES = [
        ("country", "Country"),
        ("city", "City"),
        ("poi", "Point of Interest"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=10, choices=DESTINATION_TYPE_CHOICES)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return self.name
