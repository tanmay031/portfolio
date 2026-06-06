from django.db import migrations
from django.utils import timezone
from django.utils.text import slugify


def seed_content(apps, schema_editor):
    SiteProfile = apps.get_model('portfolio', 'SiteProfile')
    SocialLink = apps.get_model('portfolio', 'SocialLink')
    Highlight = apps.get_model('portfolio', 'Highlight')
    Experience = apps.get_model('portfolio', 'Experience')
    ExperienceBullet = apps.get_model('portfolio', 'ExperienceBullet')
    Education = apps.get_model('portfolio', 'Education')
    SkillCategory = apps.get_model('portfolio', 'SkillCategory')
    Skill = apps.get_model('portfolio', 'Skill')
    BlogCategory = apps.get_model('portfolio', 'BlogCategory')
    Tag = apps.get_model('portfolio', 'Tag')
    BlogPost = apps.get_model('portfolio', 'BlogPost')

    SiteProfile.objects.get_or_create(
        name='MD Mahbubur Rahman',
        defaults={
            'role': 'Backend Engineer',
            'location': 'Stockholm, Sweden',
            'email': 'tanmay1007031@gmail.com',
            'phone': '+46 734 832 932',
            'hero_title': 'Backend architect for scalable system design.',
            'hero_subtitle': 'I design and build backend platforms, distributed services, cloud infrastructure, and integration-heavy systems with Python, Django, PostgreSQL, Redis, Celery, AWS, and Kubernetes.',
            'about': 'Backend Engineer with 9+ years of experience building scalable backend systems, microservices, and cloud-native applications. My work spans system architecture, third-party integrations, production infrastructure, distributed workflows, and platform engineering.\n\nI am especially comfortable where product delivery meets operational reliability: Django APIs, async processing, Kubernetes deployments, CI/CD pipelines, external service integrations, and data/reporting workflows that real teams depend on.',
            'years_experience': 9,
            'current_focus': 'System design, backend architecture, cloud-native systems',
            'contact_intro': 'I am open to backend architecture conversations, senior Django roles, system design work, and cloud-native product engineering.',
        },
    )

    SocialLink.objects.get_or_create(label='LinkedIn', defaults={'url': 'https://linkedin.com/in/mahbubur031', 'order': 1})

    highlights = [
        ('Architecture', 'System design, service boundaries, APIs, and distributed workflows'),
        ('Cloud', 'AWS EKS, Kubernetes, Argo CD, GitHub Actions, NGINX, Sentry'),
        ('Systems', 'Microservices, background jobs, distributed workflows, data pipelines'),
    ]
    for order, (title, detail) in enumerate(highlights, start=1):
        Highlight.objects.get_or_create(title=title, defaults={'detail': detail, 'order': order})

    experiences = [
        {
            'role': 'Backend Developer',
            'company': 'Toborrow',
            'location': 'Stockholm, Sweden',
            'start_date': '2024-10-01',
            'is_current': True,
            'technologies': 'Python, Django, PostgreSQL, Redis, Celery, AWS EKS, Kubernetes, GitHub Actions, Argo CD, HubSpot',
            'bullets': [
                'Own backend architecture and technical delivery for multiple digital lending platforms.',
                'Design and maintain scalable backend systems and APIs using Django, PostgreSQL, Redis, and Celery.',
                'Extracted screening, authentication, and notification capabilities into reusable microservices shared across lending platforms.',
                'Integrated BankID, Creditsafe, CM1, CreditInfo, Fortnox, Fintegry, Scorify, HubSpot, and external partner workflows.',
                'Designed and maintained AWS EKS infrastructure, Kubernetes deployments, ingress configuration, and CI/CD release workflows.',
                'Built asynchronous processing pipelines and reporting dashboards with Looker Studio.',
            ],
        },
        {
            'role': 'Master Thesis Researcher',
            'company': 'Bosch R&D Center',
            'location': 'Lund, Sweden',
            'start_date': '2024-02-01',
            'end_date': '2024-08-01',
            'technologies': 'Machine Learning, Data Processing, Anomaly Detection',
            'bullets': [
                'Conducted master thesis research on machine learning for heat pump fault detection and anomaly analysis.',
                'Designed predictive modeling and scalable preprocessing workflows.',
            ],
        },
        {
            'role': 'Backend Developer (Part-Time)',
            'company': 'Malmo University',
            'location': 'Malmo, Sweden',
            'start_date': '2023-09-01',
            'end_date': '2024-06-01',
            'technologies': 'Backend APIs, Cloud Architecture, Geospatial Processing, Real-Time Workflows',
            'bullets': [
                'Developed a proof-of-concept evacuation assistance platform with the Building Department and IoTaP researchers.',
                'Designed cloud-based backend architecture for emergency evacuation scenarios with reliability and fault tolerance in mind.',
                'Implemented REST APIs and geospatial processing workflows for location-aware evacuation management.',
                'Delivered a successful proof of concept that supported continued research and follow-on funding initiatives.',
            ],
        },
        {
            'role': 'Software Engineer',
            'company': 'Dynamic Solution Innovators Ltd',
            'location': 'Dhaka, Bangladesh',
            'start_date': '2017-01-01',
            'end_date': '2024-01-01',
            'technologies': 'Java, Python, REST APIs, Microservices, Docker, Cloud Infrastructure, Agile',
            'bullets': [
                'Designed enterprise-scale systems and integrated banking solutions.',
                'Engineered scalable backend systems and microservice-based enterprise applications.',
                'Developed REST APIs and backend services for enterprise platforms.',
                'Integrated banking and financial systems for reporting and workflow automation.',
                'Led Agile/Scrum development teams and mentored junior developers.',
            ],
        },
        {
            'role': 'Software Developer',
            'company': 'IICT, BUET',
            'location': 'Dhaka, Bangladesh',
            'start_date': '2015-08-01',
            'end_date': '2016-12-01',
            'technologies': 'Web Applications, SQL, Linux, Deployment',
            'bullets': [
                'Developed and maintained full-stack web applications across frontend and backend components.',
                'Designed and optimized SQL queries and database operations for performance and retrieval efficiency.',
                'Resolved software defects and managed Linux server deployments and maintenance.',
            ],
        },
    ]
    for order, data in enumerate(experiences, start=1):
        bullets = data.pop('bullets')
        experience, _ = Experience.objects.get_or_create(
            role=data['role'],
            company=data['company'],
            defaults={**data, 'order': order},
        )
        for bullet_order, text in enumerate(bullets, start=1):
            ExperienceBullet.objects.get_or_create(experience=experience, text=text, defaults={'order': bullet_order})

    education = [
        ('Master of Science in Applied Data Science', 'Malmo University', 'Malmo, Sweden', '2022-01-01', '2024-01-01'),
        ('Bachelor of Science in Computer Science & Engineering', 'Khulna University of Engineering and Technology', 'Khulna, Bangladesh', '2011-01-01', '2015-01-01'),
    ]
    for order, (degree, institution, location, start, end) in enumerate(education, start=1):
        Education.objects.get_or_create(
            degree=degree,
            institution=institution,
            defaults={'location': location, 'start_date': start, 'end_date': end, 'order': order},
        )

    skill_groups = {
        'Languages': ['Python', 'Java', 'SQL', 'Bash'],
        'Backend': ['Django', 'Django REST Framework', 'REST APIs', 'Celery', 'Microservices', 'Authentication', 'HubSpot API'],
        'Cloud & DevOps': ['AWS', 'Docker', 'Kubernetes', 'GitHub Actions', 'Argo CD', 'CI/CD', 'NGINX', 'Sentry'],
        'Databases': ['PostgreSQL', 'MySQL', 'Redis', 'Oracle'],
        'Architecture & Processing': ['Distributed Systems', 'Event-Driven Architecture', 'Background Jobs', 'Workflow Automation', 'Data Pipelines'],
        'Tools & Methods': ['Git', 'GitHub', 'Jira', 'Agile/Scrum', 'Postman', 'Swagger', 'Looker Studio'],
    }
    for category_order, (category_name, skills) in enumerate(skill_groups.items(), start=1):
        category, _ = SkillCategory.objects.get_or_create(name=category_name, defaults={'order': category_order})
        for skill_order, skill_name in enumerate(skills, start=1):
            Skill.objects.get_or_create(category=category, name=skill_name, defaults={'order': skill_order})

    categories = ['Backend Engineering', 'Django', 'Platform Engineering']
    category_map = {}
    for name in categories:
        category_map[name], _ = BlogCategory.objects.get_or_create(name=name, defaults={'slug': slugify(name)})

    tag_map = {}
    for name in ['Django', 'Architecture', 'Kubernetes', 'Systems']:
        tag_map[name], _ = Tag.objects.get_or_create(name=name, defaults={'slug': slugify(name)})

    posts = [
        (
            'Designing Django services that survive production traffic',
            category_map['Django'],
            ['Django', 'Systems'],
            'A practical note on API boundaries, background jobs, database behavior, and operational visibility in Django systems.',
            'Production Django work is rarely about views and models alone. The harder questions usually live around boundaries, queues, retries, database access, observability, and deployment discipline.\n\nThis starter article is editable from the admin panel. Replace it with your own writing when you are ready.',
        ),
        (
            'What complex integrations teach you about backend reliability',
            category_map['Backend Engineering'],
            ['Systems'],
            'Complex integrations are a forcing function for careful workflows, traceability, idempotency, and clear failure handling.',
            'Integration-heavy backends need to be explicit about states, retries, audit trails, and external service behavior. A good integration is not only one that works on a happy path. It is one that explains what happened when the outside world is slow, unavailable, or inconsistent.\n\nThis starter article is editable from the admin panel.',
        ),
        (
            'Small platform habits that make delivery calmer',
            category_map['Platform Engineering'],
            ['Kubernetes', 'Systems'],
            'A short reflection on CI/CD, Kubernetes, release flow, and the operational habits that help teams ship without drama.',
            'Platform work is often most valuable when it removes uncertainty. Repeatable deployments, useful logs, visible errors, and boring rollback paths give product teams more room to move.\n\nThis starter article is editable from the admin panel.',
        ),
    ]
    for title, category, tags, excerpt, body in posts:
        post, _ = BlogPost.objects.get_or_create(
            title=title,
            defaults={
                'slug': slugify(title),
                'category': category,
                'excerpt': excerpt,
                'body': body,
                'status': 'published',
                'published_at': timezone.now(),
            },
        )
        post.tags.set([tag_map[tag] for tag in tags])


def remove_seed_content(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('portfolio', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_content, remove_seed_content),
    ]
