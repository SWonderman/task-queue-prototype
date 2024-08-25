export function toggleAllOrders() {
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

export function parseDateToDjangoFormat(originalDateString) {
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

export function truncateFloatToTwoDecimalPlaces(number) {
  number = number.toString();

  const dotIndex = number.indexOf(".");
  if (dotIndex === -1) {
    number += ".00";
    return number;
  }

  const decimals = number.slice(dotIndex + 1);
  if (decimals.length === 0) {
    number += "00";
  } else if (decimals.length === 1) {
    number += "0";
  }

  number = number.slice(0, dotIndex + 3);

  return number;
}

export function toTitleCase(content) {
  return content
    .split(" ")
    .map((word) => word[0].toUpperCase() + word.substring(1).toLowerCase())
    .join(" ");
}
