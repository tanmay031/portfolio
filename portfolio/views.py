from django.contrib import messages
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ContactMessageForm
from .models import BlogPost, Education, Experience, Highlight, NavigationItem, PageSection, SiteProfile, SkillCategory, SocialLink


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
    posts = BlogPost.objects.filter(status=BlogPost.PUBLISHED).select_related('category').prefetch_related('tags')
    context = {
        **shared_context(),
        'posts': posts,
    }
    return render(request, 'portfolio/blog_list.html', context)


def blog_detail(request, slug):
    post = get_object_or_404(
        BlogPost.objects.filter(status=BlogPost.PUBLISHED).select_related('category').prefetch_related('tags'),
        slug=slug,
    )
    related_posts = (
        BlogPost.objects.filter(status=BlogPost.PUBLISHED)
        .exclude(pk=post.pk)
        .select_related('category')
        .prefetch_related(Prefetch('tags'))
        [:3]
    )
    context = {
        **shared_context(),
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'portfolio/blog_detail.html', context)
