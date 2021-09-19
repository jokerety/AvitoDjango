from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=512)
    price = models.PositiveIntegerField()
    url = models.URLField()
    time = models.CharField(max_length=128)
    is_send = models.BooleanField(default=False)
    external_id = models.BigIntegerField(unique=True)
    parsed_at = models.DateTimeField(auto_now_add=True, editable=False)