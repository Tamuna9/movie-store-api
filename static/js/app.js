const state = {
    movies: [],
    filteredMovies: [],
    cart: [],
    genre: "All",
    query: "",
};

const palettes = [
    { bg: "#df6249", ink: "#fff8e9", shape: "#efc95a" },
    { bg: "#303642", ink: "#fffaf0", shape: "#9fadd8" },
    { bg: "#9da989", ink: "#fffdf6", shape: "#e6c864" },
    { bg: "#c9b7dc", ink: "#272326", shape: "#ef775c" },
    { bg: "#e7c95f", ink: "#28231d", shape: "#f5eee2" },
    { bg: "#7f9bb0", ink: "#fffdf6", shape: "#e5a05e" },
];

const elements = {
    movieGrid: document.querySelector("#movieGrid"),
    resultCount: document.querySelector("#resultCount"),
    genreFilters: document.querySelector("#genreFilters"),
    searchForm: document.querySelector("#searchForm"),
    searchInput: document.querySelector("#searchInput"),
    cartButton: document.querySelector("#cartButton"),
    cartCount: document.querySelector("#cartCount"),
    cartDrawer: document.querySelector("#cartDrawer"),
    drawerOverlay: document.querySelector("#drawerOverlay"),
    closeCart: document.querySelector("#closeCart"),
    cartItems: document.querySelector("#cartItems"),
    cartTotal: document.querySelector("#cartTotal"),
    checkoutButton: document.querySelector("#checkoutButton"),
    toast: document.querySelector("#toast"),
};

document.querySelector("#year").textContent = new Date().getFullYear();

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function paletteFor(id) {
    return palettes[Math.abs(Number(id) || 0) % palettes.length];
}

function shortGenre(genre) {
    return genre.split("|")[0] || "Cinema";
}

function showToast(message) {
    elements.toast.textContent = message;
    elements.toast.classList.add("show");
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => elements.toast.classList.remove("show"), 2500);
}

async function requestJson(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || "Something went wrong");
    }
    return data;
}

function getGenres() {
    const genres = new Set();
    state.movies.forEach((movie) => {
        movie.genre.split("|").forEach((genre) => genres.add(genre));
    });
    return ["All", ...Array.from(genres).sort()];
}

function renderFilters() {
    elements.genreFilters.innerHTML = getGenres()
        .map((genre) => `
            <button class="filter-chip ${genre === state.genre ? "active" : ""}"
                    type="button" data-genre="${escapeHtml(genre)}">
                ${escapeHtml(genre)}
            </button>
        `)
        .join("");
}

function applyFilters() {
    const query = state.query.toLowerCase().trim();
    state.filteredMovies = state.movies.filter((movie) => {
        const matchesGenre = state.genre === "All" || movie.genre.split("|").includes(state.genre);
        const haystack = `${movie.title} ${movie.author} ${movie.genre}`.toLowerCase();
        return matchesGenre && (!query || haystack.includes(query));
    });
    renderMovies();
}

function renderMovies() {
    const movies = state.filteredMovies;
    elements.resultCount.textContent = `${movies.length} ${movies.length === 1 ? "film" : "films"} selected`;

    if (!movies.length) {
        elements.movieGrid.innerHTML = `
            <div class="empty-state">
                <strong>No films found</strong>
                <p>Try another title, director or genre.</p>
            </div>
        `;
        return;
    }

    elements.movieGrid.innerHTML = movies
        .map((movie, index) => {
            const palette = paletteFor(movie.id);
            const inCart = state.cart.some((item) => item.id === movie.id);
            const status = movie.availability_status || {
                code: movie.availability ? "available" : "unavailable",
                label: movie.availability ? "Available" : "Unavailable",
                message: "This title is currently unavailable.",
            };
            const buttonText = !movie.availability ? status.label : inCart ? "In your bag" : "Add to bag";
            return `
                <article class="movie-card">
                    <div class="movie-cover"
                         style="--cover-bg:${palette.bg};--cover-ink:${palette.ink};--shape-color:${palette.shape}">
                        <span class="movie-index">${String(index + 1).padStart(2, "0")} / MOVIESTAR</span>
                        <h3 class="movie-cover-title">${escapeHtml(movie.title)}</h3>
                        <div class="movie-cover-meta">
                            <span>${escapeHtml(shortGenre(movie.genre))}</span>
                            <span>${escapeHtml(status.label)}</span>
                        </div>
                    </div>
                    <div class="movie-details">
                        <div class="movie-title-row">
                            <h3 title="${escapeHtml(movie.title)}">${escapeHtml(movie.title)}</h3>
                            <span class="movie-price">$${Number(movie.price).toFixed(2)}</span>
                        </div>
                        <p class="movie-author">${escapeHtml(movie.author)} · ${escapeHtml(shortGenre(movie.genre))}</p>
                        <p class="availability-note status-${escapeHtml(status.code)}"
                           title="${escapeHtml(status.message)}">
                            <span aria-hidden="true"></span>${escapeHtml(status.message)}
                        </p>
                        <button class="add-button" type="button" data-add-id="${movie.id}"
                                ${!movie.availability || inCart ? "disabled" : ""}>
                            ${buttonText}
                        </button>
                    </div>
                </article>
            `;
        })
        .join("");
}

function renderCart() {
    elements.cartCount.textContent = state.cart.length;
    elements.cartTotal.textContent = `$${state.cart.reduce((sum, movie) => sum + Number(movie.price), 0).toFixed(2)}`;
    elements.checkoutButton.disabled = state.cart.length === 0;

    if (!state.cart.length) {
        elements.cartItems.innerHTML = `
            <div class="cart-empty">
                <div>
                    <span>◇</span>
                    <p>Your bag is waiting for a good story.</p>
                </div>
            </div>
        `;
        renderMovies();
        return;
    }

    elements.cartItems.innerHTML = state.cart
        .map((movie) => `
            <article class="cart-item">
                <div class="cart-thumb" style="--thumb-color:${paletteFor(movie.id).bg}">
                    ${escapeHtml(movie.title.charAt(0))}
                </div>
                <div>
                    <h3>${escapeHtml(movie.title)}</h3>
                    <p>${escapeHtml(shortGenre(movie.genre))} · $${Number(movie.price).toFixed(2)}</p>
                </div>
                <button class="remove-button" type="button" data-remove-id="${movie.id}"
                        aria-label="Remove ${escapeHtml(movie.title)}">×</button>
            </article>
        `)
        .join("");
    renderMovies();
}

function openCart() {
    elements.cartDrawer.classList.add("open");
    elements.drawerOverlay.classList.add("open");
    elements.cartDrawer.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    elements.closeCart.focus();
}

function closeCart() {
    elements.cartDrawer.classList.remove("open");
    elements.drawerOverlay.classList.remove("open");
    elements.cartDrawer.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
}

async function addToCart(movieId) {
    try {
        await requestJson("/cart", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: movieId }),
        });
        const movie = state.movies.find((item) => item.id === movieId);
        if (movie) state.cart.push(movie);
        renderCart();
        showToast("Added to your bag");
    } catch (error) {
        showToast(error.message);
    }
}

async function removeFromCart(movieId) {
    try {
        await requestJson(`/cart/${movieId}`, { method: "DELETE" });
        state.cart = state.cart.filter((movie) => movie.id !== movieId);
        renderCart();
        showToast("Removed from your bag");
    } catch (error) {
        showToast(error.message);
    }
}

async function completeCheckout() {
    const originalText = elements.checkoutButton.textContent;
    elements.checkoutButton.disabled = true;
    elements.checkoutButton.textContent = "Processing…";
    try {
        const result = await requestJson("/checkout", { method: "POST" });
        state.cart = [];
        renderCart();
        closeCart();
        showToast(result.message);
    } catch (error) {
        showToast(error.message);
    } finally {
        elements.checkoutButton.textContent = originalText;
        elements.checkoutButton.disabled = state.cart.length === 0;
    }
}

elements.searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    state.query = elements.searchInput.value;
    applyFilters();
    document.querySelector("#collection").scrollIntoView({ behavior: "smooth" });
});

elements.searchInput.addEventListener("input", () => {
    state.query = elements.searchInput.value;
    applyFilters();
});

elements.genreFilters.addEventListener("click", (event) => {
    const button = event.target.closest("[data-genre]");
    if (!button) return;
    state.genre = button.dataset.genre;
    renderFilters();
    applyFilters();
});

elements.movieGrid.addEventListener("click", (event) => {
    const button = event.target.closest("[data-add-id]");
    if (button) addToCart(Number(button.dataset.addId));
});

elements.cartItems.addEventListener("click", (event) => {
    const button = event.target.closest("[data-remove-id]");
    if (button) removeFromCart(Number(button.dataset.removeId));
});

elements.cartButton.addEventListener("click", openCart);
elements.closeCart.addEventListener("click", closeCart);
elements.drawerOverlay.addEventListener("click", closeCart);
elements.checkoutButton.addEventListener("click", completeCheckout);
document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeCart();
});

async function initialize() {
    try {
        const cacheBuster = Date.now();
        [state.movies, state.cart] = await Promise.all([
            requestJson(`/movies?fresh=${cacheBuster}`),
            requestJson(`/cart?fresh=${cacheBuster}`),
        ]);
        state.filteredMovies = state.movies;
        renderFilters();
        renderCart();
    } catch (error) {
        elements.movieGrid.innerHTML = `
            <div class="empty-state">
                <strong>We could not load the collection</strong>
                <p>${escapeHtml(error.message)}</p>
            </div>
        `;
        elements.resultCount.textContent = "Please refresh the page";
    }
}

initialize();
