/* =============================================
   SCROLL PROGRESS BAR
   ============================================= */
(function initScrollProgress() {
  const bar = document.querySelector('.scroll-progress');
  if (!bar) return;

  window.addEventListener('scroll', () => {
    const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
    const progress = scrollHeight - clientHeight > 0
      ? (scrollTop / (scrollHeight - clientHeight)) * 100
      : 0;
    bar.style.width = progress + '%';
  }, { passive: true });
})();

/* =============================================
   STICKY HEADER — add "scrolled" class
   ============================================= */
(function initStickyHeader() {
  const header = document.querySelector('.site-header');
  if (!header) return;
  const threshold = 30;

  function update() {
    header.classList.toggle('scrolled', window.scrollY > threshold);
  }
  update();
  window.addEventListener('scroll', update, { passive: true });
})();

/* =============================================
   MOBILE NAV TOGGLE
   ============================================= */
(function initMobileNav() {
  const toggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (!toggle || !navLinks) return;

  toggle.addEventListener('click', () => {
    const open = toggle.classList.toggle('open');
    navLinks.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', open);
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!toggle.contains(e.target) && !navLinks.contains(e.target)) {
      toggle.classList.remove('open');
      navLinks.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });

  // Close on link click
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      toggle.classList.remove('open');
      navLinks.classList.remove('open');
    });
  });
})();

/* =============================================
   ACTIVE NAV LINK (by current URL)
   ============================================= */
(function initActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(a => {
    const href = a.getAttribute('href') || '';
    const isHome = href === '/' || href === '';
    const isBlog = href.startsWith('/blog');
    const atHome = path === '/' || path === '';
    const atBlog = path.startsWith('/blog');

    if (isBlog && atBlog) {
      a.classList.add('active');
    } else if (isHome && atHome && !atBlog) {
      a.classList.add('active');
    }
  });
})();

/* =============================================
   BACK TO TOP BUTTON
   ============================================= */
(function initBackToTop() {
  const btn = document.querySelector('.back-to-top');
  if (!btn) return;

  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });

  btn.addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();

/* =============================================
   BLOG SEARCH — autocomplete suggestions
   ============================================= */
(function initBlogSearch() {
  const form = document.querySelector('.blog-search-form');
  const input = document.getElementById('blog-search-input');
  const suggestionsBox = document.querySelector('.search-suggestions');
  const clearBtn = document.querySelector('.search-clear-btn');

  if (!input || !suggestionsBox) return;

  const apiBase = input.dataset.apiUrl || '/blog/search/';
  let debounceTimer = null;
  let currentIndex = -1;

  // Show/hide clear button
  function updateClearBtn() {
    if (clearBtn) {
      clearBtn.classList.toggle('visible', input.value.length > 0);
    }
  }

  updateClearBtn();

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      input.value = '';
      closeSuggestions();
      updateClearBtn();
      input.focus();
    });
  }

  function closeSuggestions() {
    suggestionsBox.classList.remove('open');
    suggestionsBox.innerHTML = '';
    currentIndex = -1;
  }

  function renderSuggestions(results) {
    if (!results.length) { closeSuggestions(); return; }

    suggestionsBox.innerHTML =
      '<div class="suggestion-label">Suggested articles</div>' +
      results.map((r, i) =>
        `<a class="suggestion-item" href="/blog/${r.slug}/" data-index="${i}">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          ${escapeHtml(r.title)}
        </a>`
      ).join('');

    suggestionsBox.classList.add('open');
    currentIndex = -1;
  }

  function escapeHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function fetchSuggestions(query) {
    if (query.length < 2) { closeSuggestions(); return; }
    fetch(`${apiBase}?q=${encodeURIComponent(query)}`)
      .then(r => r.json())
      .then(data => renderSuggestions(data.results || []))
      .catch(() => closeSuggestions());
  }

  input.addEventListener('input', () => {
    updateClearBtn();
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => fetchSuggestions(input.value.trim()), 250);
  });

  // Keyboard navigation
  input.addEventListener('keydown', (e) => {
    const items = suggestionsBox.querySelectorAll('.suggestion-item');
    if (!items.length) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      currentIndex = Math.min(currentIndex + 1, items.length - 1);
      highlightItem(items);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      currentIndex = Math.max(currentIndex - 1, -1);
      highlightItem(items);
    } else if (e.key === 'Enter' && currentIndex >= 0) {
      e.preventDefault();
      items[currentIndex].click();
    } else if (e.key === 'Escape') {
      closeSuggestions();
    }
  });

  function highlightItem(items) {
    items.forEach((item, i) => item.classList.toggle('focused', i === currentIndex));
    if (currentIndex >= 0) items[currentIndex].scrollIntoView({ block: 'nearest' });
  }

  document.addEventListener('click', (e) => {
    if (!form.contains(e.target)) closeSuggestions();
  });

  input.addEventListener('focus', () => {
    if (input.value.trim().length >= 2) fetchSuggestions(input.value.trim());
  });
})();

/* =============================================
   SCROLL-TRIGGERED FADE-IN ANIMATIONS
   ============================================= */
(function initFadeIn() {
  const targets = document.querySelectorAll(
    '.timeline-item, .post-card, .skill-group, .education-list article, .signal-panel'
  );

  if (!targets.length || !('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.animation = 'fadeUp 0.55s cubic-bezier(0.16,1,0.3,1) both';
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
  );

  targets.forEach((el, i) => {
    el.style.opacity = '0';
    el.style.animationDelay = `${Math.min(i * 0.06, 0.36)}s`;
    observer.observe(el);
  });
})();

/* =============================================
   ESTIMATED READING TIME
   ============================================= */
(function initReadingTime() {
  const body = document.querySelector('.article-body');
  const timeEl = document.querySelector('.js-reading-time');
  if (!body || !timeEl) return;

  const words = body.innerText.trim().split(/\s+/).length;
  const minutes = Math.max(1, Math.ceil(words / 200));
  timeEl.textContent = `${minutes} min read`;
})();

/* =============================================
   SMOOTH ANCHOR SCROLL (offset for sticky header)
   ============================================= */
(function initAnchorScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href').slice(1);
      const target = document.getElementById(id);
      if (!target) return;

      e.preventDefault();
      const headerH = (document.querySelector('.site-header') || { offsetHeight: 80 }).offsetHeight;
      const top = target.getBoundingClientRect().top + window.scrollY - headerH - 16;
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });
})();
