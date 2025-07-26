from django.contrib import admin
from .models import Member
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .forms import MemberChangeForm, MemberCreationForm
from .models import Member, Profile, Address, UploadedFile

class MemberAdmin(UserAdmin):
    # Set the forms for a member
    add_form = MemberCreationForm
    form = MemberChangeForm

    # Fields to display in the list view
    list_display = ('email', 'phone', 'is_staff', 'is_superuser')
    
    # Fields to include in the add/edit forms
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('phone',)}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),)
    
    # Fields to include in the add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'phone', 'is_staff', 'is_superuser'),
        }),
    )
    
    # Ordering for the list view
    ordering = ('email',)

    # Display 'joined_date' as a read-only field
    readonly_fields = ('joined_date',)

admin.site.register(Member, MemberAdmin)
admin.site.register(Address)

class UploadedFileInline(admin.StackedInline):
    model = UploadedFile

    readonly_fields = ('download_link',)

    def download_link(self, obj):
        url = obj.gcs_signed_url()
        if url.startswith("http"):
            return format_html('<a href="{}" target="_blank">Download</a>', url)
        else:
            return url  # display error message if any
    download_link.short_description = "Download File"

    extra = 0

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [UploadedFileInline]

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['user', 'original_name', 'uploaded_at', 'gcs_path', 'download_link']

    def download_link(self, obj):
        url = obj.gcs_signed_url()
        if url.startswith("http"):
            return format_html('<a href="{}" target="_blank">Download</a>', url)
        else:
            return url  # display error message if any

    download_link.short_description = "Download File"