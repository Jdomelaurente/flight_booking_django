from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User,
    RegisteredUser,
    Class,
    SectionGroup,
    Section,
    ExcelRowData,
    Booking,
    TaskScore,
    Passenger,
    MultiCityLeg,
)


# ==============================
# Custom User
# ==============================
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "role")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )


# ==============================
# Registered User
# ==============================
@admin.register(RegisteredUser)
class RegisteredUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "date_registered")
    search_fields = ("username", "email", "role")
    ordering = ("-date_registered",)


# ==============================
# Class
# ==============================
@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject_code', 'subject_title', 'instructor', 'semester', 'academic_year', 'created_at')
    search_fields = ('subject_code', 'subject_title', 'instructor')
    list_filter = ('semester', 'academic_year')


# ==============================
# Section + SectionGroup
# ==============================
class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    fields = ("name", "schedule")


@admin.register(SectionGroup)
class SectionGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "subject_code", "subject_title", "instructor", "num_sections")
    inlines = [SectionInline]
    search_fields = ("subject_code", "subject_title", "instructor")
    list_filter = ("instructor",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'name', 'schedule')
    search_fields = ('name', 'schedule')
    list_filter = ('group',)


# ==============================
# Excel Row Data
# ==============================
@admin.register(ExcelRowData)
class ExcelRowDataAdmin(admin.ModelAdmin):
    list_display = ("id", "section", "uploaded_at")
    search_fields = ("section__name",)
    list_filter = ("uploaded_at",)


# ==============================
# Inlines for Booking
# ==============================
class TaskScoreInline(admin.TabularInline):
    model = TaskScore
    extra = 1
    fields = ("field_name", "score", "max_score")


class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 1
    fields = ("title", "first_name", "last_name", "dob", "nationality", "passport", "is_pwd", "has_declaration")


class MultiCityLegInline(admin.TabularInline):
    model = MultiCityLeg
    extra = 1
    fields = ("origin", "destination", "departure_date", "return_date")


# ==============================
# Booking
# ==============================
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "section",
        "route",
        "trip_type",
        "departure_date",
        "return_date",
        "travel_class",
        "is_active",
        "task_code",
        "total_score",
        "created_at",
    )
    search_fields = ("route", "trip_type", "travel_class", "task_code", "section__name")
    list_filter = ("trip_type", "travel_class", "is_active", "created_at")
    ordering = ("-created_at",)
    inlines = [TaskScoreInline, PassengerInline, MultiCityLegInline]


# ==============================
# Task Score
# ==============================
@admin.register(TaskScore)
class TaskScoreAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "field_name", "score", "max_score")
    search_fields = ("field_name", "booking__task_code")
    list_filter = ("booking",)


# ==============================
# Passenger
# ==============================
@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "dob", "passport", "nationality", "is_pwd", "has_declaration")
    search_fields = ("first_name", "last_name", "passport")
    list_filter = ("is_pwd", "has_declaration")


# ==============================
# Multi-City Leg
# ==============================
@admin.register(MultiCityLeg)
class MultiCityLegAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "origin", "destination", "departure_date", "return_date")
    search_fields = ("origin", "destination", "booking__task_code")
    list_filter = ("departure_date", "return_date")
