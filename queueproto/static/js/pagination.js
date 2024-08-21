import { BASE_URL } from "./settings.js";

export function gotoPreviousPage() {
  const currentPage = +document.getElementById("pagination-current-page")
    .innerHTML;
  const allPages = +document.getElementById("pagination-total-pages-count")
    .innerHTML;

  if (currentPage - 1 >= 1) {
    document.location.href = `${BASE_URL}?page=${currentPage - 1}`;
  }
}

export function gotoNextPage() {
  const currentPage = +document.getElementById("pagination-current-page")
    .innerHTML;
  const allPages = +document.getElementById("pagination-total-pages-count")
    .innerHTML;

  if (currentPage + 1 <= allPages) {
    document.location.href = `${BASE_URL}?page=${currentPage + 1}`;
  }
}
