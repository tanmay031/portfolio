from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SiteProfile(TimeStampedModel):
    name = models.CharField(max_length=120, default='MD Mahbubur Rahman')
    role = models.CharField(max_length=160, default='Backend Engineer')
    location = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=60, blank=True)
    hero_title = models.CharField(max_length=220)
    hero_subtitle = models.TextField()
    about = models.TextField()
    years_experience = models.PositiveIntegerField(default=9)
    current_focus = models.CharField(max_length=220, blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True)
    profile_image = models.ImageField(upload_to='profile/', blank=True)
    contact_intro = models.TextField(blank=True)

    class Meta:
        verbose_name = 'site profile'
        verbose_name_plural = 'site profile'

    def __str__(self):
        return self.name


class SocialLink(models.Model):
    label = models.CharField(max_length=60)
    url = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'label']

    def __str__(self):
        return self.label


class NavigationItem(models.Model):
    label = models.CharField(max_length=60)
    url = models.CharField(max_length=160, help_text='Use a path or anchor, for example /blog/ or /#contact.')
    order = models.PositiveIntegerField(default=0)
    opens_new_tab = models.BooleanField(default=False)

    class Meta:
        ordering = ['order', 'label']

    def __str__(self):
        return self.label


class Highlight(models.Model):
    title = models.CharField(max_length=120)
    detail = models.CharField(max_length=220)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class PageSection(TimeStampedModel):
    key = models.SlugField(max_length=80, unique=True, help_text='Stable identifier used by templates, for example about or contact.')
    kicker = models.CharField(max_length=120, blank=True)
    title = models.CharField(max_length=240)
    subtitle = models.TextField(blank=True)
    primary_label = models.CharField(max_length=80, blank=True)
    secondary_label = models.CharField(max_length=80, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'key']

    def __str__(self):
        return self.title


class Experience(TimeStampedModel):
    role = models.CharField(max_length=140)
    company = models.CharField(max_length=140)
    location = models.CharField(max_length=140, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    summary = models.TextField(blank=True)
    technologies = models.CharField(max_length=260, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-start_date']

    def __str__(self):
        return f'{self.role} at {self.company}'

    @property
    def date_range(self):
        start = self.start_date.strftime('%b %Y')
        end = 'Present' if self.is_current else self.end_date.strftime('%b %Y') if self.end_date else ''
        return f'{start} - {end}'.strip(' -')

    @property
    def tech_list(self):
        return [item.strip() for item in self.technologies.split(',') if item.strip()]


class ExperienceBullet(models.Model):
    experience = models.ForeignKey(Experience, related_name='bullets', on_delete=models.CASCADE)
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.text[:80]


class Education(TimeStampedModel):
    degree = models.CharField(max_length=180)
    institution = models.CharField(max_length=180)
    location = models.CharField(max_length=140, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-start_date']

    def __str__(self):
        return self.degree

    @property
    def date_range(self):
        start = self.start_date.strftime('%Y')
        end = self.end_date.strftime('%Y') if self.end_date else 'Present'
        return f'{start} - {end}'


class SkillCategory(models.Model):
    name = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'skill categories'

    def __str__(self):
        return self.name


class Skill(models.Model):
    category = models.ForeignKey(SkillCategory, related_name='skills', on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class BlogCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'blog categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogPost(TimeStampedModel):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    STATUS_CHOICES = (
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
    )

    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(BlogCategory, related_name='posts', on_delete=models.SET_NULL, blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    excerpt = models.TextField(blank=True)
    body = models.TextField()
    cover_image = models.ImageField(upload_to='blog/', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    published_at = models.DateTimeField(blank=True, null=True)
    seo_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == self.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('portfolio:blog_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


class ContactMessage(TimeStampedModel):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=160)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.subject}'
