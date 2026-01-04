from django.db import models

class TermsPage(models.Model):
    title = models.CharField(
        max_length=200,
        default="Terms and Conditions"
    )
    intro_content = models.TextField(
        help_text="This content appears below the main title"
    )
    last_updated = models.DateField(auto_now=True)

    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class TermsCategory(models.Model):
    terms_page = models.ForeignKey(
        TermsPage,
        related_name="categories",
        on_delete=models.CASCADE
    )
    category_title = models.CharField(max_length=200)
    category_content = models.TextField()

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.category_title
