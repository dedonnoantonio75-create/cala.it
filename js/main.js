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

// ── Slideshow ──
function initSlideshow(el) {
  const track = el.querySelector('.slideshow__track');
  const slides = el.querySelectorAll('.slideshow__slide');
  const dots = el.querySelectorAll('.slideshow__dot');
  const total = slides.length;
  if (total < 2) return;
  let cur = 0, timer, startX = 0;

  function goTo(n) {
    cur = (n + total) % total;
    track.style.transform = `translateX(-${cur * 100}%)`;
    dots.forEach((d, i) => d.classList.toggle('active', i === cur));
  }
  function next() { goTo(cur + 1); }
  function prev() { goTo(cur - 1); }
  function startAuto() { timer = setInterval(next, 4500); }
  function resetAuto() { clearInterval(timer); startAuto(); }

  el.querySelector('.slideshow__next')?.addEventListener('click', () => { next(); resetAuto(); });
  el.querySelector('.slideshow__prev')?.addEventListener('click', () => { prev(); resetAuto(); });
  dots.forEach((d, i) => d.addEventListener('click', () => { goTo(i); resetAuto(); }));

  // Touch swipe
  el.addEventListener('touchstart', e => { startX = e.touches[0].clientX; }, { passive: true });
  el.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 40) { dx < 0 ? next() : prev(); resetAuto(); }
  }, { passive: true });

  goTo(0);
  startAuto();
}
document.querySelectorAll('.slideshow').forEach(initSlideshow);

// ── Contact forms (Netlify Forms AJAX) ──
const SUCCESS_MSG = {
  it: 'Grazie per il messaggio. Vi risponderemo entro 24 ore.',
  en: 'Thank you for your message. We will get back to you within 24 hours.',
  fr: 'Merci pour votre message. Nous vous répondrons dans les 24 heures.',
  es: 'Gracias por su mensaje. Le responderemos en menos de 24 horas.',
  de: 'Vielen Dank für Ihre Nachricht. Wir melden uns innerhalb von 24 Stunden.',
};
const pageLang = (document.documentElement.lang || 'it').slice(0, 2);
const successText = SUCCESS_MSG[pageLang] || SUCCESS_MSG.it;

document.querySelectorAll('form[data-netlify="true"]').forEach(form => {
  form.addEventListener('submit', e => {
    e.preventDefault();
    const required = form.querySelectorAll('[required]');
    let valid = true;
    required.forEach(el => {
      el.style.borderColor = el.value.trim() ? '' : 'red';
      if (!el.value.trim()) valid = false;
    });
    if (!valid) return;

    const btn = form.querySelector('button[type="submit"]');
    if (btn) btn.disabled = true;

    fetch('/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams(new FormData(form)).toString(),
    })
      .then(() => {
        form.innerHTML = `<p style="color:var(--gold);font-family:var(--font-italic);font-style:italic;font-size:1.2rem;text-align:center;padding:40px 0">${successText}</p>`;
      })
      .catch(() => {
        if (btn) btn.disabled = false;
        alert(successText);
      });
  });
});
