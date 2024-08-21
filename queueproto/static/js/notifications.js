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

export const notificationController = new NotificationController();
