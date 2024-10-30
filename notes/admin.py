from django.contrib import admin
from .models import Note, Bio, UserInfo, Feedback, NoteDownload

# Register your models here.
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('author', 'faculty', 'subject', 'upload_date', 'downloads')
    search_fields = ('subject', 'faculty', 'author')
    list_filter = ('upload_date', )
    

@admin.register(Bio)
class BioAdmin(admin.ModelAdmin):
    list_display = ('author', 'bio', 'created_at', 'updated_at')


@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('author', 'notes_count', 'total_downloads', 'last_uploaded_note', 'recent_activity')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('author', 'feedback')

@admin.register(NoteDownload)
class NoteDownloadAdmin(admin.ModelAdmin):
    list_display = ('user', 'note', 'downloaded_at')