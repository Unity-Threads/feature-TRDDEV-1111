from django.db import models

class FAQCategory(models.Model):
    title = models.CharField(max_length=200)

    class Meta:
        verbose_name = "FAQ Category"
        verbose_name_plural = "FAQ Categories"

    def __str__(self):
        return self.title


class FAQ(models.Model):
    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=300)
    answer = models.TextField()

    def __str__(self):
        return self.question
