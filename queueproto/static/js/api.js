import { notificationController } from "./notifications.js";
import { API_URL } from "./settings.js";

export async function generateOrders() {
  const toGenerateValue = document.getElementById("to-generate").value;

  const url = `${API_URL}/core/orders?generate=${toGenerateValue}`;
  try {
    const response = await fetch(url, { method: "POST" });
    const errorsResponse = await response.json();
    if (errorsResponse && errorsResponse.errors.length > 0) {
      const errors = errorsResponse.errors;
      errors.forEach((err) =>
        notificationController.addNotification(err.message),
      );
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

export async function handleOrders() {
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
        notificationController.addNotification(
          "Something went wrong: " + detail.msg,
        );
      });
    } else {
      notificationController.addNotification(
        "Orders were added to the handle queue",
      );
    }
  } catch (error) {
    notificationController.addNotification(
      "Error occurred while handling orders",
    );
    console.error(error);
  }
}

export async function getOrderFulfillmentHistory(orderId) {
  const url = `${API_URL}/core/orders/${orderId}/fulfillment/history`;
  try {
    const response = await fetch(url);
    const jsonResponse = await response.json();
    if (!response.ok) {
      jsonResponse.detail.forEach((detail) => {
        notificationController.addNotification(
          "Something went wrong: " + detail.msg,
        );
      });
      return [];
    } else {
      return jsonResponse;
    }
  } catch (error) {
    notificationController.addNotification(
      "Error occurred while gettings orders fulfillment history",
    );
    console.error(error);
  }
}
