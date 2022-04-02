from django.db import models


class Data(models.Model):

    name = models.CharField(blank=True, null=True, max_length=255)
    key = models.CharField(blank=True, null=True, max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        'account.Account',
        on_delete=models.CASCADE,
        related_name='%(class)s_created_by',
        blank=True, null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    value = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Data'
        verbose_name_plural = 'Data'
