const menu = document.querySelector('.menu');
const navigation = document.querySelector('#navigation');
function setMenu(open) {
  menu.setAttribute('aria-expanded', String(open));
  navigation.classList.toggle('open', open);
}
menu.addEventListener('click', () => setMenu(menu.getAttribute('aria-expanded') !== 'true'));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') {
    setMenu(false);
    menu.focus();
  }
});

const requestForm = document.querySelector('#request-form');
if (requestForm) {
  requestForm.addEventListener('submit', event => {
    event.preventDefault();
    document.querySelector('#request-status').textContent = 'Demo abgeschlossen. Ihre Anfrage wurde nicht übertragen.';
  });
  document.querySelector('#demo-booking').addEventListener('click', () => {
    const slot = document.querySelector('#demo-slot').value;
    document.querySelector('#booking-status').textContent = slot
      ? `Demo-Termin um ${slot} Uhr ausgewählt. Es wurde kein Termin gebucht.`
      : 'Bitte wählen Sie eine Beispieluhrzeit.';
  });
}

const cookie = document.querySelector('.cookie');
if (cookie) {
  const storageKey = 'ecosteps-consent';
  const details = cookie.querySelector('#cookie-details');
  const detailsButton = cookie.querySelector('[data-cookie-details]');
  const statistics = cookie.querySelector('#demo-statistics');
  let consent;

  try {
    consent = localStorage.getItem(storageKey);
  } catch {
    consent = null;
  }
  if (!consent && location.protocol === 'file:') {
    const incoming = new URLSearchParams(location.search).get('cookie-demo');
    if (incoming === 'all' || incoming === 'no') consent = incoming;
  }

  function openSettings() {
    if (details) {
      details.hidden = true;
      detailsButton.setAttribute('aria-expanded', 'false');
      statistics.checked = consent === 'all';
    }
    cookie.showModal();
  }

  function saveConsent(value) {
    consent = value;
    try {
      localStorage.setItem(storageKey, value);
    } catch {
      // The active choice is still available while navigating the offline preview.
    }
    if (location.protocol === 'file:') {
      const url = new URL(location.href);
      url.searchParams.set('cookie-demo', value);
      try {
        history.replaceState(null, '', url.href);
      } catch {
        // Some file URL implementations restrict history updates.
      }
    }
    cookie.close();
  }

  document.querySelector('[data-cookie-settings]').addEventListener('click', openSettings);
  if (details) {
    detailsButton.addEventListener('click', () => {
      details.hidden = !details.hidden;
      detailsButton.setAttribute('aria-expanded', String(!details.hidden));
    });
    cookie.querySelectorAll('[data-consent]').forEach(button => {
      button.addEventListener('click', () => saveConsent(button.dataset.consent));
    });
    cookie.querySelector('[data-cookie-save]').addEventListener('click', () => {
      saveConsent(statistics.checked ? 'all' : 'no');
    });
    if (location.protocol === 'file:') {
      document.querySelectorAll('a[href]').forEach(anchor => {
        const original = new URL(anchor.href);
        if (original.protocol !== 'file:' || original.pathname === location.pathname || !original.pathname.endsWith('.html')) return;
        function carryConsent() {
          if (!consent) return;
          original.searchParams.set('cookie-demo', consent);
          anchor.href = original.href;
        }
        anchor.addEventListener('click', carryConsent);
        anchor.addEventListener('focus', carryConsent);
      });
    }
    if (!consent) openSettings();
  }
}
