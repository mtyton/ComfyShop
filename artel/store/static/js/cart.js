
$(document).on('click', '.add-to-cart-button', function(event) {
    
    event.preventDefault();
    const button = $(this);
    const formData = new FormData();
    const productID = parseInt($(this).data('product-id'));
    const quantity = parseInt($('#quantity'+productID).val()); 
    const addToCartURL = $(this).data('add-to-cart-url');
    const csrfToken = $(this).data('csrf-token');
    console.log(productID);
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
          // Show the options block
          createShadedOverlay()
          $('#add-to-cart-options').show();
          button.prop('disabled', false);
        },
        error: function() {
          button.prop('disabled', false);
        }
      });
    });

    function createShadedOverlay() {
      const body = document.body;
      const overlay = document.createElement('div');
      overlay.classList.add('shaded-overlay');
      body.appendChild(overlay);
      const optionsdiv = document.getElementById('add-to-cart-options');
      optionsdiv.classList.add('unshaded-overlay');
      body.appendChild(optionsdiv);
    }
    
    function removeShadedOverlay() {
      const overlay = document.querySelector('.shaded-overlay');
      if (overlay) {
        overlay.remove();
      }
    }

    $('#continue-shopping').on('click', function(event) {
      event.preventDefault();
      removeShadedOverlay();
      $('#add-to-cart-options').hide();
    });
    
    // Handle go to cart button click
    $('#go-to-cart').on('click', function(event) {
      event.preventDefault();
      window.location.href = '/store/cart/';
    });
    
    const cartButton = document.getElementById('cart-button');
    const cartDropdown = document.getElementById('cart-dropdown');


    function fetchCartItems(xcsrf_token){
      fetch('/store/cart-action/list-products')
        .then(response => response.json())
        .then(data => {
          const cartItems = data.cart_items;
          const cartItemsList = document.getElementById('cart-items');
          const csrf_token = xcsrf_token
          cartItemsList.innerHTML = ''; // Clear existing cart items
    
          cartItems.forEach(item => {
            const li = document.createElement('li');
            li.textContent = `Product ID: ${item.product_id}, Quantity: `;
            
            const quantityInput = document.createElement('input');
            quantityInput.type = 'number';
            quantityInput.classList.add('quantity-input');
            quantityInput.value = item.quantity;
            quantityInput.min = '1';
            quantityInput.step = '1';
            quantityInput.dataset.productId = item.product_id;
            quantityInput.dataset.csrfToken = csrf_token;
            li.appendChild(quantityInput);
            
            li.appendChild(document.createTextNode(' '));

            const removeButton = document.createElement('a');
            removeButton.href = '#';
            removeButton.classList.add('remove-from-cart-button');
            removeButton.dataset.productId = item.product_id;
            removeButton.dataset.csrfToken = csrf_token;
            removeButton.textContent = 'Remove';
            li.appendChild(removeButton);

            cartItemsList.appendChild(li);
          });
        });
    }

      $(document).on('click', '.remove-from-cart-button', function(event) {
        event.preventDefault();
        const button = $(this);
        const productId = button.data('product-id');
        const csrfToken = button.data('csrf-token');
        const url = button.data('remove-from-cart-url');
        $.ajax({
          type: 'POST',
          url: url,
          data: {"product_id": productId},
          headers: { 'X-CSRFToken': csrfToken },          
            dataType: 'json',
            success: function(data) {
                alert("Item has been removed");
                location.reload();
            },
            error: function() {
                alert("Error occurred while removing the item from the cart.");
            }
        });
    });


    $(document).on('change', '.quantity-input', function(event) {
      event.preventDefault();
      const input = $(this);
      const formData = new FormData();
      const productID = $(this).data('product-id');
      const newQuantity = input.val();
      const csrfToken = $(this).data('csrf-token');
      formData.append('product_id', productID);
      formData.append('quantity', newQuantity);

    
      $.ajax({
        type: 'POST',
        url: '/../../cart/item/',
        data: formData, // Use the serialized form data
        headers: { 'X-CSRFToken': csrfToken },
        dataType: 'json',
        processData: false, // Prevent jQuery from processing the data
        contentType: false, // Let the browser set the content type        
      });
    });
