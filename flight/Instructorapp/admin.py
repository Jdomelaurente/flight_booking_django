from django.contrib import admin
from .models import (
    User,
    Class,
    SectionGroup,
    Section,
    RegisteredUser,
    ExcelRowData,
    Booking,
    Passenger,
    MultiCityLeg,
)
from django.contrib.auth.admin import UserAdmin


# Keep your existing user registration
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


# ----------------------------
# ✅ Additional models
# ----------------------------

@admin.register(RegisteredUser)
class RegisteredUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "date_registered")
    search_fields = ("username", "email", "role")


@admin.register(ExcelRowData)
class ExcelRowDataAdmin(admin.ModelAdmin):
    list_display = ("id", "section", "uploaded_at")
    search_fields = ("section__name",)
    list_filter = ("uploaded_at",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "route", "trip_type", "departure_date", "return_date", "travel_class", "created_at")
    search_fields = ("route", "trip_type", "travel_class")
    list_filter = ("trip_type", "travel_class", "created_at")


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "dob", "passport", "nationality", "is_pwd")
    search_fields = ("first_name", "last_name", "passport")
    list_filter = ("is_pwd", "has_declaration")


@admin.register(MultiCityLeg)
class MultiCityLegAdmin(admin.ModelAdmin):
    list_display = ("id", "origin", "destination", "departure_date", "return_date", "booking")
    search_fields = ("origin", "destination")
    list_filter = ("departure_date", "return_date")
