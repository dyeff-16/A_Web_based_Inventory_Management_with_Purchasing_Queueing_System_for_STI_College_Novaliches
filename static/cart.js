    function stockButton(action, itemCode, item_id, event){
        event.preventDefault();
        fetch('/cart/update_quantity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({action, itemCode, item_id})
        })
        .then (r => r.json())
        .then (data => {
            console.log(data.message);
            document.getElementById(`getCartItem_${item_id}`).textContent = data.new_quantity;
            getCartItem();
        })
    }


   function getCartItem(){
        fetch('/cart/getCartItem')
        .then (r=> r.json())
        .then (data =>{
            let myCart = document.getElementById('getCartItem');
            myCart.innerText = '';
            
            data.forEach(cart_items =>{
                myCart.innerText += cart_items.item_quantity;

            })
        });
    }
    setInterval(getCartItem, 2000)

    function updateTotal() {
        let total = 0;
        document.querySelectorAll('.select-item').forEach(function(checkbox) {
            if (checkbox.checked) {
                total += parseFloat(checkbox.getAttribute('data-price'));
            }
        });
        document.getElementById('selected-total').textContent = total.toFixed(2);
    }
