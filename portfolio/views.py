from django.contrib import messages
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ContactMessageForm
from .models import BlogCategory, BlogPost, Education, Experience, Highlight, NavigationItem, PageSection, SiteProfile, SkillCategory, SocialLink, Tag


def get_profile():
    return SiteProfile.objects.first()


def shared_context():
    return {
        'profile': get_profile(),
        'social_links': SocialLink.objects.all(),
        'navigation_items': NavigationItem.objects.all(),
        'sections': {section.key: section for section in PageSection.objects.all()},
    }


def home(request):
    form = ContactMessageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Thanks. Your message is saved and ready for follow-up.')
        return redirect('portfolio:home')

    skill_categories = SkillCategory.objects.prefetch_related('skills')
    experiences = Experience.objects.prefetch_related('bullets')
    latest_posts = BlogPost.objects.filter(status=BlogPost.PUBLISHED).select_related('category')[:3]

    context = {
        **shared_context(),
        'highlights': Highlight.objects.all(),
        'experiences': experiences,
        'education_items': Education.objects.all(),
        'skill_categories': skill_categories,
        'latest_posts': latest_posts,
        'form': form,
    }
    return render(request, 'portfolio/home.html', context)


def blog_list(request):
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    tag_slug = request.GET.get('tag', '').strip()

    posts = BlogPost.objects.filter(status=BlogPost.PUBLISHED).select_related('category').prefetch_related('tags')

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(body__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)

    categories = BlogCategory.objects.all()
    all_tags = Tag.objects.all()

    context = {
        **shared_context(),
        'posts': posts,
        'categories': categories,
        'all_tags': all_tags,
        'query': query,
        'active_category': category_slug,
        'active_tag': tag_slug,
    }
    return render(request, 'portfolio/blog_list.html', context)


def blog_search_api(request):
    """JSON endpoint for blog search autocomplete suggestions."""
    query = request.GET.get('q', '').strip()
    results = []
    if len(query) >= 2:
        posts = (
            BlogPost.objects.filter(status=BlogPost.PUBLISHED, title__icontains=query)
            .values('title', 'slug')[:6]
        )
        results = list(posts)
    return JsonResponse({'results': results})


def blog_detail(request, slug):
    post = get_object_or_404(
        BlogPost.objects.filter(status=BlogPost.PUBLISHED).select_related('category').prefetch_related('tags'),
        slug=slug,
    )
    # Prefer posts from the same category or sharing tags
    tag_ids = list(post.tags.values_list('pk', flat=True))
    related_posts = (
        BlogPost.objects.filter(status=BlogPost.PUBLISHED)
        .exclude(pk=post.pk)
        .filter(Q(category=post.category) | Q(tags__pk__in=tag_ids))
        .select_related('category')
        .prefetch_related(Prefetch('tags'))
        .distinct()
        [:3]
    )
    if related_posts.count() < 3:
        # Fall back to latest posts if not enough related
        extra = (
            BlogPost.objects.filter(status=BlogPost.PUBLISHED)
            .exclude(pk=post.pk)
            .exclude(pk__in=[p.pk for p in related_posts])
            .select_related('category')
            [:3 - related_posts.count()]
        )
        related_posts = list(related_posts) + list(extra)
    context = {
        **shared_context(),
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'portfolio/blog_detail.html', context)
