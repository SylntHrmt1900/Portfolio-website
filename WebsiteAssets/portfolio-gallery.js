/* Artwork-only galleries. Uploaded files are indexed in gallery/works.js. */
(() => {
  'use strict';

  const collections = window.PORTFOLIO_WORKS;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const icon = path => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">${path}</svg>`;
  const dialog = document.createElement('dialog');
  dialog.id = 'workPreview';
  dialog.className = 'work-dialog';
  dialog.setAttribute('aria-label', 'Artwork preview');
  dialog.setAttribute('data-lenis-prevent', '');
  dialog.innerHTML = `
    <div class="work-toolbar">
      <button type="button" class="work-zoom" aria-label="Zoom artwork" title="Zoom artwork" aria-pressed="false">
        ${icon('<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5M7 10.5h7M10.5 7v7"/>')}
      </button>
      <a class="work-original" target="_blank" rel="noopener noreferrer" aria-label="Open original file in a new tab" title="Open original file">
        ${icon('<path d="M14 3h7v7M21 3 10 14M10 3H4a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h16a1 1 0 0 0 1-1v-6"/>')}
      </a>
      <button type="button" class="work-close" aria-label="Close artwork preview" autofocus>
        ${icon('<path d="m6 6 12 12M18 6 6 18"/>')}
      </button>
    </div>
    <div class="work-stage"><img alt="" decoding="async"><video controls playsinline preload="none" hidden></video></div>
    <p class="work-error" role="status" hidden>Could not load this preview. <a target="_blank" rel="noopener noreferrer">Open the original file</a>.</p>
    <div class="work-controls">
      <button type="button" class="work-previous" aria-label="Previous artwork">${icon('<path d="m14 5-7 7 7 7"/>')}</button>
      <span class="work-position" aria-live="polite" aria-atomic="true"></span>
      <button type="button" class="work-next" aria-label="Next artwork">${icon('<path d="m10 5 7 7-7 7"/>')}</button>
    </div>`;
  document.body.appendChild(dialog);

  const stage = dialog.querySelector('.work-stage');
  const image = stage.querySelector('img');
  const video = stage.querySelector('video');
  const zoomButton = dialog.querySelector('.work-zoom');
  const originalLink = dialog.querySelector('.work-original');
  const closeButton = dialog.querySelector('.work-close');
  const error = dialog.querySelector('.work-error');
  const position = dialog.querySelector('.work-position');
  let artworks = [];
  let currentIndex = 0;
  let savedState = null;
  let revealObserver = null;
  let closingTimer = null;
  let loadToken = 0;
  let mediaAnimation = null;

  function pauseVideo(release = false) {
    video.pause();
    if (release && video.hasAttribute('src')) {
      video.removeAttribute('src');
      video.load();
    }
  }

  function showError() {
    if (!dialog.open) return;
    error.hidden = false;
  }

  function fadeMedia(element, token) {
    if (token !== loadToken || reducedMotion.matches || !element.animate) return;
    if (mediaAnimation) mediaAnimation.cancel();
    mediaAnimation = element.animate([{ opacity: 0 }, { opacity: 1 }], {
      duration: 300, easing: 'cubic-bezier(.22,1,.36,1)'
    });
  }

  function showArtwork(index) {
    if (!artworks.length) return;
    currentIndex = (index + artworks.length) % artworks.length;
    const artwork = artworks[currentIndex];
    const token = ++loadToken;
    if (mediaAnimation) mediaAnimation.cancel();
    pauseVideo(true);
    error.hidden = true;
    stage.classList.remove('is-zoomed');
    stage.classList.toggle('is-light', artwork.surface === 'light');
    stage.scrollTo(0, 0);
    zoomButton.setAttribute('aria-pressed', 'false');
    zoomButton.setAttribute('aria-label', 'Zoom artwork');
    zoomButton.title = 'Zoom artwork';
    const isVideo = artwork.type === 'video';
    zoomButton.hidden = isVideo;
    image.hidden = isVideo;
    video.hidden = !isVideo;
    originalLink.href = artwork.original || artwork.src;
    error.querySelector('a').href = artwork.original || artwork.src;
    position.textContent = `${currentIndex + 1} / ${artworks.length}`;
    if (isVideo) {
      video.width = artwork.width;
      video.height = artwork.height;
      video.poster = artwork.thumbnail;
      video.setAttribute('aria-label', artwork.alt);
      video.preload = 'metadata';
      video.src = artwork.src;
      video.load();
      fadeMedia(video, token);
      return;
    }
    image.alt = artwork.alt;
    image.width = artwork.width;
    image.height = artwork.height;
    image.src = artwork.thumbnail;
    image.decode().then(() => fadeMedia(image, token)).catch(() => {});
    // Decode the optimized large view before replacing the already-visible preview.
    const fullImage = new Image();
    fullImage.src = artwork.src;
    fullImage.decode().then(() => {
      if (token !== loadToken) return;
      image.src = artwork.src;
    }).catch(() => {
      if (token === loadToken) showError();
    });
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
    ++loadToken;
    pauseVideo(true);
    if (mediaAnimation) mediaAnimation.cancel();
    if (dialog.open) dialog.close();
    dialog.classList.remove('is-visible', 'is-closing');
    restorePage(restoreFocus);
  }

  function close(restoreFocus = true) {
    pauseVideo();
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
    closingTimer = setTimeout(() => finishClose(), 400);
  }

  function open(index, opener) {
    if (dialog.open) finishClose(false);
    savedState = {
      opener, scrollX: window.scrollX, scrollY: window.scrollY,
      bodyOverflow: document.body.style.overflow,
      rootOverflow: document.documentElement.style.overflow,
      lenisWasStopped: Boolean(window.lenis && window.lenis.isStopped)
    };
    showArtwork(index);
    if (window.lenis) window.lenis.stop();
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';
    dialog.showModal();
    dialog.getBoundingClientRect();
    getComputedStyle(dialog, '::backdrop').opacity;
    dialog.classList.add('is-visible');
    closeButton.focus({ preventScroll: true });
  }

  function render(container, category) {
    close(false);
    artworks = collections[category] || [];
    container.replaceChildren();
    container.dataset.category = category;
    container.classList.add('work-grid');
    if (!artworks.length) {
      const empty = document.createElement('div');
      empty.className = 'work-empty';
      empty.innerHTML = '<p>Selected work will be added here soon.</p><button type="button" class="work-return">Back to Homepage</button>';
      empty.querySelector('button').addEventListener('click', () => window.navigateToHome('work'));
      container.appendChild(empty);
      container.classList.remove('work-grid');
      return;
    }
    if (!reducedMotion.matches && 'IntersectionObserver' in window) {
      revealObserver = new IntersectionObserver((entries, observer) => {
        entries.filter(entry => entry.isIntersecting).forEach((entry, index) => {
          const tile = entry.target;
          observer.unobserve(tile);
          tile.style.setProperty('--work-reveal-delay', `${Math.min(index, 3) * 70}ms`);
          tile.querySelector('img').decode().catch(() => {}).then(() => {
            if (tile.isConnected) tile.classList.add('is-revealed');
          });
        });
      }, { threshold: 0.02, rootMargin: '0px 0px -16px 0px' });
    }
    artworks.forEach((artwork, index) => {
      const tile = document.createElement('button');
      tile.type = 'button';
      tile.className = 'work-tile';
      tile.classList.toggle('is-light', artwork.surface === 'light');
      tile.setAttribute('aria-label', `${artwork.type === 'video' ? 'View video' : 'View artwork'} ${index + 1} of ${artworks.length}: ${artwork.alt}`);
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
      if (artwork.type === 'video') {
        const play = document.createElement('span');
        play.className = 'work-play';
        play.setAttribute('aria-hidden', 'true');
        play.innerHTML = icon('<path d="m9 5 11 7-11 7z" fill="currentColor" stroke="none"/>');
        tile.appendChild(play);
      }
      tile.addEventListener('click', () => open(index, tile));
      container.appendChild(tile);
      if (revealObserver) {
        tile.classList.add('is-reveal-pending');
        revealObserver.observe(tile);
      }
    });
  }

  zoomButton.addEventListener('click', () => {
    if (image.hidden) return;
    const zoomed = stage.classList.toggle('is-zoomed');
    stage.style.setProperty('--work-zoom-width', `${Math.max(artworks[currentIndex].width, stage.clientWidth)}px`);
    zoomButton.setAttribute('aria-pressed', String(zoomed));
    zoomButton.setAttribute('aria-label', zoomed ? 'Fit artwork to preview' : 'Zoom artwork');
    zoomButton.title = zoomed ? 'Fit artwork to preview' : 'Zoom artwork';
    stage.scrollTo(0, 0);
  });
  closeButton.addEventListener('click', () => close());
  dialog.querySelector('.work-previous').addEventListener('click', () => showArtwork(currentIndex - 1));
  dialog.querySelector('.work-next').addEventListener('click', () => showArtwork(currentIndex + 1));
  dialog.addEventListener('cancel', event => { event.preventDefault(); close(); });
  dialog.addEventListener('close', () => { if (!dialog.open) finishClose(); });
  dialog.addEventListener('transitionend', event => {
    if (event.target === dialog && event.propertyName === 'transform' && dialog.classList.contains('is-closing')) finishClose();
  });
  reducedMotion.addEventListener('change', () => {
    if (!reducedMotion.matches) return;
    if (revealObserver) revealObserver.disconnect();
    revealObserver = null;
    if (mediaAnimation) mediaAnimation.cancel();
    document.querySelectorAll('.work-tile').forEach(tile => tile.classList.add('is-revealed'));
    if (dialog.classList.contains('is-closing')) finishClose();
  });
  dialog.addEventListener('keydown', event => {
    if (event.key === 'Tab') {
      const controls = [...dialog.querySelectorAll('button, a[href], video[controls]')].filter(control => control.getClientRects().length > 0);
      const first = controls[0], last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    } else if (event.key === 'Escape') {
      event.preventDefault(); event.stopPropagation(); close();
    } else if ((event.key === 'ArrowLeft' || event.key === 'ArrowRight') && event.target !== video && !stage.classList.contains('is-zoomed')) {
      event.preventDefault(); event.stopPropagation();
      showArtwork(currentIndex + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
  let startedOnBackdrop = false;
  function isBackdrop(event) {
    const rect = dialog.getBoundingClientRect();
    return event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom);
  }
  dialog.addEventListener('pointerdown', event => { startedOnBackdrop = isBackdrop(event); });
  dialog.addEventListener('click', event => {
    if (startedOnBackdrop && isBackdrop(event)) close();
    startedOnBackdrop = false;
  });
  video.addEventListener('error', () => { if (!video.hidden && video.hasAttribute('src')) showError(); });

  window.WorkGallery = Object.freeze({
    render, close,
    count: category => (collections[category] || []).length,
    sourceCount: category => new Set((collections[category] || []).map(item => item.original || item.src)).size
  });
})();
