import { API_URL } from "./settings.js";
import {
  parseDateToDjangoFormat,
  truncateFloatToTwoDecimalPlaces,
} from "./utils.js";

const order_event_source = new EventSource(`${API_URL}/core/orders/stream`);
const order_processing_status_event_source = new EventSource(
  `${API_URL}/core/orders/processing/status/stream`,
);
const order_handling_status_event_source = new EventSource(
  `${API_URL}/core/orders/handling/status/stream`,
);

order_event_source.onopen = () => {
  console.log("Connecting to the SSE.");
};

order_event_source.addEventListener("newOrders", async function (event) {
  try {
    await updateOrdersTable(JSON.parse(event.data));
  } catch (error) {
    console.error("Could not get event data:", error);
  }
});

order_processing_status_event_source.onopen = () => {
  console.log("Connecting to the monitoring orders processing status SSE.");
};

order_processing_status_event_source.addEventListener(
  "updatedOrderProcessingStatus",
  function (event) {
    try {
      updateOrdersProcessingStatus(JSON.parse(event.data));
    } catch (error) {
      console.error(error);
    }
  },
);

order_handling_status_event_source.onopen = () => {
  console.log("Connecting to the monitoring orders handling status SSE.");
};

order_handling_status_event_source.addEventListener(
  "updatedOrderHandlingStatus",
  function (event) {
    try {
      console.log(JSON.parse(event.data));
    } catch (error) {
      console.error(error);
    }
  },
);

async function updateOrdersTable(orderData) {
  const ordersTableBody = document.querySelector("#orders-table tbody");

  const tr = document.createElement("tr");
  tr.className =
    "odd:bg-white even:bg-gray-50 border-b opacity-0 -translate-y-2 transition-all duration-700 ease-in";

  const thCol1 = document.createElement("th");
  thCol1.scope = "row";
  thCol1.className = "px-6 py-4 font-medium text-gray-900 whitespace-nowrap";

  const orderCheckbox = document.createElement("input");
  orderCheckbox.type = "checkbox";
  orderCheckbox.name = "order";
  orderCheckbox.value = orderData["id"];

  thCol1.appendChild(orderCheckbox);
  tr.appendChild(thCol1);

  const thCol2 = document.createElement("th");
  thCol2.scope = "row";
  thCol2.className = "px-6 py-4 font-medium text-gray-900 whitespace-nowrap";
  thCol2.innerHTML = orderData["id"];
  tr.appendChild(thCol2);

  const tdCol3 = document.createElement("td");
  tdCol3.className = "px-6 py-4";
  tdCol3.innerHTML = parseDateToDjangoFormat(orderData["placed_at"]);
  tr.appendChild(tdCol3);

  const tdCol4 = document.createElement("td");
  tdCol4.className = "px-6 py-4";
  tdCol4.innerHTML = `${orderData["customer"]["first_name"]} ${orderData["customer"]["last_name"]}`;
  tr.appendChild(tdCol4);

  const tdCol5 = document.createElement("td");
  tdCol5.className = "px-6 py-4";
  tdCol5.innerHTML = orderData["customer"]["country"];
  tr.appendChild(tdCol5);

  const tdCol6 = document.createElement("td");
  tdCol6.className = "px-6 py-4 text-center";
  tdCol6.innerHTML =
    "$" + truncateFloatToTwoDecimalPlaces(orderData["total_price"], 2);
  tr.appendChild(tdCol6);

  const tdCol7 = document.createElement("td");
  tdCol7.className = "px-6 py-4 text-center";

  const stateDiv = document.createElement("div");
  stateDiv.className =
    "text-xs text-yellow-600 flex items-center justify-center";

  const stateInnerDiv = document.createElement("div");
  stateInnerDiv.className =
    "w-[85px] flex flex-row items-center justify-center gap-2 p-1 bg-yellow-200 border border-yellow-300 rounded-lg";

  const stateInnerDivSpan = document.createElement("span");
  stateInnerDivSpan.className =
    "w-[8px] h-[8px] border-2 border-yellow-600 rounded-full";

  const stateInnerDivP = document.createElement("p");
  stateInnerDivP.className = "font-semibold";
  stateInnerDivP.innerHTML = orderData["state"];

  stateInnerDiv.appendChild(stateInnerDivSpan);
  stateInnerDiv.appendChild(stateInnerDivP);
  stateDiv.append(stateInnerDiv);
  tdCol7.appendChild(stateDiv);
  tr.appendChild(tdCol7);

  const tdCol8 = document.createElement("td");
  tdCol8.className = "px-6 py-4 text-center";
  const latestHandlingProcessState =
    orderData["latest_handling_process"] != null
      ? orderData["latest_handling_process"]["state"]
      : "-";
  tdCol8.innerHTML = `<p>${latestHandlingProcessState}</p><p id="processing-status-${orderData["id"]}" class="text-xs text-gray-500"></p>`;

  tr.appendChild(tdCol8);

  const tdCol9 = document.createElement("td");
  tdCol9.className = "px-6 py-4 text-center";

  const totalQuantity = orderData["total_quantity"];
  let totalQuantityDescription = "item";
  if (totalQuantity > 1) {
    totalQuantityDescription = "items";
  }
  tdCol9.innerHTML = `${totalQuantity} ${totalQuantityDescription}`;
  tr.appendChild(tdCol9);

  const tdCol10 = document.createElement("td");
  tdCol10.className = "px-6 py-4 text-center";

  const actionLink = document.createElement("a");
  actionLink.className = "font-medium text-blue-600 hover:underline";
  actionLink.innerHTML = "Edit";
  actionLink.href = "#";

  tdCol10.appendChild(actionLink);
  tr.appendChild(tdCol10);

  ordersTableBody.prepend(tr);

  requestAnimationFrame(() => {
    tr.classList.remove("opacity-0", "-translate-y-2");
  });

  // Let the animation finish playing
  await new Promise((resolve) => setTimeout(resolve, 500));
}

function updateOrdersProcessingStatus(orderProcessingStatusData) {
  const processingStatusParagraph = document.getElementById(
    "processing-status-" + orderProcessingStatusData["order_id"],
  );
  if (!processingStatusParagraph) {
    console.error("Processing status pragraph was not found");
    return;
  }

  processingStatusParagraph.innerHTML = orderProcessingStatusData["status"];
}
