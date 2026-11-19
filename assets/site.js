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
