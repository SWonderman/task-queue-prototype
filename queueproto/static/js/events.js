import { API_URL } from "./settings.js";
import { 
    updateOrdersTable, 
    updateOrdersProcessingStatus, 
    updateOrdersHandlingStatus, 
    updateOrdersFulfillmentStatus 
} from "./dom.js";

const order_event_source = new EventSource(`${API_URL}/core/orders/stream`);

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

order_event_source.addEventListener(
  "updatedOrderProcessingStatus",
  function (event) {
    try {
      updateOrdersProcessingStatus(JSON.parse(event.data));
    } catch (error) {
      console.error(error);
    }
  },
);

order_event_source.addEventListener(
  "updatedOrderHandlingStatus",
  function (event) {
    try {
      updateOrdersHandlingStatus(JSON.parse(event.data));
    } catch (error) {
      console.error(error);
    }
  },
);

order_event_source.addEventListener(
  "updatedOrderFulfillmentStatus",
  function (event) {
    try {
      updateOrdersFulfillmentStatus(JSON.parse(event.data));
    } catch (error) {
      console.error(error);
    }
  },
);
