/* ==========================================================================
   ZimLatestNews — main.js
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {

  /* -------------------------------------------------------------------------
     1. Mobile menu toggle
     ------------------------------------------------------------------------- */
  const btnMenu   = document.getElementById('btn-menu');
  const mobileNav = document.getElementById('mobile-nav');

  if (btnMenu && mobileNav) {
    btnMenu.addEventListener('click', function () {
      const open = mobileNav.classList.toggle('open');
      btnMenu.setAttribute('aria-expanded', open);
    });
  }

  /* -------------------------------------------------------------------------
     2. Search bar toggle
     ------------------------------------------------------------------------- */
  const btnSearch = document.getElementById('btn-search');
  const searchBar = document.getElementById('search-bar');
  const searchInput = searchBar ? searchBar.querySelector('input') : null;

  if (btnSearch && searchBar) {
    btnSearch.addEventListener('click', function () {
      const open = searchBar.classList.toggle('open');
      if (open && searchInput) searchInput.focus();
    });
  }

  /* -------------------------------------------------------------------------
     3. Back-to-top button
     ------------------------------------------------------------------------- */
  const backToTop = document.getElementById('back-to-top');

  if (backToTop) {
    window.addEventListener('scroll', function () {
      backToTop.classList.toggle('visible', window.scrollY > 400);
    }, { passive: true });

    backToTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* -------------------------------------------------------------------------
     4. Lazy-load AdSense slots via IntersectionObserver
        Each .ad-slot element needs data-ad-client and data-ad-slot attributes.
        The actual <ins> tag is injected only when the slot enters the viewport.
     ------------------------------------------------------------------------- */
  const adSlots = document.querySelectorAll('.ad-slot[data-ad-client]');

  if (adSlots.length && 'IntersectionObserver' in window) {
    const adObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const el        = entry.target;
          const client    = el.dataset.adClient;
          const slot      = el.dataset.adSlot;
          const format    = el.dataset.adFormat || 'auto';
          const responsive = el.dataset.fullWidthResponsive || 'true';

          const ins = document.createElement('ins');
          ins.className = 'adsbygoogle';
          ins.style.display = 'block';
          ins.setAttribute('data-ad-client', client);
          ins.setAttribute('data-ad-slot', slot);
          ins.setAttribute('data-ad-format', format);
          ins.setAttribute('data-full-width-responsive', responsive);

          el.innerHTML = '';
          el.appendChild(ins);

          try { (window.adsbygoogle = window.adsbygoogle || []).push({}); }
          catch (e) { console.warn('AdSense push error:', e); }

          adObserver.unobserve(el);

          // Record impression via our Django endpoint
          const adId = el.dataset.adId;
          if (adId) {
            fetch('/ads/impression/' + adId + '/', { method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') } })
              .catch(function () {});
          }
        }
      });
    }, { rootMargin: '200px' });

    adSlots.forEach(function (slot) { adObserver.observe(slot); });
  }

  /* -------------------------------------------------------------------------
     5. Direct / house ad click tracking
     ------------------------------------------------------------------------- */
  document.querySelectorAll('[data-track-ad]').forEach(function (el) {
    el.addEventListener('click', function () {
      const adId = el.dataset.trackAd;
      fetch('/ads/click/' + adId + '/', { method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') } })
        .catch(function () {});
    });
  });

  /* -------------------------------------------------------------------------
     6. Comment reply toggle — show the reply form under a comment
     ------------------------------------------------------------------------- */
  document.querySelectorAll('.comment-reply-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const commentId  = btn.dataset.commentId;
      const replyForm  = document.getElementById('reply-form-' + commentId);
      if (!replyForm) return;

      const isOpen = replyForm.classList.toggle('open');
      btn.textContent = isOpen ? 'Cancel' : 'Reply';

      if (isOpen) {
        // Set the parent_id hidden field
        const parentInput = replyForm.querySelector('input[name="parent_id"]');
        if (parentInput) parentInput.value = commentId;
        replyForm.querySelector('textarea').focus();
      }
    });
  });

  /* -------------------------------------------------------------------------
     7. Share buttons
     ------------------------------------------------------------------------- */
  const url   = encodeURIComponent(window.location.href);
  const title = encodeURIComponent(document.title);

  const shareTwitter  = document.getElementById('share-twitter');
  const shareFacebook = document.getElementById('share-facebook');
  const shareWhatsapp = document.getElementById('share-whatsapp');
  const shareCopy     = document.getElementById('share-copy');

  if (shareTwitter)  shareTwitter.href  = 'https://twitter.com/intent/tweet?url=' + url + '&text=' + title;
  if (shareFacebook) shareFacebook.href = 'https://www.facebook.com/sharer/sharer.php?u=' + url;
  if (shareWhatsapp) shareWhatsapp.href = 'https://wa.me/?text=' + title + '%20' + url;

  if (shareCopy) {
    shareCopy.addEventListener('click', function (e) {
      e.preventDefault();
      navigator.clipboard.writeText(window.location.href).then(function () {
        shareCopy.textContent = '✓ Copied!';
        setTimeout(function () { shareCopy.textContent = 'Copy link'; }, 2000);
      });
    });
  }

  /* -------------------------------------------------------------------------
     8. Breaking news ticker — duplicate items for seamless loop
     ------------------------------------------------------------------------- */
  const track = document.querySelector('.ticker-track');
  if (track && track.children.length) {
    const clone = track.innerHTML;
    track.innerHTML += clone; // duplicate so the loop is seamless
  }

  /* -------------------------------------------------------------------------
     9. Sticky sidebar — keep sidebar visible while scrolling article body
     ------------------------------------------------------------------------- */
  const sidebar = document.querySelector('.article-sidebar');
  if (sidebar && window.innerWidth > 900) {
    sidebar.style.position = 'sticky';
    sidebar.style.top      = '80px';
    sidebar.style.alignSelf = 'start';
  }

  /* -------------------------------------------------------------------------
     10. Lazy-load article images with shimmer placeholder
     ------------------------------------------------------------------------- */
  document.querySelectorAll('img[data-src]').forEach(function (img) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const el = entry.target;
          el.src = el.dataset.src;
          el.onload  = function () { el.style.opacity = '1'; el.closest('.shimmer') && el.closest('.shimmer').classList.remove('shimmer'); };
          el.onerror = function () { el.closest('.shimmer') && el.closest('.shimmer').classList.remove('shimmer'); };
          observer.unobserve(el);
        }
      });
    }, { rootMargin: '300px' });
    observer.observe(img);
  });

  /* -------------------------------------------------------------------------
     11. Auto-dismiss flash messages after 5 seconds
     ------------------------------------------------------------------------- */
  document.querySelectorAll('.message').forEach(function (msg) {
    setTimeout(function () {
      msg.style.transition = 'opacity 0.4s';
      msg.style.opacity = '0';
      setTimeout(function () { msg.remove(); }, 400);
    }, 5000);
  });

  /* -------------------------------------------------------------------------
     Helpers
     ------------------------------------------------------------------------- */
  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? match[2] : '';
  }

});
