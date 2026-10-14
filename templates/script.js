/* RESILIO STORE — multi-page vanilla JavaScript storefront
   Demo only: no live inventory, authentication, order fulfilment, or payment processing. */
(() => {
  "use strict";

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const image = (id, width = 800) => `https://images.unsplash.com/${id}?auto=format&fit=crop&w=${width}&q=85`;
  const money = amount => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);
  const safeText = value => String(value ?? "").replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);

  const products = [
    { id:1, name:"Everyday Runner Sneakers", category:"Fashion", price:2499, oldPrice:3299, rating:4.9, reviews:128, badge:"BESTSELLER", isNew:false, popularity:98, image:image("photo-1542291026-7eec264c27ff"), colors:["#db4e3d","#e8e0d0","#343b32"], colorNames:["Sport red","Warm stone","Forest"], description:"Your go-to pair for busy days and spontaneous plans. A clean silhouette, a comfortable feel and an easy-to-style finish make these a natural part of your everyday rotation." },
    { id:2, name:"Minimal Everyday Backpack", category:"Accessories", price:1899, oldPrice:2299, rating:4.8, reviews:86, badge:"POPULAR", isNew:false, popularity:91, image:image("photo-1553062407-98eeb64c6a62"), colors:["#333c32","#b9a58b","#252525"], colorNames:["Olive","Sand","Black"], description:"A clean, versatile backpack for commutes, campus days and weekend escapes, with room for the essentials that travel with you." },
    { id:3, name:"Studio Wireless Headphones", category:"Tech", price:3499, oldPrice:4299, rating:4.8, reviews:204, badge:"SAVE 19%", isNew:false, popularity:99, image:image("photo-1505740420928-5e560c06d30e"), colors:["#d7d4c9","#272727","#8495a5"], colorNames:["Chalk","Onyx","Slate"], description:"A modern over-ear silhouette for playlists, podcasts and focus time. Designed to feel at home at your desk, on the commute and everywhere in between." },
    { id:4, name:"Ceramic Morning Mug", category:"Home", price:599, oldPrice:799, rating:4.7, reviews:62, badge:"EVERYDAY FAVOURITE", isNew:false, popularity:78, image:image("photo-1514228742587-6b1558fcca3d"), colors:["#e7dfcf","#9caa87","#bf8977"], colorNames:["Oat","Sage","Clay"], description:"A thoughtfully shaped ceramic mug for slow mornings, desk breaks and your favourite warm drink. The small ritual deserves a good object." },
    { id:5, name:"Essential Skin Care Set", category:"Beauty", price:1299, oldPrice:1599, rating:4.8, reviews:112, badge:"GLOW PICK", isNew:false, popularity:87, image:image("photo-1601049541289-9b1b7bbbfe19"), colors:["#e8c9b6","#f0e8dc"], colorNames:["Rose beige","Cream"], description:"A simple self-care ritual for your daily routine, presented as a thoughtful gift set. Check actual ingredients and suitability with the real supplier before selling." },
    { id:6, name:"Classic Cotton Overshirt", category:"Fashion", price:1599, oldPrice:1999, rating:4.7, reviews:74, badge:"NEW", isNew:true, popularity:80, image:image("photo-1598033129183-c4f50c736f10"), colors:["#c4b59e","#5b6855","#e5e0d5"], colorNames:["Taupe","Moss","Ivory"], description:"An easy layering piece with a relaxed fit. Wear it over a tee or on its own for an effortless look that works across seasons." },
    { id:7, name:"Smart Everyday Watch", category:"Tech", price:2999, oldPrice:3799, rating:4.6, reviews:145, badge:"TRENDING", isNew:false, popularity:94, image:image("photo-1523275335684-37898b6baf30"), colors:["#292929","#d1b88b","#8b9c88"], colorNames:["Black","Brass","Sage"], description:"A versatile everyday watch with a clean design that moves easily from casual outfits to smarter occasions. Product specifications should be confirmed with the actual seller." },
    { id:8, name:"Sculptural Table Lamp", category:"Home", price:2199, oldPrice:2799, rating:4.9, reviews:51, badge:"DESIGN PICK", isNew:true, popularity:85, image:image("photo-1507473885765-e6ed057f782c"), colors:["#ded6c8","#8c9780"], colorNames:["Linen","Olive"], description:"Warm light and a sculptural silhouette bring atmosphere to bedside tables, reading corners and workspaces. A small shift can change a whole room." },
    { id:9, name:"Canvas Weekend Tote", category:"Accessories", price:899, oldPrice:1199, rating:4.7, reviews:93, badge:"GREAT VALUE", isNew:false, popularity:83, image:image("photo-1544816155-12df9643f363"), colors:["#c9b99d","#626d56","#b5aaa0"], colorNames:["Natural","Olive","Stone"], description:"A roomy canvas carryall for errands, books and weekend plans. Simple, practical and easy to take anywhere." },
    { id:10, name:"Wireless Desk Speaker", category:"Tech", price:1799, oldPrice:2199, rating:4.6, reviews:68, badge:"NEW", isNew:true, popularity:75, image:image("photo-1608043152269-423dbba4e7e1"), colors:["#333333","#d6d0c4"], colorNames:["Graphite","Oat"], description:"A compact speaker for your desk, kitchen or bedside table. Bring a favourite soundtrack into everyday spaces." },
    { id:11, name:"Soft Knit Everyday Tee", category:"Fashion", price:799, oldPrice:999, rating:4.8, reviews:156, badge:"BESTSELLER", isNew:false, popularity:96, image:image("photo-1521572163474-6864f9cf17ab"), colors:["#eae5dc","#454d43","#b9b4a8"], colorNames:["Cream","Forest","Grey"], description:"A reliable wardrobe essential with a relaxed shape. Pair it with denim, layered looks or your favourite weekend trousers." },
    { id:12, name:"Daily Hydration Bottle", category:"Accessories", price:699, oldPrice:899, rating:4.7, reviews:118, badge:"DAILY ESSENTIAL", isNew:false, popularity:90, image:image("photo-1602143407151-7111542de6e8"), colors:["#d4dfca","#ded5c6","#3c4c40"], colorNames:["Pistachio","Sand","Forest"], description:"A reusable bottle for desk days, workouts and travel. Keep your hydration routine close at hand and easy to remember." },
    { id:13, name:"Cozy Textured Cushion", category:"Home", price:999, oldPrice:1299, rating:4.8, reviews:48, badge:"HOME FAVOURITE", isNew:false, popularity:74, image:image("photo-1584100936595-c0654b55a2e2"), colors:["#d5c7ae","#9eaa91","#b5a0a0"], colorNames:["Oat","Sage","Dusty rose"], description:"Give a favourite chair or sofa a softer touch with a textured cushion in an easy-to-pair neutral tone." },
    { id:14, name:"Everyday Crossbody Bag", category:"Fashion", price:1399, oldPrice:1799, rating:4.7, reviews:81, badge:"STYLE PICK", isNew:true, popularity:86, image:image("photo-1548036328-c9fa89d128fa"), colors:["#9d6f52","#282827","#d5c5ac"], colorNames:["Cognac","Black","Oat"], description:"Keep the essentials close in a compact crossbody bag with a versatile silhouette for errands, travel and evenings out." },
    { id:15, name:"Gentle Self-Care Kit", category:"Beauty", price:1099, oldPrice:1399, rating:4.6, reviews:57, badge:"GIFT IDEA", isNew:false, popularity:72, image:image("photo-1608248543803-ba4f8c70ae0b"), colors:["#e8d5c6","#d8dfcf"], colorNames:["Blush","Sage"], description:"A self-care-inspired gift set for thoughtful gifting or a small moment of everyday indulgence. Confirm ingredients and supplier claims before launch." },
    { id:16, name:"Modern Desk Organizer", category:"Home", price:849, oldPrice:1099, rating:4.7, reviews:39, badge:"NEW", isNew:true, popularity:70, image:image("photo-1499951360447-b19be8fe80f5"), colors:["#cbbda7","#777f6b"], colorNames:["Natural","Moss"], description:"Give your desk a little breathing room with an organizer for everyday work essentials, stationery and accessories." }
  ];

  const slides = [
    { image:"photo-1542291026-7eec264c27ff", alt:"Sport red everyday sneakers", name:"The everyday runner", price:"₹2,499", id:1 },
    { image:"photo-1505740420928-5e560c06d30e", alt:"Studio headphones", name:"Sound, simplified", price:"₹3,499", id:3 },
    { image:"photo-1507473885765-e6ed057f782c", alt:"Sculptural table lamp", name:"Light a little differently", price:"₹2,199", id:8 }
  ];

  const readStorage = (key, fallback) => {
    try { const value = localStorage.getItem(key); return value ? JSON.parse(value) : fallback; }
    catch { return fallback; }
  };
  const writeStorage = (key, value) => { try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* current session remains usable */ } };

  let cart = readStorage("resilio-v2-cart", readStorage("resilio-cart", []));
  let wishlist = readStorage("resilio-v2-wishlist", readStorage("resilio-wishlist", []));
  let appliedPromo = readStorage("resilio-v2-promo", false) === true;
  let toastTimer = 0;
  let heroIndex = 0;
  let heroInterval = 0;
  let detailQty = 1;
  let maxPrice = 5000;
  let shopShowCount = 12;
  let shopView = "grid";
  let selectedColorIndex = 0;

  const productById = id => products.find(product => product.id === Number(id));
  // Defensively clean persisted data so stale or manually edited browser storage cannot break rendering.
  cart = (Array.isArray(cart) ? cart : []).reduce((clean, item) => {
    const id = Number(item?.id); const product = productById(id);
    const qty = Math.max(1, Math.min(99, Math.floor(Number(item?.qty) || 1)));
    if (!product) return clean;
    const variantIndex = Math.max(0, Math.min(product.colors.length - 1, Math.floor(Number(item?.variantIndex) || 0)));
    const existing = clean.find(entry => entry.id === id && entry.variantIndex === variantIndex);
    if (existing) existing.qty = Math.min(99, existing.qty + qty);
    else clean.push({ id, qty, variantIndex });
    return clean;
  }, []);
  wishlist = [...new Set((Array.isArray(wishlist) ? wishlist : []).map(Number).filter(id => Boolean(productById(id))))];
  writeStorage("resilio-v2-cart", cart);
  writeStorage("resilio-v2-wishlist", wishlist);
  const countCart = () => cart.reduce((sum, item) => sum + item.qty, 0);
  const subtotal = () => cart.reduce((sum, item) => { const p = productById(item.id); return sum + (p ? p.price * item.qty : 0); }, 0);
  const discountAmount = value => appliedPromo ? Math.round(value * .10) : 0;
  const shippingAmount = value => value === 0 || value >= 1999 ? 0 : 99;
  const totalAmount = value => value - discountAmount(value) + shippingAmount(value);

  function toast(message) {
    let el = $("#siteToast");
    if (!el) {
      el = document.createElement("div"); el.id = "siteToast"; el.className = "toast"; el.setAttribute("role", "status"); el.setAttribute("aria-live", "polite"); document.body.appendChild(el);
    }
    el.textContent = message; el.classList.add("show"); clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove("show"), 2400);
  }

  function headerMarkup() {
    return `
      <div class="announcement"><span>Complimentary shipping on orders over ₹1,999</span><a href="shop.html">Find your next favourite <span>↗</span></a></div>
      <header class="site-header" id="siteHeader">
        <button class="icon-btn mobile-menu-button" id="mobileMenu" aria-label="Open navigation">☰</button>
        <a class="logo" href="index.html" aria-label="Resilio Store home"><span class="logo-mark">r.</span><span>resilio<span class="logo-light">store</span></span></a>
        <nav class="main-nav" id="mainNav" aria-label="Main navigation">
          <a href="shop.html" data-nav="shop">Shop all</a><a href="shop.html?category=Fashion" data-nav="Fashion">Fashion</a><a href="shop.html?category=Tech" data-nav="Tech">Technology</a><a href="shop.html?category=Home" data-nav="Home">Home & living</a><a class="nav-sale" href="shop.html?sort=low">The good deals ↗</a>
        </nav>
        <div class="header-actions"><button class="icon-btn header-icon" id="searchToggle" aria-label="Search">⌕</button><a class="icon-btn header-icon" href="wishlist.html" aria-label="Wishlist">♡<span class="header-count" id="headerWishlistCount">0</span></a><button class="icon-btn header-icon" id="cartToggle" aria-label="Open shopping bag">♧<span class="header-count" id="headerCartCount">0</span></button></div>
      </header>
      <div class="search-strip" id="searchStrip"><span class="global-search-icon">⌕</span><form id="globalSearchForm" style="display:flex;flex:1"><input id="globalSearchInput" type="search" placeholder="Search products, categories and little favourites..." aria-label="Search products" autocomplete="off" aria-expanded="false" aria-controls="searchSuggestions"><button type="submit" aria-label="Submit search">↗</button></form><button id="closeGlobalSearch" aria-label="Close search">×</button></div><div id="searchSuggestions" class="search-suggestions hidden"></div>
      <div id="globalOverlay" class="overlay"></div>
      <aside class="cart-drawer" id="cartDrawer" aria-label="Shopping bag" aria-hidden="true">
        <div class="drawer-heading"><div><span class="eyebrow">YOUR LITTLE FINDS</span><h2>Your bag <span id="drawerCartCount">(0)</span></h2></div><button class="icon-btn" id="closeCartDrawer" aria-label="Close bag">×</button></div>
        <div class="drawer-shipping"><p id="drawerShippingMessage">Free shipping on orders over ₹1,999.</p><div class="progress-track"><span id="drawerShippingProgress"></span></div></div>
        <div class="drawer-items" id="drawerCartItems"></div>
        <div class="drawer-empty hidden" id="drawerCartEmpty"><div class="empty-illustration">♡</div><h3>Room for something good.</h3><p>Your bag is empty for now. Let's find something for your everyday.</p><a class="btn btn-primary" href="shop.html">Explore the shop ↗</a></div>
        <div class="drawer-bottom" id="drawerCartBottom"><div class="summary-line"><span>Subtotal</span><strong id="drawerSubtotal">₹0</strong></div><div class="summary-line"><span>Shipping</span><strong id="drawerShippingCost">—</strong></div><div class="summary-line discount-line hidden" id="drawerDiscountRow"><span>WELCOME10</span><strong id="drawerDiscount">−₹0</strong></div><div class="summary-line summary-total"><span>Total</span><strong id="drawerTotal">₹0</strong></div><a class="btn btn-primary summary-checkout" href="cart.html">View bag & checkout <span>↗</span></a></div>
      </aside>
      <div class="modal-backdrop" id="quickModalBackdrop"><section class="quick-modal" role="dialog" aria-modal="true" aria-label="Quick product view"><button class="icon-btn modal-close" id="closeQuickModal" aria-label="Close product view">×</button><div id="quickModalContent"></div></section></div>
      <button class="back-top" id="backTop" aria-label="Back to top">↑</button>`;
  }

  function footerMarkup() {
    return `<footer class="site-footer"><div class="footer-main">
      <div class="footer-brand"><a class="logo footer-logo" href="index.html"><span class="logo-mark">r.</span><span>resilio<span class="logo-light">store</span></span></a><p>A considered edit of everyday essentials. A little less noise, a little more meaning in the things you choose.</p><div class="social-row"><a href="contact.html" aria-label="Instagram">ig ↗</a><a href="contact.html" aria-label="Pinterest">p ↗</a><a href="contact.html" aria-label="Facebook">f ↗</a></div></div>
      <div class="footer-column"><b>Explore</b><a href="shop.html">Shop everything</a><a href="shop.html?category=Fashion">Fashion</a><a href="shop.html?category=Tech">Technology</a><a href="shop.html?category=Home">Home & living</a><a href="shop.html?sort=newest">New arrivals</a></div>
      <div class="footer-column"><b>Make yourself at home</b><a href="wishlist.html">Your wishlist</a><a href="cart.html">Your bag</a><a href="about.html">Our story</a><a href="contact.html">Contact us</a><a href="contact.html#contactForm">FAQs & support</a></div>
      <div class="footer-column"><b>The important bits</b><a href="contact.html">Shipping information</a><a href="contact.html">Returns & exchanges</a><a href="contact.html">Privacy policy</a><a href="contact.html">Terms of service</a><a href="contact.html">Cookie preferences</a></div>
    </div><div class="footer-bottom"><span>© <span id="footerYear"></span> Resilio Store · Everyday, elevated.</span><span class="footer-payment">VISA · MASTERCARD · UPI · RUPAY</span><a href="#top">Back to top ↑</a></div><p class="footer-disclaimer">Frontend concept demonstration. Products, ratings, reviews, offers and business details are illustrative. No real order or payment is processed.</p></footer>`;
  }

  function mountChrome() {
    const header = $("#site-header"); const footer = $("#site-footer");
    if (header) header.innerHTML = headerMarkup();
    if (footer) footer.innerHTML = footerMarkup();
    if (!$("#site-header")) return;
    $("#footerYear").textContent = new Date().getFullYear();
    const page = document.body.dataset.page || "";
    $$("[data-nav]").forEach(link => {
      const category = new URLSearchParams(location.search).get("category");
      if ((page === "shop" && link.dataset.nav === "shop" && !category) || (category && link.dataset.nav === category)) link.classList.add("active");
    });
    updateHeaderCounts();
    bindChromeEvents();
    renderDrawerCart();
  }

  function updateHeaderCounts() {
    const cartCount = $("#headerCartCount"); const wishCount = $("#headerWishlistCount");
    if (cartCount) cartCount.textContent = countCart();
    if (wishCount) wishCount.textContent = wishlist.length;
    const drawerCount = $("#drawerCartCount"); if (drawerCount) drawerCount.textContent = `(${countCart()})`;
  }

  function bindChromeEvents() {
    const drawer = $("#cartDrawer"); const overlay = $("#globalOverlay");
    const closeDrawer = () => { drawer?.classList.remove("open"); overlay?.classList.remove("open"); drawer?.setAttribute("aria-hidden", "true"); document.body.classList.remove("no-scroll"); };
    const openDrawer = () => { renderDrawerCart(); drawer?.classList.add("open"); overlay?.classList.add("open"); drawer?.setAttribute("aria-hidden", "false"); document.body.classList.add("no-scroll"); };
    $("#cartToggle")?.addEventListener("click", openDrawer);
    $("#closeCartDrawer")?.addEventListener("click", closeDrawer);
    overlay?.addEventListener("click", () => { closeDrawer(); closeQuickModal(); });
    $("#mobileMenu")?.addEventListener("click", () => $("#mainNav")?.classList.toggle("open"));
    document.addEventListener("click", event => {
      const nav = $("#mainNav"); const menu = $("#mobileMenu");
      if (nav && menu && !nav.contains(event.target) && !menu.contains(event.target)) nav.classList.remove("open");
    });
    $("#searchToggle")?.addEventListener("click", () => { $("#searchStrip")?.classList.add("open"); $("#globalSearchInput")?.focus(); });
    $("#closeGlobalSearch")?.addEventListener("click", () => { $("#searchStrip")?.classList.remove("open"); $("#searchSuggestions")?.classList.add("hidden"); });
    $("#globalSearchForm")?.addEventListener("submit", event => {
      event.preventDefault(); const query = $("#globalSearchInput").value.trim();
      location.href = `shop.html${query ? `?q=${encodeURIComponent(query)}` : ""}`;
    });
    $("#globalSearchInput")?.addEventListener("input", event => renderSearchSuggestions(event.target.value));
    $("#globalSearchInput")?.addEventListener("keydown", event => {
      if (event.key === "Escape") { $("#searchSuggestions")?.classList.add("hidden"); $("#searchStrip")?.classList.remove("open"); }
      if (event.key === "ArrowDown") { const first = $(".search-suggestion", $("#searchSuggestions")); if (first) { event.preventDefault(); first.focus(); } }
    });
    $("#searchSuggestions")?.addEventListener("click", event => {
      const item = event.target.closest("[data-search-product]");
      const all = event.target.closest("[data-search-all]");
      if (item) location.href = `product.html?id=${Number(item.dataset.searchProduct)}`;
      if (all) location.href = `shop.html?q=${encodeURIComponent($("#globalSearchInput").value.trim())}`;
    });
    $("#drawerCartItems")?.addEventListener("click", event => {
      const button = event.target.closest("[data-drawer-action]"); if (!button) return;
      const id = Number(button.dataset.id); const variantIndex = Number(button.dataset.variantIndex || 0); const action = button.dataset.drawerAction;
      if (action === "plus") changeQty(id, 1, variantIndex); if (action === "minus") changeQty(id, -1, variantIndex); if (action === "remove") removeCartItem(id, variantIndex); if (action === "save") moveCartToWishlist(id, variantIndex);
    });
    $("#closeQuickModal")?.addEventListener("click", closeQuickModal);
    $("#quickModalBackdrop")?.addEventListener("click", event => { if (event.target.id === "quickModalBackdrop") closeQuickModal(); });
    $("#quickModalContent")?.addEventListener("click", event => {
      const add = event.target.closest("[data-quick-add]"); const wish = event.target.closest("[data-quick-wish]");
      if (add) { addToCart(Number(add.dataset.quickAdd)); closeQuickModal(); }
      if (wish) toggleWishlist(Number(wish.dataset.quickWish));
    });
    document.addEventListener("keydown", event => {
      if (event.key === "Escape") { closeDrawer(); closeQuickModal(); $("#searchStrip")?.classList.remove("open"); $("#mainNav")?.classList.remove("open"); }
    });
    const backTop = $("#backTop");
    window.addEventListener("scroll", () => {
      $("#siteHeader")?.classList.toggle("scrolled", window.scrollY > 10);
      backTop?.classList.toggle("visible", window.scrollY > 500);
    }, { passive:true });
    backTop?.addEventListener("click", () => window.scrollTo({ top:0, behavior:"smooth" }));
  }

  function badgeClass(product) {
    if (product.isNew) return "new";
    if (product.badge === "BESTSELLER") return "bestseller";
    if (product.badge === "TRENDING") return "trending";
    return product.oldPrice > product.price ? "sale" : "";
  }

  function productCard(product, index = 0) {
    const wish = wishlist.includes(product.id); const discount = Math.round((1 - product.price / product.oldPrice) * 100);
    return `<article class="product-card" style="animation-delay:${Math.min(index,8)*30}ms"><div class="product-image"><a href="product.html?id=${product.id}" aria-label="View ${safeText(product.name)}"><img src="${product.image}" alt="${safeText(product.name)}" loading="lazy"></a>${product.badge ? `<span class="product-badge ${badgeClass(product)}">${safeText(product.badge)}</span>` : ""}<button class="product-heart ${wish ? "active" : ""}" data-action="wishlist" data-id="${product.id}" aria-label="${wish ? "Remove from" : "Add to"} wishlist">${wish ? "♥" : "♡"}</button><button class="quick-view-button" data-action="quick" data-id="${product.id}">Quick look ↗</button></div><div class="product-info"><span class="product-category">${safeText(product.category)}</span><div class="product-name-row"><a class="product-name" href="product.html?id=${product.id}">${safeText(product.name)}</a><span class="product-rating"><span class="star">★</span> ${product.rating}</span></div><div class="product-price-row"><span class="product-price">${money(product.price)}</span><span class="old-price">${money(product.oldPrice)}</span><span class="discount-percent">${discount}% off</span></div><div class="product-card-footer"><div class="swatches">${product.colors.slice(0,3).map(color => `<span class="swatch" style="background:${color}" title="Colour option"></span>`).join("")}</div><button class="add-cart-btn" data-action="add" data-id="${product.id}">＋ Add to bag</button></div></div></article>`;
  }

  function bindProductGrid(grid) {
    if (!grid || grid.dataset.productGridBound === "true") return;
    grid.dataset.productGridBound = "true";
    grid.addEventListener("click", event => {
      const button = event.target.closest("[data-action]"); if (!button) return;
      const id = Number(button.dataset.id); const action = button.dataset.action;
      if (action === "add") addToCart(id);
      if (action === "wishlist") toggleWishlist(id);
      if (action === "quick") openQuickModal(id);
    });
  }

  function addToCart(id, qty = 1, variantIndex = 0) {
    const product = productById(id); if (!product) return;
    const amount = Math.max(1, Math.min(99, Math.floor(Number(qty) || 1)));
    const variant = Math.max(0, Math.min(product.colors.length - 1, Math.floor(Number(variantIndex) || 0)));
    const existing = cart.find(item => item.id === Number(id) && item.variantIndex === variant);
    if (existing) {
      if (existing.qty >= 99) { toast("You've reached the quantity limit for this item."); return; }
      existing.qty = Math.min(99, existing.qty + amount);
    } else cart.push({ id: Number(id), qty: amount, variantIndex: variant });
    saveCart(); updateHeaderCounts(); renderDrawerCart(); renderCartPage(); renderCheckoutSummary();
    const colour = product.colorNames[variant] ? ` · ${product.colorNames[variant]}` : "";
    toast(`${product.name}${colour} added to your bag`);
  }
  function moveCartToWishlist(id, variantIndex = 0) {
    const product = productById(id); if (!product) return;
    cart = cart.filter(item => !(item.id === Number(id) && Number(item.variantIndex || 0) === Number(variantIndex || 0)));
    if (!wishlist.includes(Number(id))) wishlist.push(Number(id));
    saveCart(); saveWishlist(); renderDrawerCart(); renderCartPage(); renderCheckoutSummary();
    renderWishlistPage(); refreshProductCards();
    toast(`${product.name} saved for later`);
  }
  function changeQty(id, delta, variantIndex = 0) {
    const item = cart.find(entry => entry.id === Number(id) && Number(entry.variantIndex || 0) === Number(variantIndex || 0)); if (!item) return;
    item.qty += delta; if (item.qty <= 0) cart = cart.filter(entry => !(entry.id === Number(id) && Number(entry.variantIndex || 0) === Number(variantIndex || 0)));
    item.qty = Math.min(99, item.qty);
    saveCart(); updateHeaderCounts(); renderDrawerCart(); renderCartPage(); renderCheckoutSummary();
  }
  function removeCartItem(id, variantIndex = 0) {
    cart = cart.filter(item => !(item.id === Number(id) && Number(item.variantIndex || 0) === Number(variantIndex || 0)));
    saveCart(); updateHeaderCounts(); renderDrawerCart(); renderCartPage(); renderCheckoutSummary(); toast("Removed from your bag");
  }
  function saveCart() { writeStorage("resilio-v2-cart", cart); writeStorage("resilio-v2-promo", appliedPromo); }
  function saveWishlist() { writeStorage("resilio-v2-wishlist", wishlist); updateHeaderCounts(); }
  function toggleWishlist(id) {
    const product = productById(id); if (!product) return;
    if (wishlist.includes(id)) { wishlist = wishlist.filter(existing => existing !== id); toast("Removed from your wishlist"); }
    else { wishlist.push(id); toast("Saved to your wishlist ♡"); }
    saveWishlist(); refreshProductCards(); renderWishlistPage(); updateProductWishButton(id);
  }
  function refreshProductCards() {
    const page = document.body.dataset.page;
    if (page === "home") { renderHomeProducts(); }
    if (page === "shop") renderShopProducts();
    if (page === "product") renderRelatedProducts();
    if (page === "cart") renderCartRecommendations();
  }
  function renderDrawerCart() {
    const list = $("#drawerCartItems"); if (!list) return;
    const subtotalValue = subtotal(); const discount = discountAmount(subtotalValue); const ship = shippingAmount(subtotalValue); const total = totalAmount(subtotalValue);
    list.innerHTML = cart.map(item => {
      const p = productById(item.id); if (!p) return "";
      const variantIndex = Math.max(0, Math.min(p.colors.length - 1, Number(item.variantIndex) || 0));
      const variantLabel = p.colorNames[variantIndex] || "Default colour";
      return `<div class="drawer-item"><img src="${p.image}" alt="${safeText(p.name)}"><div><strong>${safeText(p.name)}</strong><small>${safeText(p.category)} · ${safeText(variantLabel)}</small><div class="drawer-qty"><button data-drawer-action="minus" data-id="${p.id}" data-variant-index="${variantIndex}" aria-label="Decrease quantity">−</button><span>${item.qty}</span><button data-drawer-action="plus" data-id="${p.id}" data-variant-index="${variantIndex}" aria-label="Increase quantity">+</button></div><div class="drawer-item-actions"><button class="drawer-remove" data-drawer-action="remove" data-id="${p.id}" data-variant-index="${variantIndex}">Remove</button><button class="drawer-save-later" data-drawer-action="save" data-id="${p.id}" data-variant-index="${variantIndex}">Save for later ♡</button></div></div><span class="drawer-price">${money(p.price * item.qty)}</span></div>`;
    }).join("");
    const empty = cart.length === 0; $("#drawerCartEmpty")?.classList.toggle("hidden", !empty); $("#drawerCartBottom")?.classList.toggle("hidden", empty); list.classList.toggle("hidden", empty);
    $("#drawerSubtotal").textContent = money(subtotalValue); $("#drawerShippingCost").textContent = subtotalValue === 0 ? "—" : ship ? money(ship) : "FREE"; $("#drawerTotal").textContent = money(total); $("#drawerDiscount").textContent = `−${money(discount)}`; $("#drawerDiscountRow")?.classList.toggle("hidden", discount === 0);
    const remaining = Math.max(0, 1999 - subtotalValue); $("#drawerShippingMessage").textContent = subtotalValue === 0 ? "Free shipping on orders over ₹1,999." : remaining === 0 ? "Lovely! Complimentary shipping is unlocked." : `Add ${money(remaining)} more for complimentary shipping.`;
    $("#drawerShippingProgress").style.width = `${Math.min(100, subtotalValue / 1999 * 100)}%`; updateHeaderCounts();
  }

  function openQuickModal(id) {
    const p = productById(id); if (!p) return;
    const wish = wishlist.includes(id);
    $("#quickModalContent").innerHTML = `<div class="quick-view-content"><img src="${p.image}" alt="${safeText(p.name)}"><div><span class="eyebrow">${safeText(p.category)} · RESILIO EDIT</span><h2>${safeText(p.name)}</h2><div class="product-rating"><span class="star">★</span> ${p.rating} · ${p.reviews} sample ratings</div><div class="quick-view-price">${money(p.price)} <del>${money(p.oldPrice)}</del></div><p>${safeText(p.description)}</p><div class="swatches">${p.colors.map(color => `<span class="swatch" style="background:${color};width:17px;height:17px"></span>`).join("")}</div><a href="product.html?id=${p.id}" class="btn btn-outline" style="justify-content:center;margin-top:15px">View full details ↗</a><button class="btn btn-primary" data-quick-add="${p.id}">Add to bag <span>↗</span></button><button class="btn btn-outline" data-quick-wish="${p.id}">${wish ? "♥ Saved to wishlist" : "♡ Save to wishlist"}</button></div></div>`;
    $("#quickModalBackdrop")?.classList.add("open"); document.body.classList.add("no-scroll");
  }
  function closeQuickModal() { $("#quickModalBackdrop")?.classList.remove("open"); document.body.classList.remove("no-scroll"); }

  function renderHomeProducts() {
    const best = $("#homeBestsellers"); if (best) { best.innerHTML = [...products].sort((a,b) => b.popularity-a.popularity).slice(0,4).map(productCard).join(""); bindProductGrid(best); }
    const fresh = $("#homeNewArrivals"); if (fresh) { fresh.innerHTML = products.filter(p => p.isNew).slice(0,4).map(productCard).join(""); bindProductGrid(fresh); }
  }

  function getQueryProducts() {
    const params = new URLSearchParams(location.search); let result = [...products];
    const category = params.get("category"); const query = (params.get("q") || "").trim().toLowerCase(); const sort = params.get("sort") || "featured";
    if (category) result = result.filter(p => p.category.toLowerCase() === category.toLowerCase());
    if (query) result = result.filter(p => `${p.name} ${p.category} ${p.description} ${p.badge}`.toLowerCase().includes(query));
    if (sort === "popular" || sort === "featured") result.sort((a,b) => b.popularity-a.popularity);
    else if (sort === "low") result.sort((a,b) => a.price-b.price);
    else if (sort === "high") result.sort((a,b) => b.price-a.price);
    else if (sort === "rating") result.sort((a,b) => b.rating-a.rating);
    else if (sort === "newest") result.sort((a,b) => Number(b.isNew)-Number(a.isNew) || b.id-a.id);
    return { result, category:category || "All", query, sort };
  }

  function renderShopProducts() {
    const grid = $("#shopProductGrid"); if (!grid) return;
    let result = [...products]; const category = $('input[name="category"]:checked')?.value || "All"; const query = ($("#shopSearch")?.value || "").trim().toLowerCase();
    const sort = $("#shopSort")?.value || "featured"; const saleOnly = $("#saleOnly")?.checked || false; const newOnly = $("#newOnly")?.checked || false;
    result = result.filter(p => (category === "All" || p.category === category) && p.price <= maxPrice && (!saleOnly || p.oldPrice > p.price) && (!newOnly || p.isNew) && (!query || `${p.name} ${p.category} ${p.description} ${p.badge}`.toLowerCase().includes(query)));
    if (sort === "popular" || sort === "featured") result.sort((a,b) => b.popularity-a.popularity);
    if (sort === "low") result.sort((a,b) => a.price-b.price);
    if (sort === "high") result.sort((a,b) => b.price-a.price);
    if (sort === "rating") result.sort((a,b) => b.rating-a.rating);
    if (sort === "newest") result.sort((a,b) => Number(b.isNew)-Number(a.isNew) || b.id-a.id);
    grid.classList.toggle("compact-view", shopView === "compact");
    grid.innerHTML = result.slice(0,shopShowCount).map(productCard).join(""); bindProductGrid(grid);
    $("#shopResultCount").textContent = `Showing ${Math.min(result.length,shopShowCount)} of ${result.length} ${result.length === 1 ? "find" : "finds"}`;
    $("#shopEmpty")?.classList.toggle("hidden", result.length !== 0); grid.classList.toggle("hidden", result.length === 0);
    $("#shopLoadMore")?.classList.toggle("hidden", shopShowCount >= result.length || result.length === 0);
    const chips = [];
    if (category !== "All") chips.push({ key:"category", label:category });
    if (query) chips.push({ key:"query", label:`Search: ${query}` });
    if (maxPrice < 5000) chips.push({ key:"price", label:`Up to ${money(maxPrice)}` });
    if (saleOnly) chips.push({ key:"sale", label:"On offer" });
    if (newOnly) chips.push({ key:"new", label:"New arrivals" });
    $("#activeFilterChips").innerHTML = `<div class="filter-chip-list">${chips.map(c => `<button class="filter-chip-small" data-clear-filter="${c.key}">${safeText(c.label)} ×</button>`).join("")}</div>`;
  }

  function initShop() {
    const grid = $("#shopProductGrid"); if (!grid) return;
    const initial = getQueryProducts(); const params = new URLSearchParams(location.search);
    if (initial.category !== "All") { const input = $(`input[name="category"][value="${CSS.escape(initial.category)}"]`); if (input) input.checked = true; }
    if (initial.query) $("#shopSearch").value = initial.query;
    if (initial.sort) $("#shopSort").value = initial.sort;
    if (initial.sort === "newest") $("#shopSort").value = "newest";
    if (params.has("sort") && !["featured","popular","low","high","rating","newest"].includes(params.get("sort"))) $("#shopSort").value = "featured";
    $("#shopSearch").addEventListener("input", () => { shopShowCount = 12; renderShopProducts(); });
    $("#shopSort").addEventListener("change", () => { shopShowCount = 12; renderShopProducts(); });
    $$('input[name="category"]').forEach(input => input.addEventListener("change", () => { shopShowCount = 12; renderShopProducts(); }));
    $("#priceRange")?.addEventListener("input", event => { maxPrice = Number(event.target.value); $("#priceMaxText").textContent = money(maxPrice); shopShowCount = 12; renderShopProducts(); });
    $$('[data-max-price]').forEach(button => button.addEventListener("click", () => { maxPrice = Number(button.dataset.maxPrice); $("#priceRange").value = maxPrice; $("#priceMaxText").textContent = money(maxPrice); renderShopProducts(); }));
    $("#saleOnly")?.addEventListener("change", renderShopProducts); $("#newOnly")?.addEventListener("change", renderShopProducts);
    $("#shopLoadMore")?.addEventListener("click", () => { shopShowCount += 4; renderShopProducts(); });
    $("#shopEmptyReset")?.addEventListener("click", resetShop);
    $("#resetFilters")?.addEventListener("click", resetShop);
    $("#activeFilterChips")?.addEventListener("click", event => {
      const button = event.target.closest("[data-clear-filter]"); if (!button) return;
      const key = button.dataset.clearFilter;
      if (key === "category") { const radio = $('input[name="category"][value="All"]'); if (radio) radio.checked = true; }
      if (key === "query") $("#shopSearch").value = "";
      if (key === "price") { maxPrice = 5000; $("#priceRange").value = 5000; $("#priceMaxText").textContent = money(5000); }
      if (key === "sale") $("#saleOnly").checked = false;
      if (key === "new") $("#newOnly").checked = false;
      renderShopProducts();
    });
    $$('[data-filter-toggle]').forEach(button => button.addEventListener("click", () => {
      const content = $(`[data-filter-content="${button.dataset.filterToggle}"]`); if (!content) return;
      content.classList.toggle("hidden"); const span = $("span",button); if (span) span.textContent = content.classList.contains("hidden") ? "+" : "−";
    }));
    $$('[data-view]').forEach(button => button.addEventListener("click", () => { shopView = button.dataset.view === "compact" ? "compact" : "grid"; $$('[data-view]').forEach(b => b.classList.toggle("active", b === button)); renderShopProducts(); }));
    renderShopProducts();
  }
  function resetShop() {
    const all = $('input[name="category"][value="All"]'); if (all) all.checked = true;
    if ($("#shopSearch")) $("#shopSearch").value = ""; if ($("#shopSort")) $("#shopSort").value = "featured";
    if ($("#saleOnly")) $("#saleOnly").checked = false; if ($("#newOnly")) $("#newOnly").checked = false;
    maxPrice = 5000; if ($("#priceRange")) $("#priceRange").value = 5000; if ($("#priceMaxText")) $("#priceMaxText").textContent = money(5000); shopShowCount = 12; renderShopProducts();
  }

  function initProductPage() {
    if (!$("#productDetail")) return;
    const id = Number(new URLSearchParams(location.search).get("id") || 1); const p = productById(id) || products[0];
    document.title = `${p.name} — Resilio Store`;
    $("#productCrumb").textContent = p.name; $("#productBadge").textContent = p.badge || "RESILIO EDIT";
    $("#productMainImage").src = p.image; $("#productMainImage").alt = p.name; $("#productCategory").textContent = `${p.category} · RESILIO EDIT`;
    $("#productName").textContent = p.name; $("#productRating").textContent = p.rating; $("#productReviewLink").textContent = `${p.reviews} sample ratings`;
    $("#productPrice").textContent = money(p.price); $("#productOldPrice").textContent = money(p.oldPrice); $("#productDiscount").textContent = `${Math.round((1-p.price/p.oldPrice)*100)}% OFF`;
    $("#productDescription").textContent = p.description; $("#productWhy").textContent = `${p.name} is part of the Resilio everyday edit: considered style, a practical role and details that feel right for daily life. Confirm supplier specifications before using commercial product claims.`;
    $("#detailCategoryText").textContent = p.category; $("#productRef").textContent = `RS-${String(p.id).padStart(4,"0")}`;
    $("#selectedColourLabel").textContent = p.colorNames[0] || "Everyday neutral";
    $("#productColorOptions").innerHTML = p.colors.map((color,i) => `<button class="color-choice ${i===0 ? "active" : ""}" data-color-index="${i}" aria-label="${safeText(p.colorNames[i] || `Colour ${i+1}`)}"><span style="background:${color}"></span></button>`).join("");
    $("#productColorOptions").addEventListener("click", event => { const choice = event.target.closest("[data-color-index]"); if (!choice) return; selectedColorIndex = Number(choice.dataset.colorIndex); $$('[data-color-index]').forEach(b => b.classList.toggle("active", b === choice)); $("#selectedColourLabel").textContent = p.colorNames[selectedColorIndex] || `Colour ${selectedColorIndex+1}`; });
    detailQty = 1; $("#detailQty").textContent = detailQty;
    rememberRecentlyViewed(p.id);
    $("#detailQtyMinus").addEventListener("click", () => { detailQty = Math.max(1,detailQty-1); $("#detailQty").textContent = detailQty; });
    $("#detailQtyPlus").addEventListener("click", () => { detailQty = Math.min(99,detailQty+1); $("#detailQty").textContent = detailQty; });
    $("#detailAddToCart").addEventListener("click", () => addToCart(p.id,detailQty,selectedColorIndex));
    $("#detailWish").addEventListener("click", () => toggleWishlist(p.id)); updateProductWishButton(p.id);
    renderRelatedProducts(p.id);
  }
  function updateProductWishButton(id) { const button = $("#detailWish"); if (button) { const active = wishlist.includes(id); button.classList.toggle("active",active); button.textContent = active ? "♥" : "♡"; button.setAttribute("aria-label",active?"Remove from wishlist":"Add to wishlist"); } }
  function renderRelatedProducts(currentId) {
    const grid = $("#relatedProducts"); if (!grid) return;
    const current = productById(currentId || Number(new URLSearchParams(location.search).get("id") || 1)) || products[0];
    const related = [...products].filter(p => p.id !== current.id).sort((a,b) => Number(b.category === current.category)-Number(a.category === current.category) || b.popularity-a.popularity).slice(0,4);
    grid.innerHTML = related.map(productCard).join(""); bindProductGrid(grid);
  }

  function renderCartPage() {
    const list = $("#cartPageItems"); if (!list) return;
    const value = subtotal(); const discount = discountAmount(value); const shipping = shippingAmount(value); const total = value - discount + shipping;
    list.innerHTML = cart.map(item => {
      const p = productById(item.id); if (!p) return "";
      const variantIndex = Math.max(0, Math.min(p.colors.length - 1, Number(item.variantIndex) || 0));
      const variantLabel = p.colorNames[variantIndex] || "Default colour";
      return `<article class="cart-page-item"><div class="cart-page-product"><a href="product.html?id=${p.id}"><img src="${p.image}" alt="${safeText(p.name)}"></a><div><small>${safeText(p.category)} · ${safeText(variantLabel)}</small><strong><a href="product.html?id=${p.id}">${safeText(p.name)}</a></strong><span class="cart-page-price">${money(p.price)}</span><div class="cart-page-item-actions"><button class="remove-page-item" data-page-cart="remove" data-id="${p.id}" data-variant-index="${variantIndex}">Remove</button><button class="save-page-item" data-page-cart="save" data-id="${p.id}" data-variant-index="${variantIndex}">Save for later ♡</button></div></div></div><div class="cart-page-qty"><div class="qty-control"><button data-page-cart="minus" data-id="${p.id}" data-variant-index="${variantIndex}" aria-label="Decrease quantity">−</button><span>${item.qty}</span><button data-page-cart="plus" data-id="${p.id}" data-variant-index="${variantIndex}" aria-label="Increase quantity">+</button></div></div><div class="cart-page-line-total">${money(p.price*item.qty)}</div></article>`;
    }).join("");
    const empty = cart.length === 0; $("#cartPageEmpty")?.classList.toggle("hidden",!empty); $("#cartPageContent")?.classList.toggle("hidden",empty);
    $("#cartPageSubtotal").textContent = money(value); $("#cartPageShipping").textContent = value === 0 ? "—" : shipping ? money(shipping) : "FREE"; $("#cartPageDiscount").textContent = `−${money(discount)}`; $("#cartPageDiscountRow")?.classList.toggle("hidden",discount===0); $("#cartPageTotal").textContent = money(total); $("#cartPageQuantity").textContent = `(${countCart()} items)`;
    if ($("#cartPromoMessage")) $("#cartPromoMessage").textContent = appliedPromo ? "WELCOME10 is applied — 10% off your demo total." : "Try WELCOME10 for 10% off the demo total.";
    $("#goCheckout")?.classList.toggle("hidden",empty);
  }
  function initCartPage() {
    if (!$("#cartPageContent")) return;
    $("#cartPageItems").addEventListener("click", event => { const b = event.target.closest("[data-page-cart]"); if (!b) return; const id=Number(b.dataset.id); const variantIndex=Number(b.dataset.variantIndex || 0); if (b.dataset.pageCart === "remove") removeCartItem(id,variantIndex); if (b.dataset.pageCart === "plus") changeQty(id,1,variantIndex); if (b.dataset.pageCart === "minus") changeQty(id,-1,variantIndex); if (b.dataset.pageCart === "save") moveCartToWishlist(id,variantIndex); });
    $("#cartPromoForm").addEventListener("submit", event => { event.preventDefault(); const code = $("#cartPromoInput").value.trim().toUpperCase(); if (code === "WELCOME10") { appliedPromo = true; saveCart(); toast("WELCOME10 applied to your demo bag"); } else { appliedPromo = false; saveCart(); toast("That code isn't recognised. Try WELCOME10."); } renderCartPage(); renderDrawerCart(); });
    renderCartPage(); renderCartRecommendations();
  }
  function renderCartRecommendations() {
    const grid = $("#cartRecommendations"); if (!grid) return;
    const inCart = new Set(cart.map(i=>i.id)); const picks = products.filter(p => !inCart.has(p.id)).sort((a,b)=>b.popularity-a.popularity).slice(0,4);
    grid.innerHTML = picks.map(productCard).join(""); bindProductGrid(grid);
  }

  function renderWishlistPage() {
    const grid = $("#wishlistPageGrid"); if (!grid) return;
    const items = wishlist.map(productById).filter(Boolean);
    grid.innerHTML = items.map(productCard).join(""); bindProductGrid(grid);
    $("#wishlistPageCount").textContent = `${items.length} saved ${items.length===1?"find":"finds"}`;
    $("#wishlistEmptyPage")?.classList.toggle("hidden",items.length>0); grid.classList.toggle("hidden",items.length===0);
    $("#clearWishlist")?.classList.toggle("hidden",items.length===0);
  }

  function renderCheckoutSummary() {
    const list = $("#checkoutOrderItems"); if (!list) return;
    const value = subtotal(); const discount = discountAmount(value); const ship = shippingAmount(value);
    list.innerHTML = cart.map(item => { const p=productById(item.id); if(!p)return ""; const colour=p.colorNames[Math.max(0,Math.min(p.colors.length-1,Number(item.variantIndex)||0))] || "Default colour"; return `<div class="checkout-order-item"><img src="${p.image}" alt="${safeText(p.name)}"><div><b>${safeText(p.name)}</b><small>Qty ${item.qty} · ${safeText(p.category)} · ${safeText(colour)}</small></div><strong>${money(p.price*item.qty)}</strong></div>`; }).join("");
    if (cart.length===0) list.innerHTML = `<p class="muted-copy">Your bag is empty. <a href="shop.html" class="under-link">Find something good ↗</a></p>`;
    $("#checkoutSubtotal").textContent = money(value); $("#checkoutShipping").textContent = value===0 ? "—" : ship ? money(ship) : "FREE"; $("#checkoutDiscount").textContent = `−${money(discount)}`; $("#checkoutDiscountRow")?.classList.toggle("hidden",discount===0); $("#checkoutTotal").textContent = money(value-discount+ship);
  }
  function initWishlistPage() {
    $("#clearWishlist")?.addEventListener("click", () => { wishlist = []; saveWishlist(); renderWishlistPage(); refreshProductCards(); toast("Wishlist cleared"); });
  }

  function initCheckout() {
    const form = $("#checkoutForm");
    if (!form) return;
    renderCheckoutSummary();
    form.addEventListener("submit", event => {
      event.preventDefault();
      if (cart.length === 0) {
        let notice = $("#checkoutEmptyNotice");
        if (!notice) { notice = document.createElement("p"); notice.id = "checkoutEmptyNotice"; notice.className = "checkout-empty-notice"; notice.setAttribute("role", "alert"); form.prepend(notice); }
        notice.innerHTML = 'Your bag is empty. <a href="shop.html">Browse the shop ↗</a> before continuing.';
        notice.scrollIntoView({ behavior:"smooth", block:"center" });
        toast("Add a product before starting checkout.");
        return;
      }
      if (!form.reportValidity()) return;
      const orderRef = `RS-DEMO-${Date.now().toString().slice(-6)}`;
      const orderSnapshot = { reference:orderRef, total:totalAmount(subtotal()), itemCount:countCart(), createdAt:new Date().toISOString() };
      writeStorage("resilio-v2-last-demo-order", orderSnapshot);
      const success = $("#checkoutSuccess");
      if (success) {
        const heading = $("h2", success); const paragraph = $("p", success);
        if (heading) heading.textContent = "Your demo order is ready.";
        if (paragraph) paragraph.textContent = `Reference ${orderRef}. This is only a frontend demonstration: no order was transmitted and no payment was taken.`;
        success.classList.remove("hidden");
        success.scrollIntoView({behavior:"smooth",block:"center"});
      }
      cart = []; appliedPromo = false; saveCart(); updateHeaderCounts(); renderDrawerCart(); renderCartPage();
      toast(`Demo checkout complete · ${orderRef}`);
    });
  }

  function initContact() {
    const form = $("#contactForm"); if (!form) return;
    form.addEventListener("submit", event => { event.preventDefault(); if (!form.reportValidity()) return; $("#contactSuccess")?.classList.remove("hidden"); $("#contactSuccess")?.scrollIntoView({behavior:"smooth",block:"center"}); toast("Demo message validated in your browser"); form.reset(); });
  }
  function initNewsletters() {
    $$('[data-newsletter]').forEach(form => form.addEventListener("submit", event => { event.preventDefault(); if (!form.reportValidity()) return; const input = $('input[type="email"]',form); toast("Thanks for your interest! Signup is a demo."); form.reset(); }));
  }
  function initHero() {
    const imageElement = $("#homeHeroImage"); if (!imageElement) return;
    const setSlide = index => {
      heroIndex = (index + slides.length) % slides.length; const slide=slides[heroIndex]; imageElement.style.opacity="0";
      setTimeout(()=>{ imageElement.src=image(slide.image,1200); imageElement.alt=slide.alt; $("#heroPickName").textContent=slide.name; $("#heroPickPrice").innerHTML=`${slide.price} <span>↗</span>`; $("#heroSlideCounter").innerHTML=`${String(heroIndex+1).padStart(2,"0")} <i>/</i> 03`; $$('[data-hero-slide]').forEach(b=>b.classList.toggle("active",Number(b.dataset.heroSlide)===heroIndex)); imageElement.style.opacity="1"; },170);
    };
    $$('[data-hero-slide]').forEach(button=>button.addEventListener("click",()=>{setSlide(Number(button.dataset.heroSlide));clearInterval(heroInterval);heroInterval=setInterval(()=>setSlide(heroIndex+1),6500);}));
    $("#heroPickName")?.closest("a")?.addEventListener("click", event => { const slide=slides[heroIndex]; event.currentTarget.href=`product.html?id=${slide.id}`; });
    heroInterval=setInterval(()=>setSlide(heroIndex+1),6500);
    document.addEventListener("visibilitychange",()=>{clearInterval(heroInterval);if(!document.hidden)heroInterval=setInterval(()=>setSlide(heroIndex+1),6500);});
  }
  function initNumbers() {
    const nodes = $$('[data-count]'); if (!nodes.length) return;
    const runCount = node => { const target=Number(node.dataset.count); const decimal=node.dataset.decimal === "true"; const duration=1000; const start=performance.now(); const update=now=>{const progress=Math.min(1,(now-start)/duration);const eased=1-Math.pow(1-progress,3);const value=target*eased;node.textContent=decimal?value.toFixed(1):Math.round(value).toLocaleString("en-IN")+(target===12000?"+":"");if(progress<1)requestAnimationFrame(update);};requestAnimationFrame(update); };
    if ("IntersectionObserver" in window) { const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting&&!entry.target.dataset.counted){entry.target.dataset.counted="true";runCount(entry.target);observer.unobserve(entry.target);}}),{threshold:.3});nodes.forEach(node=>observer.observe(node)); } else nodes.forEach(runCount);
  }

  function renderSearchSuggestions(rawQuery) {
    const panel = $("#searchSuggestions"); const input = $("#globalSearchInput");
    if (!panel || !input) return;
    const query = String(rawQuery || "").trim().toLowerCase();
    if (!query) { panel.innerHTML = ""; panel.classList.add("hidden"); input.setAttribute("aria-expanded", "false"); return; }
    const matches = products.filter(product => `${product.name} ${product.category} ${product.description} ${product.badge}`.toLowerCase().includes(query)).slice(0, 5);
    panel.innerHTML = `${matches.map(product => `<button type="button" class="search-suggestion" data-search-product="${product.id}"><img src="${product.image}" alt=""><span><strong>${safeText(product.name)}</strong><small>${safeText(product.category)} · ${money(product.price)}</small></span><span class="suggestion-arrow">↗</span></button>`).join("")}${matches.length ? "" : `<p class="search-no-results">No quick matches. Try another keyword.</p>`}<button type="button" class="search-see-all" data-search-all>See all results for “${safeText(rawQuery.trim())}” ↗</button>`;
    panel.classList.remove("hidden"); input.setAttribute("aria-expanded", "true");
  }

  function rememberRecentlyViewed(id) {
    const old = readStorage("resilio-v2-recently-viewed", []);
    const clean = Array.isArray(old) ? old.map(Number).filter(value => productById(value) && value !== Number(id)) : [];
    writeStorage("resilio-v2-recently-viewed", [Number(id), ...clean].slice(0, 8));
    renderRecentlyViewed(Number(id));
  }

  function renderRecentlyViewed(currentId) {
    const ids = readStorage("resilio-v2-recently-viewed", []);
    const viewed = (Array.isArray(ids) ? ids : []).map(Number).filter(id => id !== Number(currentId)).map(productById).filter(Boolean).slice(0, 4);
    let section = $("#recentlyViewedSection");
    if (!viewed.length) { section?.remove(); return; }
    if (!section) {
      section = document.createElement("section");
      section.id = "recentlyViewedSection"; section.className = "section-pad recently-viewed-section";
      const footer = $("#site-footer");
      const reviews = $("#productReviews");
      const headingText = `<div class="section-head"><div><span class="eyebrow">PICK UP WHERE YOU LEFT OFF</span><h2>Recently <em>viewed.</em></h2></div><a href="shop.html" class="under-link">Explore more ↗</a></div><div id="recentlyViewedGrid" class="product-grid"></div>`;
      section.innerHTML = headingText;
      if (reviews) reviews.insertAdjacentElement("afterend", section); else if (footer) footer.insertAdjacentElement("beforebegin", section); else document.body.appendChild(section);
    }
    const grid = $("#recentlyViewedGrid");
    if (grid) { grid.innerHTML = viewed.map(productCard).join(""); bindProductGrid(grid); }
  }

  // Keep the cart and wishlist aligned if the shopper has multiple store tabs open.
  window.addEventListener("storage", event => {
    if (!["resilio-v2-cart", "resilio-v2-wishlist", "resilio-v2-promo"].includes(event.key)) return;
    cart = readStorage("resilio-v2-cart", []);
    wishlist = readStorage("resilio-v2-wishlist", []);
    appliedPromo = readStorage("resilio-v2-promo", false) === true;
    cart = (Array.isArray(cart) ? cart : []).filter(item => productById(item?.id)).map(item => { const p=productById(item.id); return { id:Number(item.id), qty:Math.max(1,Math.min(99,Math.floor(Number(item.qty)||1))), variantIndex:Math.max(0,Math.min(p.colors.length-1,Math.floor(Number(item.variantIndex)||0))) }; });
    wishlist = [...new Set((Array.isArray(wishlist) ? wishlist : []).map(Number).filter(id => Boolean(productById(id))))];
    updateHeaderCounts(); renderDrawerCart(); renderCartPage(); renderCheckoutSummary(); renderWishlistPage(); refreshProductCards();
  });

  function init() {
    mountChrome();
    renderHomeProducts(); initHero(); initNumbers(); initNewsletters(); initShop(); initProductPage(); initCartPage(); initWishlistPage(); renderWishlistPage(); initCheckout(); initContact();
    renderDrawerCart(); renderCartPage(); renderCheckoutSummary();
    saveCart(); saveWishlist();
  }
  document.addEventListener("DOMContentLoaded", init);
})();