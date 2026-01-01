from django.contrib import admin
from .models import AboutUs
from .models import AboutUs, TimelineEvent

@admin.register(TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ('year', 'title', 'order')
    list_editable = ('order',)


@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ("title", "updated_at")

    def has_add_permission(self, request):
        return not AboutUs.objects.exists()
