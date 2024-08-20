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
