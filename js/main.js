/* Cala dei Balcani — Main JavaScript */

// ── Navigation ──
const nav = document.querySelector('.nav');
const navToggle = document.querySelector('.nav__toggle');

if (nav) {
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 50);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

const navRows = document.querySelectorAll('.nav__row');

if (navToggle && navRows.length) {
  navToggle.addEventListener('click', () => {
    let anyOpen = false;
    navRows.forEach(row => {
      row.classList.toggle('open');
      if (row.classList.contains('open')) anyOpen = true;
    });
    navToggle.setAttribute('aria-expanded', String(anyOpen));
  });
  navRows.forEach(row => {
    row.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        navRows.forEach(r => r.classList.remove('open'));
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  });
}

// ── Scroll animations ──
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

// ── FAQ accordion ──
document.querySelectorAll('.faq-question').forEach(btn => {
  btn.addEventListener('click', () => {
    const item   = btn.closest('.faq-item');
    const isOpen = item.classList.contains('open');
    document.querySelectorAll('.faq-item.open').forEach(i => i.classList.remove('open'));
    if (!isOpen) item.classList.add('open');
  });
});

// ── Smooth scroll for # anchors ──
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  });
});

// ── Active language link ──
(function () {
  const path = window.location.pathname;
  document.querySelectorAll('.nav__lang a').forEach(a => {
    a.classList.remove('active');
    const href = a.getAttribute('href');
    if (href === '/' && !path.startsWith('/en') && !path.startsWith('/fr') && !path.startsWith('/es') && !path.startsWith('/de')) {
      a.classList.add('active');
    } else if (href !== '/' && path.startsWith(href)) {
      a.classList.add('active');
    }
  });
})();

// ── Contact form (basic validation) ──
const form = document.querySelector('.contact-form');
if (form) {
  form.addEventListener('submit', e => {
    e.preventDefault();
    const required = form.querySelectorAll('[required]');
    let valid = true;
    required.forEach(el => {
      el.style.borderColor = el.value.trim() ? '' : 'red';
      if (!el.value.trim()) valid = false;
    });
    if (valid) {
      form.innerHTML = '<p style="color:var(--gold);font-family:var(--font-italic);font-style:italic;font-size:1.2rem;text-align:center;padding:40px 0">Grazie per il messaggio. Vi risponderemo entro 24 ore.</p>';
    }
  });
}
