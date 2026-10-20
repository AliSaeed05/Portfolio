// Optional enhancements: the page works without this file.
// 1) Opens the case study named in the URL hash and keeps the hash in sync.
// 2) Click any project picture to view it full size (arrows, zoom, Esc).
(function () {
  function caseFor(el) {
    if (!el) return null;
    return el.tagName === 'DETAILS' ? el : el.querySelector('details.case');
  }
  function openFromHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    var el = document.getElementById(id);
    var d = caseFor(el);
    if (d) { d.open = true; el.scrollIntoView(); }
  }
  Array.prototype.forEach.call(document.querySelectorAll('article.project[id]'), function (a) {
    var d = a.querySelector('details.case');
    if (!d) return;
    d.addEventListener('toggle', function () {
      if (d.open && location.hash !== '#' + a.id) {
        history.replaceState(null, '', '#' + a.id);
      } else if (!d.open && location.hash === '#' + a.id) {
        history.replaceState(null, '', location.pathname + location.search + '#work');
      }
    });
  });
  window.addEventListener('hashchange', openFromHash);
  openFromHash();

  // ---- Image viewer ----
  var links = Array.prototype.slice.call(document.querySelectorAll('a.lb'));
  if (!links.length || typeof HTMLDialogElement === 'undefined') return;

  var dlg = document.createElement('dialog');
  dlg.className = 'lightbox';
  dlg.setAttribute('aria-label', 'Image viewer');
  dlg.innerHTML =
    '<div class="lb-stage"><img alt=""><video controls playsinline preload="metadata" hidden></video></div>' +
    '<p class="lb-cap" aria-live="polite"></p>' +
    '<div class="lb-bar">' +
    '<button type="button" class="lb-prev">Previous</button>' +
    '<span class="lb-count" aria-live="polite"></span>' +
    '<button type="button" class="lb-next">Next</button>' +
    '<button type="button" class="lb-zoom" aria-pressed="false">Zoom</button>' +
    '<button type="button" class="lb-close">Close</button></div>';
  document.body.appendChild(dlg);

  var stage = dlg.querySelector('.lb-stage'), img = stage.querySelector('img'), vid = stage.querySelector('video');
  var cap = dlg.querySelector('.lb-cap'), count = dlg.querySelector('.lb-count');
  var prev = dlg.querySelector('.lb-prev'), next = dlg.querySelector('.lb-next');
  var zoom = dlg.querySelector('.lb-zoom'), close = dlg.querySelector('.lb-close');
  var group = [], idx = 0, opener = null;

  function setZoom(on) {
    stage.classList.toggle('zoomed', on);
    zoom.setAttribute('aria-pressed', on ? 'true' : 'false');
    if (!on) { stage.scrollTop = 0; stage.scrollLeft = 0; }
  }
  function show(i) {
    idx = (i + group.length) % group.length;
    var a = group[idx];
    setZoom(false);
    vid.pause();
    var isVid = a.getAttribute('data-type') === 'video';
    img.hidden = isVid; vid.hidden = !isVid; zoom.hidden = isVid;
    if (isVid) {
      img.removeAttribute('src');
      vid.src = a.getAttribute('href');
      vid.setAttribute('aria-label', a.getAttribute('data-alt') || 'Video');
    } else {
      vid.removeAttribute('src'); vid.load();
      img.src = a.getAttribute('href');
      img.alt = a.getAttribute('data-alt') || '';
    }
    cap.textContent = a.getAttribute('data-caption') || '';
    count.textContent = (idx + 1) + ' of ' + group.length;
    var single = group.length < 2;
    prev.hidden = next.hidden = count.hidden = single;
    [1, -1].forEach(function (d) {
      var n = group[(idx + d + group.length) % group.length];
      if (n && n.getAttribute('data-type') !== 'video') { (new Image()).src = n.getAttribute('href'); }
    });
  }
  function openAt(a) {
    var scope = a.closest('article.project') || document;
    group = Array.prototype.slice.call(scope.querySelectorAll('a.lb'));
    opener = a;
    show(group.indexOf(a));
    dlg.showModal();
    document.body.classList.add('lb-open');
    close.focus();
  }

  links.forEach(function (a) {
    a.addEventListener('click', function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return; // keep "open in new tab"
      e.preventDefault();
      openAt(a);
    });
  });
  prev.addEventListener('click', function () { show(idx - 1); });
  next.addEventListener('click', function () { show(idx + 1); });
  zoom.addEventListener('click', function () { setZoom(!stage.classList.contains('zoomed')); });
  close.addEventListener('click', function () { dlg.close(); });
  img.addEventListener('click', function () { setZoom(!stage.classList.contains('zoomed')); });
  stage.addEventListener('click', function (e) { if (e.target === stage) dlg.close(); });
  dlg.addEventListener('keydown', function (e) {
    if (group.length < 2 || e.target === vid) return; // arrows seek inside a playing video
    if (e.key === 'ArrowLeft') { e.preventDefault(); show(idx - 1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); show(idx + 1); }
  });
  dlg.addEventListener('close', function () {
    document.body.classList.remove('lb-open');
    vid.pause(); vid.removeAttribute('src'); vid.load();
    img.removeAttribute('src');
    if (opener) opener.focus();
  });
  var x0 = null;
  stage.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  stage.addEventListener('touchend', function (e) {
    if (x0 === null || stage.classList.contains('zoomed') || group.length < 2) return;
    var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1));
  });
})();
