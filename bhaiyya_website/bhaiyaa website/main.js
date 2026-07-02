(function () {
  var revealSelector = [
    "body > .card",
    "body > div > .card",
    ".card-header",
    "#About .row > [class*='col-']",
    ".card .card",
    ".team-profile-card",
    ".profile-detail",
    ".profile-detail-photo",
    ".profile-detail-copy > *",
    "#Service .card .card-img-top",
    "#Service .card .card-body > *",
    ".site-footer li",
    ".site-footer p",
    ".site-footer"
  ].join(",");

  var revealItems = Array.prototype.slice.call(document.querySelectorAll(revealSelector));
  revealItems = revealItems.filter(function (item, index, list) {
    return list.indexOf(item) === index;
  });

  revealItems.forEach(function (item, index) {
    var isCard = item.matches(".card .card, .team-profile-card");
    var isProfilePiece = item.matches(".profile-detail-photo, .profile-detail-copy > *");
    var isSectionPiece = item.matches(".card-header, #About .row > [class*='col-'], #Service .card .card-img-top, #Service .card .card-body > *, .site-footer li, .site-footer p");
    var group = item.closest(".row, .profile-grid");
    var rowCards = group ? Array.prototype.slice.call(group.querySelectorAll(".card, .team-profile-card")) : [];
    var rowIndex = rowCards.indexOf(item);
    var delay = Math.min(index * 80, 280);

    item.classList.add("scroll-reveal");
    if (isCard) {
      var half = Math.ceil(rowCards.length / 2);
      var pairIndex = rowCards.length > 3 && rowIndex >= half ? rowIndex - half : rowIndex;

      delay = rowIndex >= 0 ? pairIndex * 340 : delay;
      item.classList.add("card-reveal");

      if (rowCards.length > 3 && rowIndex >= half) {
        item.classList.add("from-right");
      } else {
        item.classList.add("from-left");
      }
    }

    if (isProfilePiece) {
      var profile = item.closest(".profile-detail");
      var profilePieces = profile ? Array.prototype.slice.call(profile.querySelectorAll(".profile-detail-photo, .profile-detail-copy > *")) : [];
      var pieceIndex = profilePieces.indexOf(item);

      delay = pieceIndex >= 0 ? pieceIndex * 120 : delay;
      item.classList.add("profile-piece-reveal");
    }

    if (isSectionPiece) {
      item.classList.add("section-piece-reveal");
    }

    item.style.setProperty("--reveal-delay", Math.min(delay, 1100) + "ms");
  });

  function showItem(item) {
    item.classList.add("is-visible");
  }

  function initCarousel() {
    if (typeof window.jQuery === "undefined" || typeof window.jQuery.fn.carousel !== "function") {
      return;
    }

    window.jQuery("#myslideshow").carousel({
      interval: 3500,
      pause: false,
      ride: "carousel",
      wrap: true
    });

    window.jQuery("#reviewsCarousel").carousel({
      interval: 45000,
      pause: false,
      ride: "carousel",
      wrap: true
    });
  }

  initCarousel();

  if (!("IntersectionObserver" in window) || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    revealItems.forEach(showItem);
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) {
          return;
        }

        showItem(entry.target);
        observer.unobserve(entry.target);
      });
    }, {
      rootMargin: "0px 0px -70px 0px",
      threshold: 0.12
    });

    revealItems.forEach(function (item) {
      observer.observe(item);
    });
  }

  var navCollapse = document.querySelector(".navbar-collapse");
  var navLinks = document.querySelectorAll(".navbar-nav .nav-link");
  var navbar = document.querySelector(".navbar");

  function updateNavbarSize() {
    if (!navbar) {
      return;
    }

    var scrollTop = window.pageYOffset || document.documentElement.scrollTop || 0;
    var isScrolled = scrollTop > 4;

    if (isScrolled) {
      navbar.classList.add("navbar-scrolled");
      document.body.classList.add("navbar-is-scrolled");
    } else {
      navbar.classList.remove("navbar-scrolled");
      document.body.classList.remove("navbar-is-scrolled");
    }
  }

  updateNavbarSize();
  window.addEventListener("scroll", updateNavbarSize, false);
  window.addEventListener("resize", updateNavbarSize, false);

  Array.prototype.forEach.call(navLinks, function (link) {
    link.addEventListener("click", function () {
      if (!navCollapse || !navCollapse.classList.contains("show") || typeof window.jQuery === "undefined") {
        return;
      }

      window.jQuery(navCollapse).collapse("hide");
    });
  });

  var profileCards = document.querySelectorAll(".profile-grid .team-profile-card[href]");

  function updateActiveProfileCard() {
    Array.prototype.forEach.call(profileCards, function (card) {
      var href = card.getAttribute("href") || "";
      var hashIndex = href.indexOf("#");
      var cardHash = hashIndex >= 0 ? href.slice(hashIndex) : "";

      card.classList.toggle("is-active", cardHash !== "" && cardHash === window.location.hash);
    });
  }

  updateActiveProfileCard();
  window.addEventListener("hashchange", updateActiveProfileCard);
}());
