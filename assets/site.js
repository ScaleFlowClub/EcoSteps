const menu = document.querySelector('.menu');
const navigation = document.querySelector('#navigation');
function setMenu(open) {
  menu.setAttribute('aria-expanded', String(open));
  navigation.classList.toggle('open', open);
}
menu.addEventListener('click', () => setMenu(menu.getAttribute('aria-expanded') !== 'true'));
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  const opened = navigation.querySelector('.nav-group[open]');
  if (opened) {
    opened.open = false;
    opened.querySelector('summary').focus();
    return;
  }
  if (menu.getAttribute('aria-expanded') === 'true') {
    setMenu(false);
    menu.focus();
  }
});

const contactDialog = document.querySelector('.contact-dialog');
const requestForm = contactDialog.querySelector('#request-form');
const requestStatus = contactDialog.querySelector('#request-status');
const isOffline = document.body.dataset.mode === 'offline';
let contactOpener;

document.querySelectorAll('[data-contact-open]').forEach(trigger => {
  trigger.addEventListener('click', event => {
    if (!contactDialog.showModal) return;
    event.preventDefault();
    contactOpener = trigger;
    contactDialog.showModal();
  });
});
contactDialog.querySelector('[data-contact-close]').addEventListener('click', () => contactDialog.close());
contactDialog.addEventListener('click', event => {
  if (event.target === contactDialog) contactDialog.close();
});
contactDialog.addEventListener('close', () => contactOpener?.focus());
requestForm.addEventListener('submit', event => {
  event.preventDefault();
  if (isOffline) {
    requestStatus.textContent = 'Demo abgeschlossen. Ihre Anfrage wurde nicht übertragen.';
    return;
  }
  const fields = new FormData(requestForm);
  const subject = fields.get('audience') === 'business' ? 'Anfrage von einem Unternehmen' : 'Anfrage von einem Privathaushalt';
  const body = [
    `Name: ${fields.get('name')}`,
    `E-Mail: ${fields.get('email')}`,
    fields.get('company') && `Firma: ${fields.get('company')}`,
    fields.get('phone') && `Telefon: ${fields.get('phone')}`,
    `\n${fields.get('message')}`
  ].filter(Boolean).join('\n');
  const recipient = contactDialog.querySelector('a[href^="mailto:"]').href;
  requestStatus.textContent = 'Der Entwurf kann im E-Mail-Programm geprüft und versendet werden.';
  window.location.href = `${recipient}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
});
requestForm.querySelector('button[type=submit]').disabled = false;

const demoBooking = document.querySelector('#demo-booking');
if (demoBooking) {
  demoBooking.addEventListener('click', () => {
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
  if (location.protocol === 'file:') {
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
        function carryConsent() {
          const target = new URL(anchor.href);
          if (!consent || target.protocol !== 'file:' || target.pathname === location.pathname ||
              !target.pathname.endsWith('.html')) return;
          target.searchParams.set('cookie-demo', consent);
          anchor.href = target.href;
        }
        anchor.addEventListener('click', carryConsent);
        anchor.addEventListener('focus', carryConsent);
      });
    }
    if (!consent) openSettings();
  }
}

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
if (!reducedMotion.matches && 'IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add('revealed');
      observer.unobserve(entry.target);
    }
  }, { threshold: 0.13 });
  document.querySelectorAll('.card').forEach(card => observer.observe(card));
}

const hero = document.querySelector('.hero-media');
if (hero && !reducedMotion.matches && !window.matchMedia('(max-width: 760px)').matches) {
  let frame;
  window.addEventListener('scroll', () => {
    if (frame) return;
    frame = requestAnimationFrame(() => {
      const offset = Math.min(window.scrollY * 0.10, 26);
      hero.style.setProperty('--image-offset', `${offset}px`);
      frame = undefined;
    });
  }, { passive: true });
}

const cookieNotice = document.querySelector('.cookie-notice');
if (cookieNotice) {
  const noticeKey = 'ecosteps-cookie-notice';
  try {
    cookieNotice.hidden = sessionStorage.getItem(noticeKey) === 'seen';
  } catch {
    cookieNotice.hidden = false;
  }
  cookieNotice.querySelector('[data-cookie-acknowledge]').addEventListener('click', () => {
    try {
      sessionStorage.setItem(noticeKey, 'seen');
    } catch {
      // The current page can still dismiss the notice.
    }
    cookieNotice.hidden = true;
  });
}

function readingSections() {
  const rows = [...document.querySelectorAll('.detail-grid .archive .fl-builder-content > .fl-row')];
  if (rows.length) return rows;
  const article = document.querySelector('[data-reading-sections]');
  if (!article || article.querySelectorAll(':scope > h2').length < 2) return [];
  const sections = [];
  let section;
  for (const child of [...article.children]) {
    if (child.matches('h2')) {
      section = document.createElement('section');
      article.insertBefore(section, child);
      sections.push(section);
    }
    if (section) section.append(child);
  }
  return sections;
}

const readingRows = readingSections();
const readingHeadings = readingRows.map(row => row.querySelector('h2, h3'));
if (typeof HTMLDialogElement !== 'undefined' &&
    readingHeadings.filter(Boolean).length > 1 &&
    readingRows.reduce((total, row) => total + row.textContent.trim().length, 0) > 900) {
  const dialog = document.createElement('dialog');
  dialog.className = 'reading-dialog';
  dialog.setAttribute('aria-labelledby', 'reading-title');
  dialog.innerHTML = `
    <div class="reading-panel">
      <div class="reading-header">
        <h2 id="reading-title"></h2>
        <button type="button" aria-label="Textfenster schließen" autofocus>×</button>
      </div>
      <div class="reading-dialog-body archive prose"></div>
    </div>`;
  document.body.append(dialog);

  const body = dialog.querySelector('.reading-dialog-body');
  const title = dialog.querySelector('#reading-title');
  const entries = [];
  let active;

  function restoreSection() {
    if (!active) return;
    active.heading.hidden = false;
    active.card.after(active.row);
    active.row.hidden = true;
    active = undefined;
  }

  function openSection(entry, target) {
    if (active !== entry) {
      restoreSection();
      active = entry;
      title.textContent = entry.heading.textContent;
      entry.heading.hidden = true;
      entry.row.hidden = false;
      body.append(entry.row);
      if (!dialog.open) dialog.showModal();
      dialog.scrollTop = 0;
    }
    if (target && target !== entry.row && target !== entry.heading) {
      target.scrollIntoView({ block: 'start' });
    }
    dialog.querySelector('button').focus({ preventScroll: true });
  }

  readingRows[0].parentElement.classList.add('reading-list');
  readingRows.forEach((row, index) => {
    const heading = readingHeadings[index];
    if (!heading) return;
    const card = document.createElement('div');
    card.className = 'reading-card';
    const label = document.createElement('h2');
    const button = document.createElement('button');
    button.type = 'button';
    button.setAttribute('aria-haspopup', 'dialog');
    const text = document.createElement('span');
    text.textContent = heading.textContent;
    const arrow = document.createElement('span');
    arrow.setAttribute('aria-hidden', 'true');
    arrow.textContent = '↗';
    arrow.className = 'reading-arrow';
    button.append(text, arrow);
    label.append(button);
    card.append(label);
    const photo = [...row.querySelectorAll('img[src]')].find(image => !image.src.endsWith('/pixel.png'));
    if (photo) {
      const thumbnail = document.createElement('img');
      thumbnail.src = photo.src;
      thumbnail.alt = '';
      thumbnail.loading = 'lazy';
      card.prepend(thumbnail);
    }
    row.before(card);
    row.hidden = true;
    const entry = { row, heading, card, button };
    entries.push(entry);
    button.addEventListener('click', () => openSection(entry));
  });

  function followSection(hash) {
    let fragment;
    try {
      fragment = decodeURIComponent(hash.slice(1));
    } catch {
      return false;
    }
    const target = fragment && document.getElementById(fragment);
    const entry = target && entries.find(item => item.row.contains(target));
    if (!entry) return false;
    openSection(entry, target);
    return true;
  }

  dialog.querySelector('button').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener('close', () => {
    const previous = active;
    restoreSection();
    previous?.button.focus();
  });

  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link) return;
    const url = new URL(link.href);
    if (url.origin === location.origin && url.pathname === location.pathname &&
        url.hash && followSection(url.hash)) {
      event.preventDefault();
      history.replaceState(null, '', url.hash);
    }
  });
  window.addEventListener('hashchange', () => followSection(location.hash));
  if (cookie?.open) cookie.addEventListener('close', () => followSection(location.hash), { once: true });
  else followSection(location.hash);
}
