const BASE_URL = "http://localhost:8000";
const API_URL = `${BASE_URL}/api/v1`;

const order_event_source = new EventSource(`${API_URL}/core/orders/stream`);

order_event_source.onopen = () => {
  console.log("Connected to the SSE.");
};

order_event_source.addEventListener("newOrders", async function (event) {
  try {
    await updateOrdersTable(JSON.parse(event.data));
  } catch (error) {
    console.error("Could not get event data:", error);
  }
});

function parseDateToDjangoFormat(originalDateString) {
  const date = new Date(originalDateString);

  const formatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "numeric",
    hour12: true,
  };
  const formatter = new Intl.DateTimeFormat("en-US", formatOptions);

  let formattedDate = formatter.format(date);
  formattedDate = formattedDate.replace("AM", "a.m.");
  formattedDate = formattedDate.replace("PM", "p.m.");
  formattedDate = formattedDate.replace(
    formattedDate.month,
    `${formattedDate.month}.`,
  );

  return formattedDate;
}

function truncateFloatToTwoDecimalPlaces(number) {
  number = number.toString();

  let dotIndex = number.indexOf(".");
  if (dotIndex === -1) {
    number += ".00";
    return number;
  }

  let decimals = number.slice(dotIndex + 1);
  if (decimals.length === 0) {
    number += "00";
  } else if (decimals.length === 1) {
    number += "0";
  }

  number = number.slice(0, dotIndex + 3);

  return number;
}

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

  const totalQuantity = orderData["total_quantity"];
  let totalQuantityDescription = "item";
  if (totalQuantity > 1) {
    totalQuantityDescription = "items";
  }
  tdCol8.innerHTML = `${totalQuantity} ${totalQuantityDescription}`;
  tr.appendChild(tdCol8);

  const tdCol9 = document.createElement("td");
  tdCol9.className = "px-6 py-4 text-center";

  const actionLink = document.createElement("a");
  actionLink.className = "font-medium text-blue-600 hover:underline";
  actionLink.innerHTML = "Edit";
  actionLink.href = "#";

  tdCol9.appendChild(actionLink);
  tr.appendChild(tdCol9);

  ordersTableBody.prepend(tr);

  requestAnimationFrame(() => {
    tr.classList.remove("opacity-0", "-translate-y-2");
  });

  // Let the animation finish playing
  await new Promise((resolve) => setTimeout(resolve, 500));
}

class NotificationController {
  notificationBox;

  constructor() {
    this.notificationBox = document.getElementById("notifications-box");
  }

  createNotification(message) {
    const notification = document.createElement("li");
    notification.className =
      "w-[250px] p-4 z-50 bg-white border border-gray-200 text-sm shadow rounded";

    const notificationContent = document.createElement("div");
    notificationContent.className =
      "text-xs flex flex-row items-center justify-between";

    const notificationMessage = document.createElement("p");
    notificationMessage.innerHTML = message;

    const closeButton = document.createElement("button");
    closeButton.innerHTML = "X";
    closeButton.className =
      "px-2 py-1 bg-gray-200 rounded-full hover:bg-gray-100";
    closeButton.setAttribute("onclick", "this.parentNode.parentNode.remove()");

    notificationContent.appendChild(notificationMessage);
    notificationContent.appendChild(closeButton);

    notification.appendChild(notificationContent);

    return notification;
  }

  addNotification(message) {
    const notification = this.createNotification(message);
    this.notificationBox.append(notification);
    setTimeout(() => notification.remove(), 5000);
  }
}
const notificationController = new NotificationController();

function toggleAllOrders() {
  const rootCheckbox = document.getElementById("root-checkbox");
  const orderCheckboxes = document.getElementsByName("order");

  if (rootCheckbox.checked === true) {
    Array.from(orderCheckboxes).map((checkbox) => {
      checkbox.checked = true;
    });
  } else {
    Array.from(orderCheckboxes).map((checkbox) => {
      checkbox.checked = false;
    });
  }
}

function gotoPreviousPage() {
  const currentPage = +document.getElementById("pagination-current-page")
    .innerHTML;
  const allPages = +document.getElementById("pagination-total-pages-count")
    .innerHTML;

  if (currentPage - 1 >= 1) {
    document.location.href = `${BASE_URL}?page=${currentPage - 1}`;
  }
}

function gotoNextPage() {
  const currentPage = +document.getElementById("pagination-current-page")
    .innerHTML;
  const allPages = +document.getElementById("pagination-total-pages-count")
    .innerHTML;

  console.log("Going to the next page with number:", currentPage + 1);

  if (currentPage + 1 <= allPages) {
    document.location.href = `${BASE_URL}?page=${currentPage + 1}`;
  }
}

async function generateOrders() {
  const toGenerateValue = document.getElementById("to-generate").value;

  const url = `${API_URL}/core/orders?generate=${toGenerateValue}`;
  try {
    const response = await fetch(url, { method: "POST" });
    errors = await response.json();
    if (errors.length > 0) {
      const errors = response.errors;
      errors.forEach((err) => notificationController.addNotification(err));
    } else {
      notificationController.addNotification("Orders generated successfully");
    }
  } catch (error) {
    notificationController.addNotification(
      "Error occurred while generating orders",
    );
    console.error(`Error while generating orders: ${error}`);
  }
}

async function handleOrders() {
  const selectedOrders = Array.from(
    document.querySelectorAll("input[name=order]:checked"),
  );
  if (selectedOrders.length == 0) {
    notificationController.addNotification("No orders were selected");
    return;
  }

  const orderIds = selectedOrders.map((order) => order.value.toString());
  const url = `${API_URL}/core/orders/handle`;
  const body = JSON.stringify({ order_ids: orderIds });

  try {
    const response = await fetch(url, {
      method: "POST",
      body: body,
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) {
      const jsonResponse = await response.json();
      jsonResponse.detail.forEach((detail) => {
        console.log(detail);
        notificationController.addNotification(
          "Something went wrong: " + detail.msg,
        );
      });
    }
  } catch (error) {
    notificationController.addNotification(
      "Error occurred while handling orders",
    );
    console.error(error);
  }
}
