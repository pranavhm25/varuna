/* Varuna landing page interactions: navigation, reveals, tagline and the
   three dimensional departure terrain. All values come from the project's
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
  var lastFocus = null;

  function setMenuDelays() {
    menuItems.forEach(function (item, i) {
      item.style.transitionDelay = Math.min(i * 60, 400) + "ms";
    });
  }

  function openMenu() {
    if (!menu || !toggle) return;
    lastFocus = document.activeElement;
    menu.hidden = false;
    setMenuDelays();
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
    if (returnFocus && lastFocus) lastFocus.focus({ preventScroll: true });
  }

  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      if (open) closeMenu(true);
      else openMenu();
    });

    menu.addEventListener("click", function (event) {
      var link = event.target.closest("a");
      if (link) closeMenu(false);
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        closeMenu(true);
      }
      if (event.key === "Tab" && toggle.getAttribute("aria-expanded") === "true") {
        var focusables = Array.prototype.slice.call(
          menu.querySelectorAll("a, button")
        );
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
      }
    });
  }

  /* -------------------------------------------------- section reveals --- */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var revealObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            revealObserver.unobserve(entry.target);
          }
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
      var id = link.getAttribute("href");
      return id && id.charAt(0) === "#" ? document.querySelector(id) : null;
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
  var canTilt = window.matchMedia("(pointer: fine)").matches && !reduceMotion;
  if (canTilt) {
    document.querySelectorAll(".tilt").forEach(function (card) {
      card.addEventListener("pointermove", function (event) {
        var rect = card.getBoundingClientRect();
        var px = event.clientX / rect.width - 0.5;
        var py = event.clientY / rect.height - 0.5;
        card.style.setProperty("--ry", (px * 5).toFixed(2) + "deg");
        card.style.setProperty("--rx", (-py * 5).toFixed(2) + "deg");
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

  var W = 0;
  var H = 0;
  var yaw = -0.38;
  var targetYaw = yaw;
  var dragging = false;
  var dragX = 0;
  var velocity = 0;
  var manual = false;
  var hoverPoint = null;
  var visible = true;
  var points = [];

  function project(x, y, z) {
    var cos = Math.cos(yaw);
    var sin = Math.sin(yaw);
    var rx = x * cos - z * sin;
    var rz = x * sin + z * cos;
    return { x: rx, y: rz * 0.62 - y * 0.92, depth: rz };
  }

  function computeFit() {
    var xs = [];
    var ys = [];
    function add(p) {
      xs.push(p.x);
      ys.push(p.y);
    }
    for (var y = 0; y < YEARS.length; y += 1) {
      add(project((y - 2) * 1, 0, -2.7));
      add(project((y - 2) * 1, 0, 2.7));
    }
    for (var d = 0; d < DISTRICTS.length; d += 1) {
      for (var yy = 0; yy < YEARS.length; yy += 1) {
        add(project((yy - 2) * 1, VALUES[d][yy] * 0.018, (d - 15) * 0.18));
      }
    }
    var minX = Math.min.apply(null, xs);
    var maxX = Math.max.apply(null, xs);
    var minY = Math.min.apply(null, ys);
    var maxY = Math.max.apply(null, ys);
    var scale = Math.min(
      (W * 0.86) / Math.max(maxX - minX, 0.001),
      (H * 0.8) / Math.max(maxY - minY, 0.001)
    );
    return {
      scale: scale,
      offX: W / 2 - ((minX + maxX) / 2) * scale,
      offY: H * 0.56 - ((minY + maxY) / 2) * scale
    };
  }

  function buildPoints(fit) {
    var out = [];
    for (var d = 0; d < DISTRICTS.length; d += 1) {
      for (var y = 0; y < YEARS.length; y += 1) {
        var value = VALUES[d][y];
        var p = project((y - 2) * 1, value * 0.018, (d - 15) * 0.18);
        var base = project((y - 2) * 1, 0, (d - 15) * 0.18);
        out.push({
          d: d,
          yi: y,
          v: value,
          x: p.x * fit.scale + fit.offX,
          y: p.y * fit.scale + fit.offY,
          bx: base.x * fit.scale + fit.offX,
          by: base.y * fit.scale + fit.offY,
          depth: p.depth
        });
      }
    }
    return out;
  }

  function basePoint(year, district, fit) {
    var p = project((year - 2) * 1, 0, (district - 15) * 0.18);
    return {
      x: p.x * fit.scale + fit.offX,
      y: p.y * fit.scale + fit.offY
    };
  }

  function draw() {
    if (!W || !H) return;
    ctx.clearRect(0, 0, W, H);
    var fit = computeFit();
    points = buildPoints(fit);

    /* the departure surface, filled far to near */
    var cells = [];
    for (var d = 0; d < DISTRICTS.length - 1; d += 1) {
      for (var y = 0; y < YEARS.length - 1; y += 1) {
        var p1 = points[d * 5 + y];
        var p2 = points[(d + 1) * 5 + y];
        var p3 = points[(d + 1) * 5 + y + 1];
        var p4 = points[d * 5 + y + 1];
        cells.push({
          p: [p1, p2, p3, p4],
          v: (p1.v + p2.v + p3.v + p4.v) / 4,
          depth: (p1.depth + p2.depth + p3.depth + p4.depth) / 4
        });
      }
    }
    cells.sort(function (a, b) {
      return a.depth - b.depth;
    });
    cells.forEach(function (cell) {
      var col = cell.v < 0 ? "205,150,70" : "120,168,205";
      var alpha = 0.08 + Math.min(Math.abs(cell.v) / 90, 1) * 0.2;
      ctx.fillStyle = "rgba(" + col + "," + alpha.toFixed(3) + ")";
      ctx.beginPath();
      ctx.moveTo(cell.p[0].x, cell.p[0].y);
      for (var i = 1; i < 4; i += 1) ctx.lineTo(cell.p[i].x, cell.p[i].y);
      ctx.closePath();
      ctx.fill();
    });

    /* ridge lines across the five seasons */
    ctx.lineWidth = 0.9;
    ctx.strokeStyle = "rgba(206,222,234,0.22)";
    for (var dd = 0; dd < DISTRICTS.length; dd += 1) {
      ctx.beginPath();
      for (var yy = 0; yy < YEARS.length; yy += 1) {
        var pt = points[dd * 5 + yy];
        if (yy === 0) ctx.moveTo(pt.x, pt.y);
        else ctx.lineTo(pt.x, pt.y);
      }
      ctx.stroke();
    }

    /* ticks under the year axis */
    ctx.strokeStyle = "rgba(255,255,255,0.22)";
    for (var yi = 0; yi < 5; yi += 1) {
      var edge = basePoint(yi, 30, fit);
      ctx.beginPath();
      ctx.moveTo(edge.x, edge.y - 4);
      ctx.lineTo(edge.x, edge.y);
      ctx.stroke();
    }

    /* extremes */
    var maxPoint = points.reduce(function (best, p) {
      return p.v > best.v ? p : best;
    }, points[0]);
    var minPoint = points.reduce(function (best, p) {
      return p.v < best.v ? p : best;
    }, points[0]);

    if (W > 420) {
      drawLabel(
        DISTRICTS[maxPoint.d] + " · " + YEARS[maxPoint.yi] + " · +" + maxPoint.v.toFixed(1) + "%",
        maxPoint.x,
        maxPoint.y,
        maxPoint.x > W * 0.62 ? "left" : "right"
      );
      drawLabel(
        DISTRICTS[minPoint.d] + " · " + YEARS[minPoint.yi] + " · " + (minPoint.v > 0 ? "+" : "") + minPoint.v.toFixed(1) + "%",
        minPoint.x,
        minPoint.y,
        minPoint.x > W * 0.62 ? "left" : "right"
      );
    }

    /* year labels */
    ctx.fillStyle = "#9b9b9b";
    ctx.font = '12px "Geist Mono", Consolas, monospace';
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    for (var yl = 0; yl < 5; yl += 1) {
      var edge = basePoint(yl, 30, fit);
      var lx = Math.max(18, Math.min(W - 18, edge.x));
      var ly = Math.min(edge.y + 12, H - 14);
      ctx.fillText(String(YEARS[yl]), lx, ly);
    }

    if (hoverPoint) {
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.arc(hoverPoint.x, hoverPoint.y, 3, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function drawLabel(text, x, y, side) {
    ctx.font = '12px "Geist Mono", Consolas, monospace';
    ctx.textBaseline = "bottom";
    var pad = 8;
    var width = ctx.measureText(text).width;
    var lx = side === "left" ? x - 10 - width : x + 10;
    lx = Math.max(4, Math.min(W - width - 4, lx));
    var ly = Math.max(18, y - 8);
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "left";
    ctx.shadowColor = "rgba(0,0,0,0.9)";
    ctx.shadowBlur = 4;
    ctx.fillText(text, lx, ly);
    ctx.shadowBlur = 0;
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
    if (!visible) {
      requestAnimationFrame(animate);
      return;
    }
    if (!manual && !dragging) {
      targetYaw = -0.38 + Math.sin(now / 9000) * 0.08;
    }
    if (!dragging) {
      if (Math.abs(velocity) > 0.0001) {
        targetYaw += velocity;
        velocity *= 0.94;
        manual = true;
      }
      yaw += (targetYaw - yaw) * 0.08;
    }
    draw();
    requestAnimationFrame(animate);
  }

  function nearestPoint(clientX, clientY) {
    var rect = canvas.getBoundingClientRect();
    var x = clientX - rect.left;
    var y = clientY - rect.top;
    var best = null;
    var bestDist = 18;
    points.forEach(function (p) {
      var dx = p.x - x;
      var dy = p.y - y;
      var dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < bestDist) {
        best = p;
        bestDist = dist;
      }
    });
    return best;
  }

  canvas.addEventListener("pointerdown", function (event) {
    dragging = true;
    dragX = event.clientX;
    velocity = 0;
    canvas.setPointerCapture(event.pointerId);
    canvas.classList.add("is-dragging");
    if (tip) tip.hidden = true;
  });

  canvas.addEventListener("pointermove", function (event) {
    if (dragging) {
      var dx = event.clientX - dragX;
      dragX = event.clientX;
      targetYaw += dx * 0.006;
      yaw += dx * 0.006;
      velocity = dx * 0.0006;
      manual = true;
      if (reduceMotion) draw();
      return;
    }
    if (event.pointerType !== "mouse") return;
    var hit = nearestPoint(event.clientX, event.clientY);
    hoverPoint = hit;
    if (!tip) return;
    if (!hit) {
      tip.hidden = true;
      return;
    }
    tip.hidden = false;
    tip.textContent =
      DISTRICTS[hit.d] + " · " + YEARS[hit.yi] + " · " +
      (hit.v > 0 ? "+" : "") + hit.v.toFixed(1) + "%";
    var rect = canvas.getBoundingClientRect();
    tip.style.left = hit.x + "px";
    tip.style.top = hit.y + "px";
  });

  function endDrag(event) {
    if (!dragging) return;
    dragging = false;
    canvas.classList.remove("is-dragging");
    if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
  }
  canvas.addEventListener("pointerup", endDrag);
  canvas.addEventListener("pointercancel", endDrag);
  canvas.addEventListener("pointerleave", function () {
    hoverPoint = null;
    if (tip) tip.hidden = true;
    endDrag({ pointerId: 0 });
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
  if (!reduceMotion) {
    requestAnimationFrame(animate);
  }
})();
