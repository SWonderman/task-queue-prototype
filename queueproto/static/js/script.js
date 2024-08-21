import { generateOrders, handleOrders } from "./api.js";
import { gotoNextPage, gotoPreviousPage } from "./pagination.js";
import { toggleAllOrders } from "./utils.js";

document.addEventListener("DOMContentLoaded", () => {
  const rootCheckbox = document.getElementById("root-checkbox");
  if (rootCheckbox) {
    rootCheckbox.addEventListener("click", toggleAllOrders);
  }

  const generateOrdersBtn = document.getElementById("generate-orders-btn");
  if (generateOrdersBtn) {
    generateOrdersBtn.addEventListener("click", generateOrders);
  }

  const handleOrdersBtn = document.getElementById("handle-orders-btn");
  if (handleOrdersBtn) {
    handleOrdersBtn.addEventListener("click", handleOrders);
  }

  const paginationPreviousBtn = document.getElementById(
    "pagination-previous-btn",
  );
  if (paginationPreviousBtn) {
    paginationPreviousBtn.addEventListener("click", gotoPreviousPage);
  }

  const paginationNextBtn = document.getElementById("pagination-next-btn");
  if (paginationNextBtn) {
    paginationNextBtn.addEventListener("click", gotoNextPage);
  }
});
