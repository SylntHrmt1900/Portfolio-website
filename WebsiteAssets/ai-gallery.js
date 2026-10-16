/* AI-only renderer and native image dialog. No routing or homepage replacement. */
(() => {
  'use strict';

  const artworks = window.AI_ARTWORKS;
  const dialog = document.createElement('dialog');
  dialog.id = 'aiArtworkDialog';
  dialog.className = 'ai-artwork-dialog';
  dialog.setAttribute('aria-label', 'Artwork preview');
  dialog.setAttribute('data-lenis-prevent', '');
  dialog.innerHTML = `
    <div class="ai-artwork-toolbar">
      <button type="button" aria-label="Close artwork preview" autofocus>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>
      </button>
    </div>
    <div class="ai-artwork-stage"><img alt="" decoding="async"></div>
    <p class="ai-artwork-error" role="status" hidden>
      The image could not be loaded. <a target="_blank" rel="noopener noreferrer">Open the original image</a>.
    </p>
    <div class="ai-artwork-controls">
      <button type="button" aria-label="Previous artwork">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="m14 5-7 7 7 7"/></svg>
      </button>
      <span class="ai-artwork-position" aria-live="polite" aria-atomic="true"></span>
      <button type="button" aria-label="Next artwork">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="m10 5 7 7-7 7"/></svg>
      </button>
    </div>`;
  document.body.appendChild(dialog);

  const image = dialog.querySelector('img');
  const error = dialog.querySelector('.ai-artwork-error');
  const position = dialog.querySelector('.ai-artwork-position');
  const [closeButton, previousButton, nextButton] = dialog.querySelectorAll('button');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let currentIndex = 0;
  let savedState = null;
  let revealObserver = null;
  let closingTimer = null;

  function showArtwork(index) {
    currentIndex = (index + artworks.length) % artworks.length;
    const artwork = artworks[currentIndex];
    error.hidden = true;
    image.hidden = false;
    image.style.display = '';
    image.alt = artwork.alt;
    image.width = artwork.width;
    image.height = artwork.height;
    image.src = artwork.src;
    error.querySelector('a').href = artwork.src;
    position.textContent = `${currentIndex + 1} / ${artworks.length}`;
  }

  function restorePage(restoreFocus = true) {
    if (!savedState) return;
    const state = savedState;
    savedState = null;
    document.body.style.overflow = state.bodyOverflow;
    document.documentElement.style.overflow = state.rootOverflow;
    if (window.lenis && !state.lenisWasStopped) window.lenis.start();
    window.scrollTo({ top: state.scrollY, left: state.scrollX, behavior: 'instant' });
    if (restoreFocus && state.opener.isConnected) state.opener.focus({ preventScroll: true });
  }

  function finishClose(restoreFocus = true) {
    clearTimeout(closingTimer);
    closingTimer = null;
    if (dialog.open) dialog.close();
    dialog.classList.remove('is-visible', 'is-closing');
    restorePage(restoreFocus);
  }

  function close(restoreFocus = true) {
    // Route changes must finish immediately, including an in-progress dismissal.
    if (!restoreFocus) {
      if (revealObserver) revealObserver.disconnect();
      revealObserver = null;
      finishClose(false);
      return;
    }
    if (!dialog.open || reducedMotion.matches) {
      finishClose(restoreFocus);
      return;
    }
    if (dialog.classList.contains('is-closing')) return;
    dialog.classList.add('is-closing');
    dialog.classList.remove('is-visible');
    // A fallback also handles interrupted transitions or a background browser tab.
    closingTimer = setTimeout(() => finishClose(), 400);
  }

  function open(index, opener) {
    if (dialog.open) finishClose(false);
    savedState = {
      opener,
      scrollX: window.scrollX,
      scrollY: window.scrollY,
      bodyOverflow: document.body.style.overflow,
      rootOverflow: document.documentElement.style.overflow,
      lenisWasStopped: Boolean(window.lenis && window.lenis.isStopped)
    };
    showArtwork(index);
    if (window.lenis) window.lenis.stop();
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';
    dialog.showModal();
    // Establish the transparent start state before transitioning the native dialog
    // and its backdrop together. Layout and focus still update immediately.
    dialog.getBoundingClientRect();
    getComputedStyle(dialog, '::backdrop').opacity;
    dialog.classList.add('is-visible');
    closeButton.focus({ preventScroll: true });
  }

  function render(container) {
    close(false);
    if (!reducedMotion.matches && 'IntersectionObserver' in window) {
      revealObserver = new IntersectionObserver((entries, observer) => {
        entries.filter(entry => entry.isIntersecting).forEach((entry, index) => {
          const tile = entry.target;
          observer.unobserve(tile);
          tile.style.setProperty('--ai-reveal-delay', `${Math.min(index, 3) * 70}ms`);
          // Reveal decoded artwork rather than an empty image frame.
          tile.querySelector('img').decode().catch(() => {}).then(() => {
            if (tile.isConnected) tile.classList.add('is-revealed');
          });
        });
      }, { threshold: 0.02, rootMargin: '0px 0px -16px 0px' });
    }
    artworks.forEach((artwork, index) => {
      const tile = document.createElement('button');
      tile.type = 'button';
      tile.className = 'ai-artwork-tile';
      tile.setAttribute('aria-label', `View artwork ${index + 1} of ${artworks.length}: ${artwork.alt}`);
      tile.setAttribute('aria-haspopup', 'dialog');
      tile.setAttribute('aria-controls', dialog.id);
      const thumbnail = document.createElement('img');
      thumbnail.src = artwork.thumbnail;
      thumbnail.alt = artwork.alt;
      thumbnail.width = artwork.width;
      thumbnail.height = artwork.height;
      thumbnail.loading = 'lazy';
      thumbnail.decoding = 'async';
      tile.appendChild(thumbnail);
      tile.addEventListener('click', () => open(index, tile));
      container.appendChild(tile);
      if (revealObserver) {
        tile.classList.add('is-reveal-pending');
        revealObserver.observe(tile);
      }
    });
  }

  closeButton.addEventListener('click', () => close());
  previousButton.addEventListener('click', () => showArtwork(currentIndex - 1));
  nextButton.addEventListener('click', () => showArtwork(currentIndex + 1));
  dialog.addEventListener('cancel', event => {
    event.preventDefault();
    close();
  });
  dialog.addEventListener('close', () => {
    if (!dialog.open) finishClose();
  });
  dialog.addEventListener('transitionend', event => {
    if (event.target === dialog && event.propertyName === 'transform' &&
        dialog.classList.contains('is-closing')) finishClose();
  });
  reducedMotion.addEventListener('change', () => {
    if (!reducedMotion.matches) return;
    if (revealObserver) revealObserver.disconnect();
    revealObserver = null;
    document.querySelectorAll('.ai-artwork-tile').forEach(tile => tile.classList.add('is-revealed'));
    if (dialog.classList.contains('is-closing')) finishClose();
  });
  dialog.addEventListener('keydown', event => {
    if (event.key === 'Tab') {
      const controls = [...dialog.querySelectorAll('button, a[href]')]
        .filter(control => control.getClientRects().length > 0);
      const first = controls[0];
      const last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    } else if (event.key === 'Escape') {
      event.preventDefault();
      event.stopPropagation(); // Keep legacy modals from resetting the scroll lock.
      close();
    } else if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      event.stopPropagation();
      showArtwork(currentIndex + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });

  // Close only a gesture that both starts and ends on the backdrop.
  let startedOnBackdrop = false;
  function isBackdrop(event) {
    const rect = dialog.getBoundingClientRect();
    return event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right ||
      event.clientY < rect.top || event.clientY > rect.bottom);
  }
  dialog.addEventListener('pointerdown', event => { startedOnBackdrop = isBackdrop(event); });
  dialog.addEventListener('click', event => {
    if (startedOnBackdrop && isBackdrop(event)) close();
    startedOnBackdrop = false;
  });
  image.addEventListener('error', () => {
    image.style.display = 'none';
    error.hidden = false;
  });

  window.AIGallery = Object.freeze({ render, close, count: artworks.length });
})();
