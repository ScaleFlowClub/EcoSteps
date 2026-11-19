(() => {
  const key = 'ecosteps-theme';
  const root = document.documentElement;
  let theme;
  try {
    theme = localStorage.getItem(key);
  } catch {
    // The toggle also works without persistent browser storage.
  }
  if (location.protocol === 'file:') {
    const fromLink = new URLSearchParams(location.search).get('theme');
    if (fromLink === 'dark' || fromLink === 'light') theme = fromLink;
  }
  root.dataset.theme = theme === 'dark' ? 'dark' : 'light';

  document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('[data-theme-toggle]');
    function updateToggle() {
      const dark = root.dataset.theme === 'dark';
      toggle.setAttribute('aria-pressed', String(dark));
      toggle.querySelector('span').textContent = dark ? '☀' : '☾';
    }
    updateToggle();
    toggle.addEventListener('click', () => {
      theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = theme;
      try {
        localStorage.setItem(key, theme);
      } catch {
        // The current page retains the selection.
      }
      if (location.protocol === 'file:') {
        const url = new URL(location.href);
        url.searchParams.set('theme', theme);
        try {
          history.replaceState(null, '', url.href);
        } catch {
          // Some browsers restrict history edits for file URLs.
        }
      }
      updateToggle();
    });
    if (location.protocol === 'file:') {
      document.querySelectorAll('a[href]').forEach(anchor => {
        function carryTheme() {
          const url = new URL(anchor.href);
          if (url.protocol !== 'file:' || url.pathname === location.pathname ||
              !url.pathname.endsWith('.html')) return;
          url.searchParams.set('theme', root.dataset.theme);
          anchor.href = url.href;
        }
        anchor.addEventListener('focus', carryTheme);
        anchor.addEventListener('click', carryTheme);
      });
    }
  });
})();
