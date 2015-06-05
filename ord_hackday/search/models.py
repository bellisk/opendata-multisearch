from django.db import models


class Portal(models.Model):
    TYPE_CHOICES = (
        ("CKAN", "CKAN"),
    )

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    url = models.URLField()

    def __str__(self):
        return self.name
