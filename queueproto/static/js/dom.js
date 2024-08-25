import { toTitleCase, parseDateToDjangoFormat, truncateFloatToTwoDecimalPlaces } from "./utils.js";
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
    const statusPill = document.createElement("div");
    statusPill.className = "p-2 border border-gray-300 rounded shadow";
    statusPill.innerHTML = `
     <h3 class="pb-1 font-semibold text-sm">${toTitleCase(data["state"])}</h3>
     <p class="text-xs">Task Status: ${toTitleCase(data["status"])}</p>
     <p class="text-xs">Message: ${data["message"] && data["message"] != "" ? data["message"] : "-"}</p>
     <p class="text-xs">Task Started At: ${new Date(data["started_at"]).toUTCString()}</p>
     <p class="text-xs">Task Finished At: ${new Date(data["finished_at"]).toUTCString()}</p>
     `;
    handlingStatusPillContainer.appendChild(statusPill);
  });
}

export async function updateOrdersTable(orderData) {
  const ordersTableBody = document.querySelector("#orders-table tbody");

  const tr = document.createElement("tr");
  tr.className =
    "odd:bg-white even:bg-gray-50 border-b opacity-0 -translate-y-2 transition-all duration-700 ease-in";

  const [outerDivClass, innerDivClass, spanClass, paragraphClass] = getFulfillmentStatusStylingBasedOnStatus(
    orderData["state"]
  );

  const latestHandlingProcessState =
    orderData["latest_handling_process"] != null
      ? toTitleCase(orderData["latest_handling_process"]["state"])
      : "-";

  const latestHandlingProcessStatus =
    orderData["latest_handling_process"] != null
      ? orderData["latest_handling_process"]["status"]
      : null;
  const handlingProcessStatusIcon = getLatestHandlingProcessStatusIcon(latestHandlingProcessStatus);

  const latestHandlingProcessCell = document.createElement("td")
  latestHandlingProcessCell.className = "px-2 py-4 text-center";
  latestHandlingProcessCell.setAttribute("data-order-id", orderData["id"]);
  setClickEventToDisplayHandlingStatusModal(latestHandlingProcessCell);

  latestHandlingProcessCell.innerHTML = `
    <div id="handling-status-${orderData["id"]}" class="pb-1 flex flex-row items-center justify-center gap-[2px]">
        ${handlingProcessStatusIcon}
        <p class="text-xs text-gray-600">${latestHandlingProcessState}</p>
    </div>
    <p id="processing-status-${orderData["id"]}" class="text-xs text-gray-400"></p>
  `

  tr.innerHTML = `
    <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">
        <input type="checkbox" name="order" value="${orderData["id"]}"/>
    </th>
    <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">
        ${orderData["id"]}
    </th>
    <td class="px-6 py-4">
        ${parseDateToDjangoFormat(orderData["placed_at"])}
    </td>
    <td class="px-6 py-4">
        ${orderData["customer"]["first_name"]} ${orderData["customer"]["last_name"]}
    </td>
    <td class="px-6 py-4">
        ${orderData["customer"]["country"]}
    </td>
    <td class="px-6 py-4 text-center">
        $${truncateFloatToTwoDecimalPlaces(orderData["total_price"])}
    </td>
    <td class="px-6 py-4 text-center" id="fulfillment-status-${orderData["id"]}">
        <div class="${outerDivClass}">
          <div class="${innerDivClass}">
            <span class="${spanClass}"></span>
            <p class="${paragraphClass}">${toTitleCase(orderData["state"])}</p>
          </div>
        </div>
    </td>
    ${latestHandlingProcessCell.outerHTML}
    <td class="px-6 py-4 text-center">
        ${orderData["total_quantity"] > 1 ? orderData["total_quantity"] + " items" : orderData["total_quantity"] + " item"}
    </td>
    <td class="px-6 py-4 text-center">
        <a href="#" class="font-medium text-blue-600 hover:underline">Edit</a>
    </td>
  `

  ordersTableBody.prepend(tr);

  requestAnimationFrame(() => {
    tr.classList.remove("opacity-0", "-translate-y-2");
  });

  // Let the animation finish playing
  await new Promise((resolve) => setTimeout(resolve, 500));
}

export function updateOrdersProcessingStatus(orderProcessingStatusData) {
  const processingStatusParagraph = document.getElementById(
    "processing-status-" + orderProcessingStatusData["order_id"],
  );
  if (!processingStatusParagraph) {
    console.error("Processing status pragraph was not found");
    return;
  }

  processingStatusParagraph.innerHTML = toTitleCase(
    orderProcessingStatusData["status"],
  );
}

export function updateOrdersHandlingStatus(orderHandlingStatusData) {
  const handlingStatusDiv = document.getElementById(
    "handling-status-" + orderHandlingStatusData["order_id"],
  );
  if (!handlingStatusDiv) {
    console.error("Handling status paragraph was not found");
    return;
  }

  let statusIcon = "<img src='static/icons/approve-tick.svg' alt='Success' />";
  if (orderHandlingStatusData["status"] == "FAILED") {
    statusIcon = "<img src='static/icons/reject-x.svg' alt='Failure' />";
  }
    
  handlingStatusDiv.innerHTML = `
    ${statusIcon}
    <p class="text-xs text-gray-600">${toTitleCase(orderHandlingStatusData["state"])}</p>
    `;
}

export function updateOrdersFulfillmentStatus(orderFulfillmentStatusData) {
  const fulfillmentStatusTableCell = document.getElementById(
    "fulfillment-status-" + orderFulfillmentStatusData["order_id"],
  );
  if (!fulfillmentStatusTableCell) {
    console.error("Fulfillment status table cell was not found");
    return;
  }

  const fulfillmentStatus = orderFulfillmentStatusData["status"]
  const [outerDivClass, innerDivClass, spanClass, paragraphClass] = getFulfillmentStatusStylingBasedOnStatus(
    fulfillmentStatus
  );

  fulfillmentStatusTableCell.innerHTML = `
    <div class="${outerDivClass}">
      <div class="${innerDivClass}">
        <span class="${spanClass}"></span>
        <p class="${paragraphClass}">${toTitleCase(fulfillmentStatus)}</p>
      </div>
    </div>
    `;
}

function getFulfillmentStatusStylingBasedOnStatus(status) {
  let outerDivClass = "text-xs flex items-center justify-center";
  let innerDivClass =
    "w-[85px] flex flex-row items-center justify-center gap-2 p-1 border rounded-lg";
  let spanClass = "w-[8px] h-[8px] rounded-full";
  const paragraphClass = "font-semibold";

  switch (status) {
    case "CANCELED":
      outerDivClass += " text-gray-500";
      innerDivClass += " bg-gray-200 border-gray-300";
      spanClass += " border-2 border-gray-600";
      break;
    case "SHIPPED":
      outerDivClass += " text-green-600";
      innerDivClass += " bg-green-200 border-green-300";
      spanClass += " bg-green-600";
      break;
    case "SHIPPING":
      outerDivClass += " text-yellow-600";
      innerDivClass += " bg-yellow-200 border-yellow-300";
      spanClass += " border-2 border-yellow-600";
      break;
  }

  return [outerDivClass, innerDivClass, spanClass, paragraphClass]
}

function getLatestHandlingProcessStatusIcon(status) {
  let handlingProcessStatusIcon = "";

  if (status == "SUCCEEDED") {
    handlingProcessStatusIcon = "<img src='static/icons/approve-tick.svg' alt='Success' />";
  } else if (status == "FAILED") { 
    handlingProcessStatusIcon = "<img src='static/icons/reject-x.svg' alt='Failure' />";
  }

  return handlingProcessStatusIcon;
}
