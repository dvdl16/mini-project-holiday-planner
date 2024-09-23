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


class Itinerary(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    destinations = models.ManyToManyField("Destination", through="ItineraryDestination", related_name="itineraries")

    def __str__(self):
        return self.name


class ItineraryDestination(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    visit_order = models.PositiveIntegerField()

    class Meta:
        ordering = ["visit_order"]

    def __str__(self):
        return f"{self.itinerary.name} - {self.destination.name} (Order: {self.visit_order})"
