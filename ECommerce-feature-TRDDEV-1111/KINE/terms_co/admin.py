from django.contrib import admin
from .models import TermsPage, TermsCategory

class TermsCategoryInline(admin.StackedInline):
    model = TermsCategory
    extra = 1

@admin.register(TermsPage)
class TermsPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'last_updated')
    inlines = [TermsCategoryInline]
