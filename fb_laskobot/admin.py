from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Feed)
admin.site.register(Person)
admin.site.register(Events)

admin.site.register(FbButton)
admin.site.register(FbCard)