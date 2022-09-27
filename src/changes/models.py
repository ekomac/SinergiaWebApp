from django.db import models


class Change(models.Model):
    """
    Change model
    """

    LABELS = (
        ('IM', 'Mejora'),
        ('BF', 'Corrección de error'),
        ('UP', 'Actualización'),
        ('MC', 'Corrección menor'),
        ('WF', 'Sin solución'),
    )

    name = models.CharField(max_length=100)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        'account.Account', verbose_name='Autor',
        on_delete=models.SET_DEFAULT, default=None, related_name='Author')
    label = models.CharField(max_length=2, choices=LABELS, default='IM')
    readers = models.ManyToManyField(
        'account.Account', related_name='Users_who_read',
        null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'Novedad'
        verbose_name_plural = 'Novedades'
