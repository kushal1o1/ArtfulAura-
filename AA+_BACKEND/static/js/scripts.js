// JavaScript for Add to Cart Functionality
document.addEventListener('DOMContentLoaded', () => {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const productId = event.target.dataset.id;
            alert(`Product ${productId} added to cart!`);
            // Here you would call an AJAX request to your backend to add the product to the cart
        });
    });
});
