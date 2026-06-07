from django.db import migrations


def seed_sections(apps, schema_editor):
    PageSection = apps.get_model('portfolio', 'PageSection')
    sections = [
        {
            'key': 'hero',
            'title': 'Hero actions',
            'primary_label': 'Start a conversation',
            'secondary_label': 'Download CV',
            'order': 1,
        },
        {
            'key': 'profile_signal',
            'title': 'Engineering profile',
            'order': 2,
        },
        {
            'key': 'about',
            'kicker': 'About',
            'title': 'Backend architecture for real products.',
            'order': 3,
        },
        {
            'key': 'experience',
            'kicker': 'Experience',
            'title': 'Roles and systems',
            'order': 4,
        },
        {
            'key': 'skills',
            'kicker': 'Skills',
            'title': 'Tools I use to ship reliable systems',
            'order': 5,
        },
        {
            'key': 'education',
            'kicker': 'Education',
            'title': 'Academic foundation',
            'order': 6,
        },
        {
            'key': 'blog',
            'kicker': 'Blog',
            'title': 'Recent writing',
            'primary_label': 'All posts',
            'order': 7,
        },
        {
            'key': 'contact',
            'kicker': 'Contact',
            'title': "Let's talk about backend architecture, system design, or engineering roles.",
            'primary_label': 'Send message',
            'order': 8,
        },
        {
            'key': 'blog_page',
            'kicker': 'Blog',
            'title': 'Notes on backend engineering, systems, and practical delivery.',
            'subtitle': 'Published articles are managed from the Django admin panel.',
            'order': 9,
        },
        {
            'key': 'related_posts',
            'kicker': 'More writing',
            'title': 'Keep reading',
            'order': 10,
        },
    ]
    for data in sections:
        key = data.pop('key')
        PageSection.objects.get_or_create(key=key, defaults=data)


class Migration(migrations.Migration):
    dependencies = [
        ('portfolio', '0003_pagesection'),
    ]

    operations = [
        migrations.RunPython(seed_sections, migrations.RunPython.noop),
    ]
