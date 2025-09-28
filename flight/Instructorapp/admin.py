from django.contrib import admin
from .models import Class,SectionGroup, Section
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User




admin.site.register(User, UserAdmin)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject_code', 'subject_title', 'instructor', 'semester', 'academic_year', 'created_at')
    search_fields = ('subject_code', 'subject_title', 'instructor')
    list_filter = ('semester', 'academic_year')


# Inline so you can add Section + Schedule directly when creating a SectionGroup
class SectionInline(admin.TabularInline):
    model = Section
    extra = 1  # show 1 empty row by default
    fields = ("name", "schedule")  # only show relevant fields

@admin.register(SectionGroup)
class SectionGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "subject_code", "instructor", "num_sections")
    inlines = [SectionInline]  # attach sections inside group view

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'name', 'schedule')  # ✅ updated to match model
    search_fields = ('name', 'schedule')
    list_filter = ('group',)