(function () {
  'use strict';
  document.documentElement.classList.remove('no-js');

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Sticky nav background on scroll ------------------------------------- */
  var header = document.querySelector('.site-header');
  var progressBar = document.querySelector('.scroll-progress');
  var backToTop = document.querySelector('.back-to-top');

  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle('is-scrolled', y > 12);
    if (backToTop) backToTop.classList.toggle('is-visible', y > 600);
    if (progressBar) {
      var docHeight = document.documentElement.scrollHeight - window.innerHeight;
      var pct = docHeight > 0 ? (y / docHeight) * 100 : 0;
      progressBar.style.width = pct + '%';
    }
  }
  document.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (backToTop) {
    backToTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  }

  /* Mobile nav ------------------------------------------------------------ */
  var navToggle = document.getElementById('nav-open-btn');
  var navClose = document.getElementById('nav-close-btn');
  var mainNav = document.querySelector('.main-nav');
  function closeNav() {
    if (mainNav) mainNav.classList.remove('is-open');
    document.body.style.overflow = '';
  }
  if (navToggle && mainNav) {
    navToggle.addEventListener('click', function () {
      mainNav.classList.add('is-open');
      document.body.style.overflow = 'hidden';
    });
  }
  if (navClose) navClose.addEventListener('click', closeNav);
  document.querySelectorAll('.main-nav__list a').forEach(function (a) {
    a.addEventListener('click', closeNav);
  });

  /* Reveal-on-scroll -------------------------------------------------------*/
  var revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && revealEls.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* Animated counters -------------------------------------------------------*/
  var counters = document.querySelectorAll('[data-counter]');
  function animateCounter(el) {
    var raw = el.getAttribute('data-counter') || el.textContent;
    var match = raw.match(/^([^\d]*)([\d,]+)(.*)$/);
    if (!match) return;
    var prefix = match[1], numStr = match[2].replace(/,/g, ''), suffix = match[3];
    var target = parseInt(numStr, 10);
    if (isNaN(target)) return;
    if (reduceMotion) { el.textContent = prefix + target.toLocaleString() + suffix; return; }
    var duration = 1600, start = null;
    function step(ts) {
      if (!start) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var value = Math.floor(eased * target);
      el.textContent = prefix + value.toLocaleString() + suffix;
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = prefix + target.toLocaleString() + suffix;
    }
    requestAnimationFrame(step);
  }
  if ('IntersectionObserver' in window && counters.length) {
    var counterIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          counterIO.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });
    counters.forEach(function (el) { counterIO.observe(el); });
  }

  /* Services interactive tabs ------------------------------------------------*/
  var serviceTabs = document.querySelectorAll('.service-tab');
  serviceTabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      var target = tab.getAttribute('data-target');
      serviceTabs.forEach(function (t) { t.classList.remove('is-active'); });
      tab.classList.add('is-active');
      document.querySelectorAll('.service-panel').forEach(function (p) {
        p.classList.toggle('is-active', p.id === target);
      });
    });
  });

  /* Core values interactive list ---------------------------------------------*/
  var valueItems = document.querySelectorAll('.value-item');
  var valueDisplay = document.querySelector('.value-display');
  valueItems.forEach(function (item) {
    item.addEventListener('click', function () {
      valueItems.forEach(function (v) { v.classList.remove('is-active'); });
      item.classList.add('is-active');
      if (!valueDisplay) return;
      valueDisplay.querySelector('.value-display__icon').innerHTML = item.querySelector('.icon').outerHTML;
      valueDisplay.querySelector('.value-display__title').textContent = item.getAttribute('data-title');
      valueDisplay.querySelector('.value-display__desc').textContent = item.getAttribute('data-desc');
      var photoUrl = item.getAttribute('data-photo');
      var bgImg = valueDisplay.querySelector('.value-display__img');
      if (photoUrl) {
        if (!bgImg) {
          bgImg = document.createElement('img');
          bgImg.className = 'value-display__img';
          bgImg.alt = '';
          valueDisplay.querySelector('.value-display__bg').appendChild(bgImg);
        }
        bgImg.style.opacity = '0';
        setTimeout(function () { bgImg.src = photoUrl; bgImg.style.opacity = '1'; }, reduceMotion ? 0 : 150);
      }
    });
  });

  /* FAQ accordion --------------------------------------------------------------*/
  document.querySelectorAll('.faq-item__q').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = btn.closest('.faq-item');
      var answer = item.querySelector('.faq-item__a');
      var isOpen = item.classList.contains('is-open');
      document.querySelectorAll('.faq-item.is-open').forEach(function (open) {
        open.classList.remove('is-open');
        open.querySelector('.faq-item__a').style.maxHeight = null;
      });
      if (!isOpen) {
        item.classList.add('is-open');
        answer.style.maxHeight = answer.scrollHeight + 'px';
      }
    });
  });

  /* Auto-dismiss messages -------------------------------------------------------*/
  document.querySelectorAll('.message').forEach(function (msg) {
    setTimeout(function () {
      msg.style.transition = 'opacity 400ms ease';
      msg.style.opacity = '0';
      setTimeout(function () { msg.remove(); }, 400);
    }, 5000);
  });

  /* Gallery category filter + lightbox ----------------------------------------*/
  var galleryGrid = document.getElementById('gallery-grid');
  if (galleryGrid) {
    var galleryItems = Array.prototype.slice.call(galleryGrid.querySelectorAll('.masonry-item'));
    var filterButtons = document.querySelectorAll('#gallery-filters button');

    filterButtons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var cat = btn.getAttribute('data-category');
        filterButtons.forEach(function (b) { b.classList.remove('is-active'); });
        btn.classList.add('is-active');
        galleryItems.forEach(function (item) {
          var match = !cat || item.getAttribute('data-category') === cat;
          item.hidden = !match;
        });
        var url = new URL(window.location.href);
        if (cat) { url.searchParams.set('category', cat); } else { url.searchParams.delete('category'); }
        window.history.replaceState({}, '', url);
      });
    });

    var lightbox = document.getElementById('lightbox');
    var lbImg = document.getElementById('lightbox-img');
    var lbTitle = document.getElementById('lightbox-title');
    var lbDesc = document.getElementById('lightbox-desc');
    var lbClose = document.getElementById('lightbox-close');
    var lbPrev = document.getElementById('lightbox-prev');
    var lbNext = document.getElementById('lightbox-next');
    var currentIndex = -1;
    var lastFocused = null;

    function visibleItems() {
      return galleryItems.filter(function (item) { return !item.hidden; });
    }

    function openLightbox(item) {
      var items = visibleItems();
      currentIndex = items.indexOf(item);
      showCurrent(items);
      lastFocused = document.activeElement;
      lightbox.classList.add('is-open');
      lightbox.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      lbClose.focus();
    }

    function showCurrent(items) {
      items = items || visibleItems();
      if (!items.length) return;
      currentIndex = (currentIndex + items.length) % items.length;
      var item = items[currentIndex];
      lbImg.src = item.getAttribute('data-full');
      lbImg.alt = item.getAttribute('data-title') || '';
      lbTitle.textContent = item.getAttribute('data-title') || '';
      lbDesc.textContent = item.getAttribute('data-desc') || item.getAttribute('data-cat-name') || '';
    }

    function closeLightbox() {
      lightbox.classList.remove('is-open');
      lightbox.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      if (lastFocused) lastFocused.focus();
    }

    galleryItems.forEach(function (item) {
      item.addEventListener('click', function () { openLightbox(item); });
      item.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openLightbox(item); }
      });
    });

    if (lbClose) lbClose.addEventListener('click', closeLightbox);
    if (lbPrev) lbPrev.addEventListener('click', function () { currentIndex--; showCurrent(); });
    if (lbNext) lbNext.addEventListener('click', function () { currentIndex++; showCurrent(); });
    if (lightbox) {
      lightbox.addEventListener('click', function (e) {
        if (e.target === lightbox) closeLightbox();
      });
    }
    document.addEventListener('keydown', function (e) {
      if (!lightbox || !lightbox.classList.contains('is-open')) return;
      if (e.key === 'Escape') closeLightbox();
      else if (e.key === 'ArrowLeft') { currentIndex--; showCurrent(); }
      else if (e.key === 'ArrowRight') { currentIndex++; showCurrent(); }
    });
  }

  /* Simple client-side required-field validation state (native HTML5 handles the rest) */
  document.querySelectorAll('form[data-validate]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var invalid = form.querySelector(':invalid');
      if (invalid) {
        e.preventDefault();
        invalid.focus();
        invalid.closest('.field') && invalid.closest('.field').classList.add('has-error');
      }
    });
  });
})();
