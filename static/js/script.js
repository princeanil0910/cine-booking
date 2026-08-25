document.addEventListener("DOMContentLoaded", () => {
  const promoSlides = [...document.querySelectorAll(".promo-slide")];
  const promoDots = [...document.querySelectorAll("[data-promo-dot]")];
  let promoIndex = 0;

  function showPromo(index) {
    promoIndex = (index + promoSlides.length) % promoSlides.length;
    promoSlides.forEach((slide, position) => slide.classList.toggle("active", position === promoIndex));
    promoDots.forEach((dot, position) => dot.classList.toggle("active", position === promoIndex));
  }

  document.querySelectorAll("[data-promo-direction]").forEach(button => {
    button.addEventListener("click", () => showPromo(promoIndex + Number(button.dataset.promoDirection)));
  });
  promoDots.forEach(dot => dot.addEventListener("click", () => showPromo(Number(dot.dataset.promoDot))));
  if (promoSlides.length > 1) setInterval(() => showPromo(promoIndex + 1), 6000);

  const movieSearch = document.getElementById("movieSearch");
  const clearSearch = document.getElementById("clearSearch");
  const searchResult = document.getElementById("searchResult");
  const movieCards = [...document.querySelectorAll("[data-movie-card]")];

  function filterMovies() {
    if (!movieSearch || !movieCards.length) return;
    const query = movieSearch.value.trim().toLowerCase();
    let visible = 0;
    movieCards.forEach(card => {
      const matches = !query || card.dataset.searchText.toLowerCase().includes(query);
      card.hidden = !matches;
      if (matches) visible += 1;
    });
    clearSearch.hidden = !query;
    searchResult.textContent = query ? `${visible} movie${visible === 1 ? "" : "s"} found` : "";
  }

  movieSearch?.addEventListener("input", filterMovies);
  clearSearch?.addEventListener("click", () => {
    movieSearch.value = "";
    filterMovies();
    movieSearch.focus();
  });
  filterMovies();

  document.querySelectorAll("[data-coming-soon]").forEach(button => {
    button.addEventListener("click", () => {
      button.textContent = "Reminder set";
      button.classList.add("is-set");
    });
  });

  const recommendedShelf = document.querySelector(".recommended-shelf");
  document.querySelector("[data-shelf-next]")?.addEventListener("click", () => {
    recommendedShelf?.scrollBy({left: 330, behavior: "smooth"});
  });
  document.querySelector("[data-cast-next]")?.addEventListener("click", () => {
    document.querySelector(".cast-shelf")?.scrollBy({left: 300, behavior: "smooth"});
  });

  const bookingCard = document.querySelector("[data-booking-code]");
  if (bookingCard) {
    const bookingCode = bookingCard.dataset.bookingCode;
    let lastUpdated = bookingCard.dataset.updatedAt;
    setInterval(async () => {
      try {
        const response = await fetch(`/api/booking/${bookingCode}`);
        const data = await response.json();
        if (data.ok && data.updated_at && data.updated_at !== lastUpdated) {
          lastUpdated = data.updated_at;
          bookingCard.dataset.updatedAt = data.updated_at;
          bookingCard.querySelector(".status-top strong").textContent = data.booking_status;
          bookingCard.querySelector(".status-grid div:nth-child(4) strong").textContent = data.payment_status;
          document.getElementById("bookingUpdate").textContent = `Updated by admin at ${data.updated_at}`;
          document.getElementById("bookingUpdate").classList.add("is-new");
        }
      } catch (_) {}
    }, 10000);
  }

  const map = document.querySelector(".seat-map");
  const form = document.getElementById("bookingForm");

  if (map && form) {
    const emailInput = form.querySelector('input[name="email"]');
    const price = Number(document.querySelector(".booking-card")?.dataset?.price || 0);
    // Price is injected below from the showtime card when needed.
    const showPriceText = document.querySelector(".booking-layout .booking-card h2");
    const urlParts = window.location.pathname.split("/");
    const showtimeId = map.dataset.showtime;

    // Read per-seat price from the server-rendered page through a safe fallback.
    const seatPrice = Number(document.body.dataset.seatPrice || "0") || Number(
      document.querySelector(".seat-price")?.dataset?.price || "0"
    );

    let selected = new Set();
    const totalEl = document.getElementById("total");
    const payAmount = document.getElementById("payAmount");
    const seatSummary = document.getElementById("seatSummary");
    const seatsInput = document.getElementById("seatsInput");
    const msg = document.getElementById("formMsg");

    emailInput?.addEventListener("input", () => {
      emailInput.value = emailInput.value.replace(/\s+/g, "");
    });

    // The Flask template exposes the exact show price through this element if present.
    const priceNode = document.querySelector("[data-ticket-price]");
    const ticketPrice = Number(priceNode?.dataset?.ticketPrice || 0);

    function update() {
      const seats = [...selected].sort();
      const total = seats.length * ticketPrice;
      seatSummary.textContent = seats.length ? seats.join(", ") : "None";
      seatsInput.value = seats.join(",");
      totalEl.textContent = `₹${total}`;
      payAmount.textContent = total;
    }

    map.querySelectorAll(".seat:not(.taken)").forEach(btn => {
      btn.addEventListener("click", () => {
        const seat = btn.dataset.seat;
        if (selected.has(seat)) {
          selected.delete(seat);
          btn.classList.remove("selected");
        } else {
          selected.add(seat);
          btn.classList.add("selected");
        }
        update();
      });
    });

    form.addEventListener("submit", async e => {
      e.preventDefault();
      if (!selected.size) {
        msg.textContent = "Please select at least one seat.";
        msg.className = "form-msg err";
        return;
      }
      msg.textContent = "Processing booking...";
      msg.className = "form-msg";
      try {
        const response = await fetch("/book", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(Object.fromEntries(new FormData(form).entries()))
        });
        const data = await response.json();
        if (!data.ok) throw new Error(data.error || "Booking failed.");
        window.location.href = data.tracking_url;
      } catch (err) {
        msg.textContent = err.message;
        msg.className = "form-msg err";
      }
    });

    // Refresh seat availability after a short interval.
    setInterval(async () => {
      try {
        const res = await fetch(`/api/show/${showtimeId}/seats`);
        const data = await res.json();
        (data.booked || []).forEach(seat => {
          const btn = map.querySelector(`[data-seat="${seat}"]`);
          if (btn) {
            btn.disabled = true;
            btn.classList.remove("selected");
            btn.classList.add("taken");
            selected.delete(seat);
          }
        });
        update();
      } catch (_) {}
    }, 15000);

    update();
  }

  const cancelBtn = document.querySelector("[data-cancel]");
  if (cancelBtn) {
    cancelBtn.addEventListener("click", async () => {
      if (!confirm("Cancel this booking?")) return;
      const code = cancelBtn.dataset.cancel;
      const res = await fetch(`/booking/${code}/cancel`, {method: "POST"});
      const data = await res.json();
      const msg = document.getElementById("cancelMsg");
      msg.textContent = data.message || data.error;
      msg.className = data.ok ? "form-msg ok" : "form-msg err";
      if (data.ok) setTimeout(() => location.reload(), 700);
    });
  }
});
