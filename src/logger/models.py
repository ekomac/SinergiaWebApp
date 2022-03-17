from django.db import models


class Log(models.Model):

    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        'account.Account', related_name='logs', on_delete=models.SET_NULL,
        null=True)
    url = models.CharField(max_length=255)
    error = models.TextField(blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    _type = models.CharField(max_length=255, default="other")
    # post_data = models.TextField(blank=True, null=True)
    # get_data = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user} - {self.url} @ {self.timestamp}'

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Log'
        verbose_name_plural = 'Logs'
