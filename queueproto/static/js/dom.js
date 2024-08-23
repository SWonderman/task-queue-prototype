import { toTitleCase } from "./utils.js";
import { getOrderFulfillmentHistory } from "./api.js";

export function setClickEventToDisplayHandlingStatusModal(element) {
  element.addEventListener("click", async () => {
    openHandligHistoryModal();
    const orderId = element.getAttribute("data-order-id");
    const orderFulfillmentHistory = await getOrderFulfillmentHistory(orderId);
    fillInHandlingStatusHistoryModal(orderFulfillmentHistory);
  });
}

export function openHandligHistoryModal() {
  const handlingStatusHistoryModal = document.getElementById(
    "handling-status-history-modal",
  );
  if (!handlingStatusHistoryModal) {
    console.error("Handling status history modal element was not found");
    return;
  }

  handlingStatusHistoryModal.classList.remove("hidden");
}

export function closeHandlingHistoryModal() {
  const handlingStatusHistoryModal = document.getElementById(
    "handling-status-history-modal",
  );
  if (!handlingStatusHistoryModal) {
    console.error("Handling status history modal element was not found");
    return;
  }
  handlingStatusHistoryModal.classList.add("hidden");

  // Clear all data from the pill container
  const handlingStatusPillContainer = document.getElementById(
    "handling-status-pill-container",
  );
  if (!handlingStatusPillContainer) {
    console.error("Handling status pill container element was not found");
    return;
  }
  handlingStatusPillContainer.innerHTML = "";
}

export function fillInHandlingStatusHistoryModal(orderFulfillmentHistoryData) {
  const handlingStatusPillContainer = document.getElementById(
    "handling-status-pill-container",
  );
  if (!handlingStatusPillContainer) {
    console.error("It was not possible to find handling status pill container");
    return;
  }

  orderFulfillmentHistoryData.forEach((data) => {
    let statusPill = document.createElement("div");
    statusPill.className = "p-2 border border-gray-300 rounded shadow";
    statusPill.innerHTML = `
     <h3 class="pb-1 font-semibold text-sm">${toTitleCase(data["state"])}</h3>
     <p class="text-xs">Task Status: ${toTitleCase(data["status"])}</p>
     <p class="text-xs">Task Started At: ${new Date(data["started_at"]).toUTCString()}</p>
     <p class="text-xs">Task Finished At: ${new Date(data["finished_at"]).toUTCString()}</p>
     `;
    handlingStatusPillContainer.appendChild(statusPill);
  });
}
