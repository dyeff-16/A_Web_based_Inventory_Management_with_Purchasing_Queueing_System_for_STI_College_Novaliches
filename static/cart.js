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
            document.getElementById(`subTotal_${item_id}`).textContent = data.total_amount; 
                // 🔑 Keep the checkbox price in sync with the new subtotal
            const cb = document.getElementById(`check_${item_id}`);
            if (cb) {
            cb.dataset.price = String(data.total_amount);     // update dataset
            cb.setAttribute('data-price', data.total_amount); // (optional) keep attr in sync
            }

            // Recompute the selected total (whether checked or not)
            updateTotal();
        })
    }


    function updateTotal() {
    let total = 0;

    document.querySelectorAll('.select-item').forEach(cb => {
        if (cb.checked) {
        total += Number(cb.dataset.price || cb.getAttribute('data-price') || 0);
        }
    });

    document.getElementById('selected-total').textContent = total.toFixed(2);
    }
