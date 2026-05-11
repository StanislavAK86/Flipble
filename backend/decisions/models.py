from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Decision(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    option_a = models.CharField(max_length=200, verbose_name='Вариант А')
    option_b = models.CharField(max_length=200, verbose_name='Вариант Б')
    coin_result = models.CharField(max_length=200, blank=True, verbose_name='Что выпало')
    counter_arguments = models.JSONField(default=list, verbose_name='Контраргументы')
    final_choice = models.CharField(max_length=200, blank=True, verbose_name='Итоговый выбор')
    session_key = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    from_cache = models.BooleanField(default=False, verbose_name='Из кэша')
    used_deepseek = models.BooleanField(default=False, verbose_name='Использован DeepSeek')
    provocative_question = models.TextField(blank=True, verbose_name='Провокационный вопрос')
    mode = models.CharField(max_length=20, default='cynic', verbose_name='Режим спорщика')

    class Meta:
        verbose_name = 'Решение'
        verbose_name_plural = 'Решения'
    
    def __str__(self):
        return f'{self.option_a} vs {self.option_b} [{self.mode}]'


class CachedResponse(models.Model):
    """Кэшированные ответы для экономии API (отдельно по режимам)"""
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    mode = models.CharField(max_length=20, default='cynic')  # cynic, kind, devil, lazy
    coin_result = models.CharField(max_length=200, blank=True)
    counter_arguments = models.JSONField(default=list)
    provocative_question = models.TextField(blank=True)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['option_a', 'option_b', 'mode']),
        ]
    
    def __str__(self):
        return f"{self.option_a} vs {self.option_b} [{self.mode}]"