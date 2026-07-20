(function () {
  var KEY = 'cdb_cookie_consent';
  if (localStorage.getItem(KEY)) return;

  var isSubdir = /\/(en|fr|es|de)\//.test(location.pathname);
  var privacyUrl = isSubdir ? '../privacy.html' : 'privacy.html';

  var s = document.createElement('style');
  s.textContent = '#cdb-cookie-banner{position:fixed;bottom:24px;right:24px;z-index:99998;max-width:320px;width:calc(100vw - 48px);background:#0c1a2e;color:#fff;border-radius:12px;padding:20px 22px;box-shadow:0 8px 40px rgba(0,0,0,.4);font-family:inherit;font-size:.82rem;line-height:1.5;opacity:0;transform:translateY(12px);transition:opacity .35s,transform .35s}#cdb-cookie-banner.cdb-show{opacity:1;transform:translateY(0)}#cdb-cookie-banner h6{margin:0 0 8px;font-size:.88rem;font-weight:700;color:#c9a84c;letter-spacing:.04em;text-transform:uppercase}#cdb-cookie-banner p{margin:0 0 16px;color:#c8d0dc}#cdb-cookie-banner a{color:#c9a84c}#cdb-cookie-btns{display:flex;gap:8px}#cdb-cookie-btns button{flex:1;border:none;border-radius:6px;padding:9px 12px;font-size:.78rem;font-weight:600;cursor:pointer;letter-spacing:.02em}#cdb-accept{background:#c9a84c;color:#0c1a2e}#cdb-accept:hover{background:#b8933d}#cdb-necessary{background:transparent;color:#c8d0dc;border:1px solid rgba(200,208,220,.3) !important}#cdb-necessary:hover{background:rgba(200,208,220,.08)}';
  document.head.appendChild(s);

  var banner = document.createElement('div');
  banner.id = 'cdb-cookie-banner';
  banner.setAttribute('role', 'dialog');
  banner.setAttribute('aria-label', 'Cookie consent');
  banner.innerHTML =
    '<h6>Cookie</h6>' +
    '<p>Utilizziamo cookie tecnici (necessari al funzionamento) e analitici per migliorare la navigazione. Leggi la <a href="' + privacyUrl + '">Privacy &amp; Cookie Policy</a>.</p>' +
    '<div id="cdb-cookie-btns">' +
    '<button id="cdb-accept">Accetta tutto</button>' +
    '<button id="cdb-necessary">Solo necessari</button>' +
    '</div>';

  document.body.appendChild(banner);
  requestAnimationFrame(function () { banner.classList.add('cdb-show'); });

  function dismiss(val) {
    localStorage.setItem(KEY, val);
    banner.style.opacity = '0';
    banner.style.transform = 'translateY(12px)';
    setTimeout(function () { banner.remove(); }, 350);
  }

  document.getElementById('cdb-accept').addEventListener('click', function () { dismiss('accepted'); });
  document.getElementById('cdb-necessary').addEventListener('click', function () { dismiss('necessary'); });
})();
