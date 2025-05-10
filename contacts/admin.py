from django.contrib import admin

# Register your models here.

from .models import Contact

class ContactAdmin(admin.ModelAdmin):
	list_display = ('listing','listing_id','name','message','contact_date')
	list_filter = ('contact_date',)
	search_fields = ('contact_date','email','listing','listing_id')
	list_per_page = 15

admin.site.register(Contact, ContactAdmin)

# Register your models here.
