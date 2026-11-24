/* Varuna landing page interactions: navigation, reveals, tagline and the
   three dimensional departure field. All values come from the project's
   cleaned station panel; nothing is generated. */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------------------------------- nav --- */
  var nav = document.querySelector(".nav");
  function onScrollNav() {
    if (!nav) return;
    nav.classList.toggle("is-scrolled", window.scrollY > 24);
  }
  window.addEventListener("scroll", onScrollNav, { passive: true });
  onScrollNav();

  /* ----------------------------------------------------- mobile menu --- */
  var toggle = document.querySelector(".menu-toggle");
  var menu = document.getElementById("mobile-menu");
  var menuItems = menu ? Array.prototype.slice.call(menu.querySelectorAll(".mobile-link, .mobile-cta, .mobile-note")) : [];

  function openMenu() {
    if (!menu || !toggle) return;
    menuItems.forEach(function (item, i) {
      item.style.transitionDelay = Math.min(i * 60, 400) + "ms";
    });
    menu.hidden = false;
    requestAnimationFrame(function () {
      menu.classList.add("is-open");
    });
    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute("aria-label", "Close menu");
    document.body.classList.add("menu-open");
    var first = menu.querySelector(".mobile-link");
    if (first) first.focus({ preventScroll: true });
  }

  function closeMenu(returnFocus) {
    if (!menu || !toggle) return;
    menu.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open menu");
    document.body.classList.remove("menu-open");
    window.setTimeout(function () {
      if (toggle.getAttribute("aria-expanded") === "false") menu.hidden = true;
    }, reduceMotion ? 0 : 500);
    if (returnFocus) toggle.focus({ preventScroll: true });
  }

  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      if (toggle.getAttribute("aria-expanded") === "true") closeMenu(true);
      else openMenu();
    });

    menu.addEventListener("click", function (event) {
      if (event.target.closest("a")) closeMenu(false);
    });

    document.addEventListener("keydown", function (event) {
      if (toggle.getAttribute("aria-expanded") !== "true") return;
      if (event.key === "Escape") {
        closeMenu(true);
        return;
      }
      if (event.key !== "Tab") return;
      var focusables = Array.prototype.slice.call(menu.querySelectorAll("a, button"));
      if (!focusables.length) return;
      var first = focusables[0];
      var last = focusables[focusables.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });
  }

  /* -------------------------------------------------- section reveals --- */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var revealObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -12% 0px", threshold: 0.08 }
    );
    reveals.forEach(function (el) {
      revealObserver.observe(el);
    });
  } else {
    reveals.forEach(function (el) {
      el.classList.add("is-visible");
    });
  }

  /* ------------------------------------------------- active nav state --- */
  var navLinks = Array.prototype.slice.call(document.querySelectorAll(".nav-link"));
  var sections = navLinks
    .map(function (link) {
      var href = link.getAttribute("href");
      return href && href.charAt(0) === "#" ? document.querySelector(href) : null;
    })
    .filter(Boolean);

  if ("IntersectionObserver" in window && sections.length) {
    var sectionObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var id = "#" + entry.target.id;
          navLinks.forEach(function (link) {
            if (link.getAttribute("href") === id) link.setAttribute("aria-current", "location");
            else link.removeAttribute("aria-current");
          });
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );
    sections.forEach(function (section) {
      sectionObserver.observe(section);
    });
  }

  /* ---------------------------------------------------------- tagline --- */
  var tagline = document.getElementById("tagline");
  if (tagline) {
    var text = tagline.textContent.trim().replace(/\s+/g, " ");
    tagline.setAttribute("aria-label", text);
    tagline.textContent = "";
    var words = text.split(" ").map(function (word, index) {
      var span = document.createElement("span");
      span.className = "tag-word";
      span.setAttribute("aria-hidden", "true");
      span.style.transitionDelay = Math.min(index * 55, 400) + "ms";
      span.textContent = word;
      tagline.appendChild(span);
      tagline.appendChild(document.createTextNode(" "));
      return span;
    });

    if (reduceMotion) {
      words.forEach(function (w) {
        w.classList.add("is-on");
      });
    } else {
      var tagTicking = false;
      var updateTag = function () {
        tagTicking = false;
        var trigger = window.innerHeight * 0.62;
        var remaining = 0;
        words.forEach(function (w) {
          if (w.classList.contains("is-on")) return;
          if (w.getBoundingClientRect().top < trigger) w.classList.add("is-on");
          else remaining += 1;
        });
        if (!remaining) {
          window.removeEventListener("scroll", queueTag);
          window.removeEventListener("resize", queueTag);
        }
      };
      var queueTag = function () {
        if (tagTicking) return;
        tagTicking = true;
        requestAnimationFrame(updateTag);
      };
      window.addEventListener("scroll", queueTag, { passive: true });
      window.addEventListener("resize", queueTag);
      updateTag();
    }
  }

  /* -------------------------------------------------------- 3d cards --- */
  if (window.matchMedia("(pointer: fine)").matches && !reduceMotion) {
    document.querySelectorAll(".tilt").forEach(function (card) {
      card.addEventListener("pointermove", function (event) {
        var rect = card.getBoundingClientRect();
        card.style.setProperty("--ry", ((event.clientX / rect.width - 0.5) * 5).toFixed(2) + "deg");
        card.style.setProperty("--rx", ((event.clientY / rect.height - 0.5) * -5).toFixed(2) + "deg");
      });
      card.addEventListener("pointerleave", function () {
        card.style.setProperty("--ry", "0deg");
        card.style.setProperty("--rx", "0deg");
      });
    });
  }

  /* -------------------------------------------------- terrain canvas --- */
  var canvas = document.getElementById("terrain");
  if (!canvas) return;
  var ctx = canvas.getContext("2d");
  var tip = document.getElementById("terrain-tip");

  var YEARS = [2020, 2021, 2022, 2024, 2025];
  var DISTRICTS = [
    "BAGALKOTE", "BALLARI", "BELAGAVI", "BENGALURU RURAL", "BENGALURU URBAN",
    "BIDAR", "CHAMARAJANAGARA", "CHIKKABALLAPURA", "CHIKKAMAGALURU", "CHITRADURGA",
    "DAKSHINA KANNADA", "DAVANAGERE", "DHARWAD", "GADAG", "HASSAN", "HAVERI",
    "KALABURAGI", "KODAGU", "KOLAR", "KOPPALA", "MANDYA", "MYSURU", "RAICHUR",
    "RAMANAGARA", "SHIVAMOGGA", "TUMAKURU", "UDUPI", "UTTARA KANNADA",
    "VIJAYANAGAR", "VIJAYAPURA", "YADGIR"
  ];
  var VALUES = [
    [28.9, -6.2, 41.7, 5.6, 23.0], [34.1, 18.6, 32.3, 8.0, -7.0],
    [21.9, 20.2, 52.0, 34.6, 23.5], [19.5, 55.2, 84.4, 7.9, 4.7],
    [29.4, 33.8, 71.3, 10.1, 2.3], [25.5, 6.6, 12.3, 1.1, 18.1],
    [11.1, 12.8, 58.2, 7.0, -24.1], [31.2, 73.3, 55.2, 2.7, 4.9],
    [7.5, 35.2, 49.1, 37.8, 14.9], [43.6, 62.6, 56.0, 31.6, -1.8],
    [-0.7, -3.2, 6.3, 15.1, 22.2], [24.7, 49.4, 78.6, 42.9, 9.2],
    [28.0, 26.8, 36.4, 17.0, 9.1], [19.1, 10.5, 56.9, -6.5, 8.7],
    [1.5, 27.0, 61.5, 42.3, 22.5], [-4.2, 28.5, 27.8, 13.9, -14.2],
    [40.8, 22.9, 10.0, 8.3, 37.3], [-4.8, 3.7, 17.0, 24.0, 27.3],
    [33.7, 79.2, 71.8, 6.4, 26.5], [38.5, 4.3, 21.7, 0.7, 14.2],
    [16.8, 41.6, 111.5, 18.6, 7.3], [5.2, 22.5, 71.0, 17.3, -2.1],
    [27.5, -0.5, 23.5, -3.0, 24.6], [16.8, 26.4, 79.3, 4.6, 2.1],
    [-0.5, 23.9, 27.9, 22.1, -3.4], [22.9, 64.7, 104.4, 52.5, 16.9],
    [19.5, 7.0, 5.7, 19.0, 22.5], [28.5, 18.8, 7.4, 36.8, 17.9],
    [31.0, 20.9, 46.7, 26.0, -4.7], [24.7, -4.3, 28.6, 3.0, 41.0],
    [31.2, -5.5, 37.1, 4.6, 33.7]
  ];

  var REST_YAW = -0.32;
  var RISE_PX = 0.34;
  var LEAN_PX = 3.2;

  var W = 0;
  var H = 0;
  var yaw = REST_YAW;
  var targetYaw = REST_YAW;
  var dragging = false;
  var dragX = 0;
  var velocity = 0;
  var turned = false;
  var hoverPoint = null;
  var visible = true;
  var points = [];

  function yearX(yi) {
    return (yi - (YEARS.length - 1) / 2) / ((YEARS.length - 1) / 2);
  }

  /* One stripe per district, laid out in screen space. Dragging turns the
     stack: the horizontal axis compresses and the rows lean, while near
     rows are drawn slightly wider and taller than far ones. */
  function layoutRows() {
    var n = DISTRICTS.length;
    var padTop = Math.max(20, H * 0.1);
    var padBottom = Math.max(34, H * 0.13);
    var rowStep = (H - padTop - padBottom) / (n - 1);
    var cosA = Math.cos(yaw);
    var sinA = Math.sin(yaw);
    var halfWidth = Math.min(W * 0.43, 230);
    var rows = [];
    points = [];

    for (var d = 0; d < n; d += 1) {
      var near = d / (n - 1);
      var scale = 0.82 + near * 0.26;
      var baseY = padTop + d * rowStep;
      var lean = (d - (n - 1) / 2) * sinA * LEAN_PX;
      var ridge = [];
      var base = [];
      for (var yi = 0; yi < YEARS.length; yi += 1) {
        var x = W / 2 + lean + yearX(yi) * halfWidth * cosA * scale;
        var v = VALUES[d][yi];
        var pt = { d: d, yi: yi, v: v, x: x, y: baseY - v * RISE_PX * scale };
        ridge.push(pt);
        base.push({ x: x, y: baseY });
        points.push(pt);
      }
      rows.push({ d: d, ridge: ridge, base: base, near: near });
    }
    return rows;
  }

  function draw() {
    if (!W || !H) return;
    ctx.clearRect(0, 0, W, H);
    var rows = layoutRows();

    /* Each district is a ridge across the five seasons, filled down to the
       zero departure line and painted far to near. */
    var ridgePath = function (row) {
      ctx.beginPath();
      ctx.moveTo(row.base[0].x, row.base[0].y);
      row.ridge.forEach(function (p) {
        ctx.lineTo(p.x, p.y);
      });
      for (var i = row.base.length - 1; i >= 0; i -= 1) {
        ctx.lineTo(row.base[i].x, row.base[i].y);
      }
      ctx.closePath();
    };
    var crestPath = function (row) {
      ctx.beginPath();
      row.ridge.forEach(function (p, index) {
        if (index) ctx.lineTo(p.x, p.y);
        else ctx.moveTo(p.x, p.y);
      });
    };

    rows.forEach(function (row) {
      var mean = row.ridge.reduce(function (sum, p) {
        return sum + p.v;
      }, 0) / row.ridge.length;
      var tone = mean < 0 ? "214,170,104" : "126,172,208";
      var top = row.ridge[0].y;
      var bottom = row.base[0].y;
      row.ridge.forEach(function (p) {
        if (p.y < top) top = p.y;
      });
      row.base.forEach(function (p) {
        if (p.y > bottom) bottom = p.y;
      });

      /* Each curtain is mostly opaque, so it hides the rows behind it and
         the stack reads as depth instead of a haze of overlapping fills. */
      var shade = ctx.createLinearGradient(0, top, 0, Math.max(bottom, top + 1));
      shade.addColorStop(0, "rgba(" + tone + "," + (0.18 + row.near * 0.12).toFixed(3) + ")");
      shade.addColorStop(0.55, "rgba(0,0,0,0.58)");
      shade.addColorStop(1, "rgba(0,0,0,0.94)");
      ridgePath(row);
      ctx.fillStyle = shade;
      ctx.fill();

      crestPath(row);
      ctx.lineWidth = 1;
      ctx.strokeStyle = "rgba(" + tone + "," + (0.32 + row.near * 0.5).toFixed(3) + ")";
      ctx.stroke();
    });

    /* Year axis under the nearest row. */
    var nearRow = rows[rows.length - 1];
    ctx.fillStyle = "#9b9b9b";
    ctx.font = '12px "Geist Mono", Consolas, monospace';
    ctx.textAlign = "center";
    ctx.textBaseline = "alphabetic";
    for (var yi = 0; yi < YEARS.length; yi += 1) {
      ctx.fillText(String(YEARS[yi]), Math.max(20, Math.min(W - 20, nearRow.base[yi].x)), H - 12);
    }

    /* The two observed extremes, marked rather than labelled so nothing
       overlaps the field at narrow widths. */
    var peak = points[0];
    var low = points[0];
    points.forEach(function (p) {
      if (p.v > peak.v) peak = p;
      if (p.v < low.v) low = p;
    });
    [peak, low].forEach(function (p) {
      ctx.beginPath();
      ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
      ctx.strokeStyle = "rgba(255,255,255,0.85)";
      ctx.lineWidth = 1.2;
      ctx.stroke();
    });

    if (hoverPoint) {
      ctx.beginPath();
      ctx.arc(hoverPoint.x, hoverPoint.y, 3.5, 0, Math.PI * 2);
      ctx.fillStyle = "#ffffff";
      ctx.fill();
    }
  }

  function resize() {
    var rect = canvas.getBoundingClientRect();
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = rect.width;
    H = rect.height;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw();
  }

  if ("ResizeObserver" in window) {
    new ResizeObserver(resize).observe(canvas);
  } else {
    window.addEventListener("resize", resize);
  }

  function animate(now) {
    requestAnimationFrame(animate);
    if (!visible) return;
    if (!turned && !dragging) targetYaw = REST_YAW + Math.sin(now / 9000) * 0.06;
    if (!dragging) {
      if (Math.abs(velocity) > 0.0002) {
        targetYaw += velocity;
        velocity *= 0.93;
      }
      yaw += (targetYaw - yaw) * 0.09;
    }
    draw();
  }

  function nearestPoint(clientX, clientY) {
    var rect = canvas.getBoundingClientRect();
    var x = clientX - rect.left;
    var y = clientY - rect.top;
    var limit = Math.max(14, W * 0.03);
    var best = null;
    points.forEach(function (p) {
      var distance = Math.hypot(p.x - x, p.y - y);
      if (distance < limit) {
        best = p;
        limit = distance;
      }
    });
    return best;
  }

  canvas.addEventListener("pointerdown", function (event) {
    dragging = true;
    turned = true;
    dragX = event.clientX;
    velocity = 0;
    canvas.classList.add("is-dragging");
    try {
      canvas.setPointerCapture(event.pointerId);
    } catch (error) {
      /* capture is a nicety; dragging still works without it */
    }
    if (tip) tip.hidden = true;
  });

  canvas.addEventListener("pointermove", function (event) {
    if (dragging) {
      var dx = event.clientX - dragX;
      dragX = event.clientX;
      yaw += dx * 0.005;
      targetYaw = yaw;
      velocity = dx * 0.0005;
      draw();
      return;
    }
    if (event.pointerType !== "mouse") return;
    var hit = nearestPoint(event.clientX, event.clientY);
    hoverPoint = hit;
    if (hit) draw();
    if (!tip) return;
    if (!hit) {
      tip.hidden = true;
      return;
    }
    tip.hidden = false;
    tip.textContent =
      DISTRICTS[hit.d] + " · " + YEARS[hit.yi] + " · " +
      (hit.v > 0 ? "+" : "") + hit.v.toFixed(1) + "%";
    tip.style.left = hit.x + "px";
    tip.style.top = hit.y + "px";
  });

  function endDrag(event) {
    if (!dragging) return;
    dragging = false;
    canvas.classList.remove("is-dragging");
    try {
      if (event && canvas.hasPointerCapture(event.pointerId)) {
        canvas.releasePointerCapture(event.pointerId);
      }
    } catch (error) {
      /* the pointer may already be gone */
    }
  }
  canvas.addEventListener("pointerup", endDrag);
  canvas.addEventListener("pointercancel", endDrag);
  canvas.addEventListener("pointerleave", function () {
    hoverPoint = null;
    if (tip) tip.hidden = true;
    endDrag(null);
    draw();
  });

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          visible = entry.isIntersecting;
        });
      },
      { threshold: 0 }
    ).observe(canvas);
  }

  resize();
  if (!reduceMotion) requestAnimationFrame(animate);
})();
