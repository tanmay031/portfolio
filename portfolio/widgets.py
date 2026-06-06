from django import forms


class RichTextAdminWidget(forms.Textarea):
    class Media:
        css = {
            'all': ('portfolio/css/admin-rich-text.css',)
        }
        js = ('portfolio/js/admin-rich-text.js',)

    def __init__(self, attrs=None):
        attrs = attrs or {}
        classes = attrs.get('class', '')
        attrs['class'] = f'{classes} js-rich-text-source'.strip()
        super().__init__(attrs)
