// Add item to cart on form submission
$('#add-to-cart-form').on('submit', function(event) {
    event.preventDefault();
    const form = $(this);
    const formData = new FormData(form[0]); // Serialize the form data correctly
    $.ajax({
        type: form.attr('method'),
        url: form.attr('action'),
        data: formData, // Use the serialized form data
        dataType: 'json',
        processData: false, // Prevent jQuery from processing the data
        contentType: false, // Let the browser set the content type
        success: function(data) {
            alert(data.message);
            fetchCartItems();
        }
    });
});


// Fetch cart items and update the display
function fetchCartItems() {
    fetch('/cart/')
        .then(response => response.json())
        .then(data => {
            const cartItems = data.cart_items;
            const cartItemsList = $('#cart-items');
            cartItemsList.empty();
            cartItems.forEach(item => {
                const li = $('<li>').text(`Product ID: ${item.product_id}, Quantity: ${item.quantity}`);
                cartItemsList.append(li);
                
            });
        });
}
