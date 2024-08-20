const API_URL = "http://localhost:8000/api/v1";

// TODO: could use that later to color notifications based on their type
const NotificationType = {
  Info: 0,
  Warning: 1,
  Error: 2,
  Success: 3,
};

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
