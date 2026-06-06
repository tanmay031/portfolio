from django.db import migrations


def seed_navigation_and_labels(apps, schema_editor):
    NavigationItem = apps.get_model('portfolio', 'NavigationItem')
    PageSection = apps.get_model('portfolio', 'PageSection')

    nav_items = [
        ('About', '/#about', 1),
        ('Experience', '/#experience', 2),
        ('Skills', '/#skills', 3),
        ('Blog', '/blog/', 4),
        ('Contact', '/#contact', 5),
    ]
    for label, url, order in nav_items:
        NavigationItem.objects.get_or_create(label=label, defaults={'url': url, 'order': order})

    updates = {
        'profile_signal': {'subtitle': 'years building backend systems'},
        'no_posts': {'title': 'No posts message', 'subtitle': 'No published posts yet. Add your first article from the admin panel.', 'order': 11},
        'blog_detail': {'title': 'Blog detail labels', 'primary_label': 'Back to blog', 'order': 12},
    }
    for key, defaults in updates.items():
        section, created = PageSection.objects.get_or_create(key=key, defaults=defaults)
        if not created:
            for field, value in defaults.items():
                setattr(section, field, value)
            section.save()


class Migration(migrations.Migration):
    dependencies = [
        ('portfolio', '0005_navigationitem'),
    ]

    operations = [
        migrations.RunPython(seed_navigation_and_labels, migrations.RunPython.noop),
    ]
