from django import template
from django.utils.safestring import mark_safe
import re
import markdown

register = template.Library()


@register.filter
def markdownify(value):
    if not value:
        return ''

    html = markdown.markdown(
        value,
        extensions=[
            'extra',
            'fenced_code',
            'nl2br',
            'sane_lists',
            'tables',
        ],
        output_format='html5',
    )
    html = re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        r'<pre class="mermaid">\1</pre>',
        html,
        flags=re.DOTALL,
    )
    return mark_safe(html)
