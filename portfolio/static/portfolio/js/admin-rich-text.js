(function () {
    function syncEditor(textarea, editor) {
        textarea.value = editor.innerHTML.trim();
    }

    function runCommand(command, value) {
        document.execCommand(command, false, value || null);
    }

    function createButton(label, title, action) {
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'rich-text-button';
        button.textContent = label;
        button.title = title;
        button.addEventListener('click', action);
        return button;
    }

    function attachEditor(textarea) {
        if (textarea.dataset.richTextReady === 'true') {
            return;
        }
        textarea.dataset.richTextReady = 'true';

        var wrapper = document.createElement('div');
        wrapper.className = 'rich-text-admin';

        var toolbar = document.createElement('div');
        toolbar.className = 'rich-text-toolbar';

        var editor = document.createElement('div');
        editor.className = 'rich-text-editor';
        editor.contentEditable = 'true';
        editor.innerHTML = textarea.value || '';

        toolbar.appendChild(createButton('H2', 'Heading', function () {
            editor.focus();
            runCommand('formatBlock', 'h2');
            syncEditor(textarea, editor);
        }));
        toolbar.appendChild(createButton('H3', 'Subheading', function () {
            editor.focus();
            runCommand('formatBlock', 'h3');
            syncEditor(textarea, editor);
        }));
        toolbar.appendChild(createButton('P', 'Paragraph', function () {
            editor.focus();
            runCommand('formatBlock', 'p');
            syncEditor(textarea, editor);
        }));
        toolbar.appendChild(createButton('B', 'Bold', function () {
            editor.focus();
            runCommand('bold');
            syncEditor(textarea, editor);
        }));
        toolbar.appendChild(createButton('I', 'Italic', function () {
            editor.focus();
            runCommand('italic');
            syncEditor(textarea, editor);
        }));
        toolbar.appendChild(createButton('UL', 'Bullet list', function () {
            editor.focus();
            runCommand('insertUnorderedList');
            syncEditor(textarea, editor);
        }));
        toolbar.appendChild(createButton('OL', 'Numbered list', function () {
            editor.focus();
            runCommand('insertOrderedList');
            syncEditor(textarea, editor);
        }));
        toolbar.appendChild(createButton('Quote', 'Block quote', function () {
            editor.focus();
            runCommand('formatBlock', 'blockquote');
            syncEditor(textarea, editor);
        }));
        toolbar.appendChild(createButton('Link', 'Insert link', function () {
            var url = window.prompt('Paste the URL');
            if (!url) {
                return;
            }
            editor.focus();
            runCommand('createLink', url);
            syncEditor(textarea, editor);
        }));
        toolbar.appendChild(createButton('Clear', 'Clear formatting', function () {
            editor.focus();
            runCommand('removeFormat');
            syncEditor(textarea, editor);
        }));
        toolbar.appendChild(createButton('Undo', 'Undo', function () {
            editor.focus();
            runCommand('undo');
            syncEditor(textarea, editor);
        }));
        toolbar.appendChild(createButton('Redo', 'Redo', function () {
            editor.focus();
            runCommand('redo');
            syncEditor(textarea, editor);
        }));

        editor.addEventListener('input', function () {
            syncEditor(textarea, editor);
        });
        editor.addEventListener('blur', function () {
            syncEditor(textarea, editor);
        });

        var form = textarea.closest('form');
        if (form) {
            form.addEventListener('submit', function () {
                syncEditor(textarea, editor);
            });
        }

        textarea.style.display = 'none';
        textarea.parentNode.insertBefore(wrapper, textarea.nextSibling);
        wrapper.appendChild(toolbar);
        wrapper.appendChild(editor);
    }

    function boot() {
        document.querySelectorAll('textarea.js-rich-text-source').forEach(attachEditor);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
