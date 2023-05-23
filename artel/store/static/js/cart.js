$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!this.crossDomain) {
            xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
        }
    }
});

$(document).on('click', '.add-to-cart-button', function(event) {
    event.preventDefault();
    const button = $(this);
    const formData = new FormData();
    const productID = $(this).data('product-id');
    //const quantity = $(this).data('quantity');
    const quantity = $('#quantity'+productID).val(); 
    console.log(quantity)
    const addToCartURL = $(this).data('add-to-cart-url');
    const csrfToken = $(this).data('csrf-token');
    formData.append('product_id', productID);
    formData.append('quantity', quantity); // Serialize the form data correctly
    button.prop('disabled', true); 
    $.ajax({
        type: 'POST',
        url: addToCartURL,
        data: formData, // Use the serialized form data
        headers: { 'X-CSRFToken': csrfToken },
        dataType: 'json',
        processData: false, // Prevent jQuery from processing the data
        contentType: false, // Let the browser set the content type
        success: function(data) {
            alert(data.message);
            button.prop('disabled', false);
        },
        error: function() {
          button.prop('disabled', false);
        }
      });
    });

    const cartButton = document.getElementById('cart-button');
    const cartDropdown = document.getElementById('cart-dropdown');

    cartButton.addEventListener('click', function(event) {
        event.preventDefault();
        if (cartDropdown.style.display === 'none') {
          cartDropdown.style.display = 'block';
          fetchCartItems(); // Fetch and populate cart items
        } else {
          cartDropdown.style.display = 'none';
        }
      });
      
      function fetchCartItems() {
        fetch('/cart/')
          .then(response => response.json())
          .then(data => {
            const cartItems = data.cart_items;
            const cartItemsList = document.getElementById('cart-items');
            cartItemsList.innerHTML = ''; // Clear existing cart items
            cartItems.forEach(item => {
              const li = document.createElement('li');
              li.textContent = `Product ID: ${item.product_id}, Quantity: ${item.quantity}`;
              cartItemsList.appendChild(li);
            });
          });
      }
