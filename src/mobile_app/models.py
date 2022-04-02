from django.db import models


class MobileApp(models.Model):

    latest_version = models.CharField(blank=True, null=True, max_length=255)
    url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.latest_version

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'MobileApp'
        verbose_name_plural = 'MobileApps'
