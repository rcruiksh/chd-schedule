from django.contrib import admin

# Register your models here.
from .models import Consultant

# when a consultant is added in the ModelAdmin, it must also be added in the past db
class ConsultantAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # obj.user = request.user
        clone = Consultant(netlink=obj.netlink, email=obj.email, first_name=obj.first_name, last_name=obj.last_name)
        clone.save(using='past')
        super().save_model(request, obj, form, change)

admin.site.register(Consultant, ConsultantAdmin)
