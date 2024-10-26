from django.contrib import admin
from .models import Note

# Register your models here.
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('author', 'faculty', 'subject', 'upload_date')
    search_fields = ('subject', 'faculty', 'author')
    list_filter = ('upload_date', )
    


