// The Jackie Marno-McGoldrick Art Prize — light progressive enhancement only.
(function () {
  "use strict";

  // ---- Mobile navigation toggle
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("primary-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A" && nav.classList.contains("open")) {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open menu");
      }
    });
  }

  // ---- Current year in the footer
  var yearEl = document.getElementById("year");
  if (yearEl) { yearEl.textContent = String(new Date().getFullYear()); }

  // ---- Lightbox for image galleries
  var lb = document.getElementById("lightbox");
  if (lb) {
    var links = Array.prototype.slice.call(document.querySelectorAll("a.lb"));
    var lbImg = lb.querySelector(".lb-img");
    var btnClose = lb.querySelector(".lb-close");
    var btnPrev = lb.querySelector(".lb-prev");
    var btnNext = lb.querySelector(".lb-next");
    var idx = -1;
    var lastFocus = null;

    function show(i) {
      idx = (i + links.length) % links.length;
      var a = links[idx];
      lbImg.src = a.getAttribute("href");
      lbImg.alt = (a.querySelector("img") || {}).alt || "";
      lb.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
      btnClose.focus();
    }
    function close() {
      lb.setAttribute("aria-hidden", "true");
      lbImg.removeAttribute("src");
      document.body.style.overflow = "";
      if (lastFocus) { lastFocus.focus(); }
    }

    links.forEach(function (a, i) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        lastFocus = a;
        show(i);
      });
    });
    btnPrev.addEventListener("click", function () { show(idx - 1); });
    btnNext.addEventListener("click", function () { show(idx + 1); });
    btnClose.addEventListener("click", close);
    lb.addEventListener("click", function (e) { if (e.target === lb) { close(); } });
    document.addEventListener("keydown", function (e) {
      if (lb.getAttribute("aria-hidden") === "true") { return; }
      if (e.key === "Escape") { close(); }
      else if (e.key === "ArrowLeft") { show(idx - 1); }
      else if (e.key === "ArrowRight") { show(idx + 1); }
    });
  }

  // ---- Scroll-reveal for sections
  var prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReduced || !("IntersectionObserver" in window)) { return; }

  var targets = document.querySelectorAll(
    ".section > .wrap > h2:not(.stage), .section > .wrap > .card-grid," +
    " .section > .wrap > .prose, .section > .wrap > .partner-list," +
    " .section > .wrap > .year-cards, .hero-copy, .hero-figure, .story-grid, .photo-row"
  );
  targets.forEach(function (el) { el.classList.add("reveal"); });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        io.unobserve(entry.target);
      }
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
  targets.forEach(function (el) { io.observe(el); });
})();
