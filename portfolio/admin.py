from django.contrib import admin
from django.db import models
from .models import (
    BlogCategory,
    BlogPost,
    ContactMessage,
    Education,
    Experience,
    ExperienceBullet,
    Highlight,
    NavigationItem,
    PageSection,
    SiteProfile,
    Skill,
    SkillCategory,
    SocialLink,
    Tag,
)
from .widgets import RichTextAdminWidget


class RichTextAdminMixin:
    rich_text_fields = ()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in self.rich_text_fields and isinstance(db_field, models.TextField):
            kwargs['widget'] = RichTextAdminWidget
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(SiteProfile)
class SiteProfileAdmin(RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ('about', 'contact_intro')
    fieldsets = (
        ('Identity', {'fields': ('name', 'role', 'location', 'email', 'phone')}),
        ('Home and About', {'fields': ('hero_title', 'hero_subtitle', 'about', 'years_experience', 'current_focus')}),
        ('Files', {'fields': ('profile_image', 'resume')}),
        ('Contact', {'fields': ('contact_intro',)}),
    )


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('label', 'url', 'order')
    list_editable = ('order',)


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    list_display = ('label', 'url', 'order', 'opens_new_tab')
    list_editable = ('order', 'opens_new_tab')


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('title', 'detail', 'order')
    list_editable = ('order',)


@admin.register(PageSection)
class PageSectionAdmin(RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ('subtitle',)
    list_display = ('key', 'kicker', 'title', 'order')
    list_editable = ('order',)
    search_fields = ('key', 'kicker', 'title', 'subtitle')


class ExperienceBulletInline(admin.TabularInline):
    model = ExperienceBullet
    extra = 1


@admin.register(Experience)
class ExperienceAdmin(RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ('summary',)
    inlines = [ExperienceBulletInline]
    list_display = ('role', 'company', 'location', 'start_date', 'end_date', 'is_current', 'order')
    list_editable = ('order', 'is_current')
    list_filter = ('is_current', 'company')
    search_fields = ('role', 'company', 'summary', 'technologies')


@admin.register(Education)
class EducationAdmin(RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ('description',)
    list_display = ('degree', 'institution', 'location', 'start_date', 'end_date', 'order')
    list_editable = ('order',)
    search_fields = ('degree', 'institution')


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    inlines = [SkillInline]
    list_display = ('name', 'order')
    list_editable = ('order',)


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(BlogPost)
class BlogPostAdmin(RichTextAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'published_at', 'updated_at')
    list_filter = ('status', 'category', 'tags')
    search_fields = ('title', 'excerpt', 'body')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    fieldsets = (
        ('Content', {'fields': ('title', 'slug', 'category', 'tags', 'excerpt', 'body', 'cover_image')}),
        ('Publishing', {'fields': ('status', 'published_at')}),
        ('SEO', {'fields': ('seo_title', 'meta_description')}),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at', 'updated_at')
