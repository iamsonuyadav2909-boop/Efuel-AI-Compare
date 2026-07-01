const KEY = 'efuel_compare_basket';

export function getBasket() {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function save(items) {
  localStorage.setItem(KEY, JSON.stringify(items));
  window.dispatchEvent(new Event('efuel-basket-updated'));
}

export function isInBasket(product) {
  return getBasket().some((p) => p.name === product.name && p.brand === product.brand);
}

export function addToBasket(product, category) {
  const items = getBasket();
  if (isInBasket(product)) return items;
  if (items.length >= 4) return items;
  const next = [...items, { ...product, category: category || product.category || '' }];
  save(next);
  return next;
}

export function removeFromBasket(name, brand) {
  const next = getBasket().filter((p) => !(p.name === name && p.brand === brand));
  save(next);
  return next;
}

export function clearBasket() {
  save([]);
  return [];
}
