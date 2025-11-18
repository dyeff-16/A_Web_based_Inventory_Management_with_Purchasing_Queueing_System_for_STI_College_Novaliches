// document.getElementById('searchInput').addEventListener('input', function () {

//     const search = this.value;
//     const filter = document.getElementById('filter_category').value;

//     fetch('/order/getOrder', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ search, filter })
//     })
//         .then(r => r.json())
//         .then(data => displayOrders(data.orders))
// })

// function searchBtn() {
//     const search = document.getElementById('searchInput').value;
//     const filter = document.getElementById('filter_category').value;

//     fetch('/order/getOrder', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ search, filter })
//     })
//         .then(r => r.json())
//         .then(data => displayOrders(data.orders))
// }

function orderRelease() {
    const referenceNumber = document.getElementById('referenceNumber').value;
    const invoiceNumber = document.getElementById('invoiceNumber').value;
    const releaseDate = document.getElementById('releaseDate').value;

    const btnRelease = document.getElementById('btnRelease');
    btnRelease.disabled = true;

    if (invoiceNumber === '' || releaseDate === '') {
        alert('Please input both invoice number and release date');
        btnRelease.disabled = false;
        return;
    }

    fetch('/order/orderRelease', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ referenceNumber, invoiceNumber, releaseDate })
    })
        .then(r => r.json())
        .then(data => {

            if (data.success) {
                alert('Order release');
                btnRelease.disabled = false;
                console.log('successful release');
            }

            if (data.message) {
                alert(data.message);
                btnRelease.disabled = false;
                console.log('not successful release');
            }

        })
}

// function paidOrder() {
//     fetch('/order/paidOrder')
//         .then(r => r.json())
//         .then(data => displayOrders(data.orders))
// }

function submitStatus() {

    const indexData = document.getElementById('indexData').dataset;
    console.log("Reference Number:", indexData.rfr);
    const referenceNumber = indexData.rfr;
    // const invoiceNumber = document.querySelector('#receiptModal1 #invoiceNumber').value.trim();
    // console.log('Invoice Number:', invoiceNumber);

    fetch('/order/setPaid', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ referenceNumber })
    })
        .then(r => r.json())
        .then(data => {

            if (data.success) {
                console.log(`status: paid - ${referenceNumber}`);
                window.location.href = '/order/orders';
            }

            if (data.message) {
                alert(data.message);
            }

        })
}

function displayOrders(orders) {
    const tbody = document.getElementById('tbody');
    tbody.innerHTML = ''; 

    orders.forEach((order, index) => {
        const collapseId = `orderDetails_${index}`;

        //tr1
        const tr1 = document.createElement('tr');

        const tdNum = document.createElement('td');
        tdNum.classList.add('text-primary', 'fw-semibold');
        tdNum.innerText = order.reference_number;

        const tdName = document.createElement('td');
        tdName.innerText = order.name;

        const tdDate = document.createElement('td');
        tdDate.innerHTML = `${order.order_date}<div class="small text-muted">${order.order_time}</div>`;

        // action buttons container
        const tdAction = document.createElement('td');
        const group = document.createElement('div');
        group.classList.add('d-flex', 'gap-1', 'justify-content-center');

        const btnReceipt = document.createElement('button');
        btnReceipt.classList.add('btn', 'btn-sm', 'btn-outline-secondary');
        btnReceipt.innerHTML = `<i class="bi bi-receipt me-1"></i>View Receipt`;
        btnReceipt.setAttribute('data-bs-toggle', 'modal');
        btnReceipt.setAttribute('data-bs-target', '#receiptModal1');

        btnReceipt.dataset.index = index;
        btnReceipt.dataset.rfr = order.reference_number;
        btnReceipt.dataset.image = order.receipt || 'https://via.placeholder.com/400x600/e0e0e0/666666?text=No+Receipt';

        if (!order.receipt) {
            btnReceipt.hidden = true;
        }

        btnReceipt.addEventListener('click', () => {
            const declinedBtn = document.getElementById('btnDeclined');
            declinedBtn.dataset.rfr = btnReceipt.dataset.rfr;

            const confirmBtn = document.getElementById('indexData');
            confirmBtn.dataset.index = btnReceipt.dataset.index;
            confirmBtn.dataset.rfr = btnReceipt.dataset.rfr;
            confirmBtn.dataset.image = btnReceipt.dataset.image;


            const img = document.getElementById('receiptImage');
            const base64Data = btnReceipt.dataset.image;

            if (img && base64Data) {

                if (base64Data.startsWith('https://')) {

                    img.src = base64Data;
                } else {

                    img.src = `data:image/jpeg;base64,${base64Data}`;
                }
            } else {
                img.src = 'https://via.placeholder.com/400x600/e0e0e0/666666?text=Receipt+Data+Missing';
            }
        });

        // Collapse button
        const btnCollapse = document.createElement('button');
        btnCollapse.classList.add('btn', 'btn-sm', 'btn-outline-secondary');
        btnCollapse.setAttribute('data-bs-toggle', 'collapse');
        btnCollapse.setAttribute('data-bs-target', `#${collapseId}`);
        btnCollapse.innerHTML = `<i class="bi bi-caret-down-fill"></i>`;

        group.appendChild(btnReceipt);
        group.appendChild(btnCollapse);
        tdAction.appendChild(group);

        tr1.appendChild(tdNum);
        tr1.appendChild(tdName);
        tr1.appendChild(tdDate);
        tr1.appendChild(tdAction);

        // tr2 — collapsible details
        const tr2 = document.createElement('tr');
        tr2.classList.add('collapse');
        tr2.id = collapseId;

        const tdCollapse = document.createElement('td');
        tdCollapse.colSpan = 7;
        tdCollapse.classList.add('text-start', 'bg-light');

        const rowDiv = document.createElement('div');
        rowDiv.classList.add('row', 'g-3', 'p-3');

        // Email & Student ID
        const col1 = document.createElement('div');
        col1.classList.add('col-md-4');
        const emailP = document.createElement('p');
        emailP.classList.add('mb-2');
        emailP.innerHTML = `<strong>Email:</strong> ${order.email}`;
        const stdP = document.createElement('p');
        stdP.classList.add('mb-2');
        stdP.innerHTML = `<strong>Student ID:</strong> ${order.student_id}`;
        col1.appendChild(emailP);
        col1.appendChild(stdP);

        // Total & Status
        const col2 = document.createElement('div');
        col2.classList.add('col-md-4');
        const totalP = document.createElement('p');
        totalP.classList.add('mb-2');
        totalP.innerHTML = `<strong>Total:</strong> ₱${order.total_amount}`;
        const statusP = document.createElement('p');
        statusP.classList.add('mb-2');
        statusP.innerHTML = `<strong>Status:</strong> <span class="badge bg-info">${order.status}</span>`;
        col2.appendChild(totalP);
        col2.appendChild(statusP);

        // Items
        const col3 = document.createElement('div');
        col3.classList.add('col-12');
        const label = document.createElement('p');
        label.classList.add('mb-2');
        label.innerHTML = '<strong>Items Ordered:</strong>';
        const list = document.createElement('ul');
        list.classList.add('mb-0');

        (order.items || []).forEach(item => {
            const li = document.createElement('li');


            li.innerText = `${item.item_name} ${item.size} - ${item.quantity} pcs - ₱${item.price}`;
            list.appendChild(li);
        });

        col3.appendChild(label);
        col3.appendChild(list);

        // Combine sections
        rowDiv.appendChild(col1);
        rowDiv.appendChild(col2);
        rowDiv.appendChild(col3);
        tdCollapse.appendChild(rowDiv);
        tr2.appendChild(tdCollapse);

        // Add both rows to table
        tbody.appendChild(tr1);
        tbody.appendChild(tr2);
    });


}

function setDeclined() {
    const reason = document.getElementById('reason_input').value;
    const btnDeclined = document.getElementById('btnDeclined').dataset;
    const ref_num = btnDeclined.rfr;

    fetch('/order/setDeclined', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason, ref_num })
    })
        .then(r => r.json())
        .then(data => {
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            }
        })
        .catch(err => {
            console.error(err);
            alert('Failed to decline.');
        });
}


document.getElementById('Orders').addEventListener('click', function () {
    fetch('/order/placeOrder')
        .then(r => r.json())
        .then(data => {
            const tbody = document.getElementById('tbody');
            tbody.innerHTML = '';

            data.orders.forEach((order, index) => {

                // Use order._id for guaranteed unique ID across the application
                const collapseId = `po-detail-${order._id}`;

                // --- MAIN ORDER ROW (tr1) ---
                const tr1 = document.createElement('tr');
                tr1.classList.add('align-middle');

                const tdRfrNum = document.createElement('td');
                const tdName = document.createElement('td');
                const tdDate = document.createElement('td');
                const tdAction = document.createElement('td'); // Cell for the button group
                tdAction.classList.add('text-center');

                // Create the button group for actions
                const group = document.createElement('div');
                group.classList.add('btn-group', 'btn-group-sm');

                // --- COLLAPSE BUTTON ---
                const btnCollapse = document.createElement('button');
                btnCollapse.classList.add('btn', 'btn-sm', 'btn-outline-secondary');
                btnCollapse.setAttribute('data-bs-toggle', 'collapse');
                btnCollapse.setAttribute('data-bs-target', `#${collapseId}`);
                btnCollapse.innerHTML = `Details`;
                btnCollapse.title = 'Toggle Details';


                group.appendChild(btnCollapse);
                tdAction.appendChild(group);

                tdRfrNum.innerText = order.reference_number;
                tdName.innerText = order.name;

                // Assuming order_date and order_time are available directly
                tdDate.innerText = `${order.order_date} ${order.order_time}`;

                tr1.appendChild(tdRfrNum);
                tr1.appendChild(tdName);
                tr1.appendChild(tdDate);
                tr1.appendChild(tdAction);

                tbody.appendChild(tr1);

                // --- DETAIL ROW (tr2) — collapsible details ---
                const tr2 = document.createElement('tr');
                tr2.classList.add('collapse'); // Bootstrap's collapse class
                tr2.id = collapseId; // Linked to the button's data-bs-target

                const tdCollapse = document.createElement('td');
                // Assuming 4 visible columns (RfrNum, Name, Date, Action)
                tdCollapse.colSpan = 4;
                tdCollapse.classList.add('text-start', 'bg-light');

                const rowDiv = document.createElement('div');
                rowDiv.classList.add('row', 'g-3', 'p-3');

                // Email & Student ID (col1)
                const col1 = document.createElement('div');
                col1.classList.add('col-md-4');
                const emailP = document.createElement('p');
                emailP.classList.add('mb-2');
                emailP.innerHTML = `<strong>Email:</strong> ${order.email || 'N/A'}`;
                const stdP = document.createElement('p');
                stdP.classList.add('mb-2');
                stdP.innerHTML = `<strong>Student ID:</strong> ${order.student_id || 'N/A'}`;
                col1.appendChild(emailP);
                col1.appendChild(stdP);

                // Total & Status (col2)
                const col2 = document.createElement('div');
                col2.classList.add('col-md-4');
                const totalP = document.createElement('p');
                totalP.classList.add('mb-2');
                totalP.innerHTML = `<strong>Total:</strong> ₱${order.total_amount || 'N/A'}`;

                const statusP = document.createElement('p');
                statusP.classList.add('mb-2');
                // Using badge-warning for pending/active orders
                statusP.innerHTML = `<strong>Status:</strong> <span class="badge bg-warning">${order.status || 'N/A'}</span>`;

                col2.appendChild(totalP);
                col2.appendChild(statusP);

                // Items (col3)
                const col3 = document.createElement('div');
                col3.classList.add('col-12', 'col-md-4');
                const label = document.createElement('p');
                label.classList.add('mb-2', 'fw-bold');
                label.innerHTML = 'Items Ordered:';
                const itemList = document.createElement('ul');
                itemList.classList.add('list-unstyled', 'mb-0');

                (order.items || []).forEach(item => {
                    const li = document.createElement('li');
                    const sizeText = item.size ? ` (${item.size})` : '';
                    li.innerText = `${item.item_name}${sizeText} - ${item.quantity} pcs - ₱${item.price}`;
                    itemList.appendChild(li);
                });

                col3.appendChild(label);
                col3.appendChild(itemList);

                // Combine sections
                rowDiv.appendChild(col1);
                rowDiv.appendChild(col2);
                rowDiv.appendChild(col3);
                tdCollapse.appendChild(rowDiv);
                tr2.appendChild(tdCollapse);

                // Add detail row immediately after main row
                tbody.appendChild(tr2);
            });
        })
})

document.getElementById('Paid').addEventListener('click', function () {
    fetch('/order/paidOrder')
        .then(r => r.json())
        .then(data => displayOrders(data.orders))
})
document.getElementById('toRelease').addEventListener('click', function () {
    fetch('/order/toReleaseOrder')
        .then(r => r.json())
        .then(data => {
            const tbody = document.getElementById('tbody');
            tbody.innerHTML = '';

            data.orders.forEach((order) => {

                const collapseId = `po-detail-${order._id}`;

                const tr1 = document.createElement('tr');
                tr1.classList.add('align-middle');

                const tdRfrNum = document.createElement('td');
                const tdName = document.createElement('td');
                const tdDate = document.createElement('td');
                const tdAction = document.createElement('td');
                tdAction.classList.add('text-center');


                const group = document.createElement('div');
                group.classList.add('btn-group', 'btn-group-sm');


                const btnCollapse = document.createElement('button');
                btnCollapse.classList.add('btn', 'btn-sm', 'btn-outline-secondary');
                btnCollapse.setAttribute('data-bs-toggle', 'collapse');
                btnCollapse.setAttribute('data-bs-target', `#${collapseId}`);
                btnCollapse.innerHTML = `Details`;
                btnCollapse.title = 'Toggle Details';


                group.appendChild(btnCollapse);
                tdAction.appendChild(group);

                tdRfrNum.innerText = order.reference_number;
                tdName.innerText = order.name;


                tdDate.innerText = `${order.order_date} ${order.order_time}`;

                tr1.appendChild(tdRfrNum);
                tr1.appendChild(tdName);
                tr1.appendChild(tdDate);
                tr1.appendChild(tdAction);

                tbody.appendChild(tr1);

                const tr2 = document.createElement('tr');
                tr2.classList.add('collapse');
                tr2.id = collapseId;

                const tdCollapse = document.createElement('td');

                tdCollapse.colSpan = 4;
                tdCollapse.classList.add('text-start', 'bg-light');

                const rowDiv = document.createElement('div');
                rowDiv.classList.add('row', 'g-3', 'p-3');

                const col1 = document.createElement('div');
                col1.classList.add('col-md-4');
                const emailP = document.createElement('p');
                emailP.classList.add('mb-2');
                emailP.innerHTML = `<strong>Email:</strong> ${order.email || 'N/A'}`;
                const stdP = document.createElement('p');
                stdP.classList.add('mb-2');
                stdP.innerHTML = `<strong>Student ID:</strong> ${order.student_id || 'N/A'}`;
                col1.appendChild(emailP);
                col1.appendChild(stdP);

                const col2 = document.createElement('div');
                col2.classList.add('col-md-4');
                const totalP = document.createElement('p');
                totalP.classList.add('mb-2');
                totalP.innerHTML = `<strong>Total:</strong> ₱${order.total_amount || 'N/A'}`;

                const statusP = document.createElement('p');
                statusP.classList.add('mb-2');
                statusP.innerHTML = `<strong>Status:</strong> <span class="badge bg-warning">${order.status || 'N/A'}</span>`;

                col2.appendChild(totalP);
                col2.appendChild(statusP);

                const col3 = document.createElement('div');
                col3.classList.add('col-12', 'col-md-4');
                const label = document.createElement('p');
                label.classList.add('mb-2', 'fw-bold');
                label.innerHTML = 'Items Ordered:';
                const itemList = document.createElement('ul');
                itemList.classList.add('list-unstyled', 'mb-0');

                (order.items || []).forEach(item => {
                    const li = document.createElement('li');
                    const sizeText = item.size ? ` (${item.size})` : '';
                    li.innerText = `${item.item_name}${sizeText} - ${item.quantity} pcs - ₱${item.price}`;
                    itemList.appendChild(li);
                });

                col3.appendChild(label);
                col3.appendChild(itemList);

                rowDiv.appendChild(col1);
                rowDiv.appendChild(col2);
                rowDiv.appendChild(col3);
                tdCollapse.appendChild(rowDiv);
                tr2.appendChild(tdCollapse);

                tbody.appendChild(tr2);
            });
        })
})
document.getElementById('Claimed').addEventListener('click', function () {
    fetch('/order/claimedOrder')
        .then(r => r.json())
        .then(data => {
            const tbody = document.getElementById('tbody');
            tbody.innerHTML = '';

            data.orders.forEach((order) => {

                const collapseId = `po-detail-${order._id}`;

                const tr1 = document.createElement('tr');
                tr1.classList.add('align-middle');

                const tdRfrNum = document.createElement('td');
                const tdName = document.createElement('td');
                const tdDate = document.createElement('td');
                const tdAction = document.createElement('td');
                tdAction.classList.add('text-center');


                const group = document.createElement('div');
                group.classList.add('btn-group', 'btn-group-sm');


                const btnCollapse = document.createElement('button');
                const btnClaimed = document.createElement('button');
                btnCollapse.classList.add('btn', 'btn-sm', 'btn-outline-secondary');
                btnCollapse.setAttribute('data-bs-toggle', 'collapse');
                btnCollapse.setAttribute('data-bs-target', `#${collapseId}`);
                btnCollapse.innerHTML = `Details`;
                btnCollapse.title = 'Toggle Details';

                btnClaimed.innerText = 'Claimed'
                btnClaimed.classList.add('btn', 'btn-sm', 'btn-primary', 'mx-2');
                btnClaimed.dataset.rfr = order.reference_number;
                btnClaimed.addEventListener('click', () => {
                    const referenceNumber = btnClaimed.dataset.rfr;
                    console.log(referenceNumber);
                    fetch('/order/setClaimed', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ referenceNumber })
                    })
                        .then(r => r.json())
                        .then(data => {
                            if (data.success) {
                                console.log(`status: complete - ${referenceNumber}`);
                                window.location.href = '/order/orders';
                            }

                        })
                });

                group.appendChild(btnClaimed);
                group.appendChild(btnCollapse);
                tdAction.appendChild(group);

                tdRfrNum.innerText = order.reference_number;
                tdName.innerText = order.name;


                tdDate.innerText = `${order.order_date} ${order.order_time}`;

                tr1.appendChild(tdRfrNum);
                tr1.appendChild(tdName);
                tr1.appendChild(tdDate);
                tr1.appendChild(tdAction);

                tbody.appendChild(tr1);

                const tr2 = document.createElement('tr');
                tr2.classList.add('collapse');
                tr2.id = collapseId;

                const tdCollapse = document.createElement('td');

                tdCollapse.colSpan = 4;
                tdCollapse.classList.add('text-start', 'bg-light');

                const rowDiv = document.createElement('div');
                rowDiv.classList.add('row', 'g-3', 'p-3');

                const col1 = document.createElement('div');
                col1.classList.add('col-md-4');
                const emailP = document.createElement('p');
                emailP.classList.add('mb-2');
                emailP.innerHTML = `<strong>Email:</strong> ${order.email || 'N/A'}`;
                const stdP = document.createElement('p');
                stdP.classList.add('mb-2');
                stdP.innerHTML = `<strong>Student ID:</strong> ${order.student_id || 'N/A'}`;
                col1.appendChild(emailP);
                col1.appendChild(stdP);

                const col2 = document.createElement('div');
                col2.classList.add('col-md-4');
                const totalP = document.createElement('p');
                totalP.classList.add('mb-2');
                totalP.innerHTML = `<strong>Total:</strong> ₱${order.total_amount || 'N/A'}`;

                const statusP = document.createElement('p');
                statusP.classList.add('mb-2');
                statusP.innerHTML = `<strong>Status:</strong> <span class="badge bg-warning">${order.status || 'N/A'}</span>`;

                col2.appendChild(totalP);
                col2.appendChild(statusP);

                const col3 = document.createElement('div');
                col3.classList.add('col-12', 'col-md-4');
                const label = document.createElement('p');
                label.classList.add('mb-2', 'fw-bold');
                label.innerHTML = 'Items Ordered:';
                const itemList = document.createElement('ul');
                itemList.classList.add('list-unstyled', 'mb-0');

                (order.items || []).forEach(item => {
                    const li = document.createElement('li');
                    const sizeText = item.size ? ` (${item.size})` : '';
                    li.innerText = `${item.item_name}${sizeText} - ${item.quantity} pcs - ₱${item.price}`;
                    itemList.appendChild(li);
                });

                col3.appendChild(label);
                col3.appendChild(itemList);

                rowDiv.appendChild(col1);
                rowDiv.appendChild(col2);
                rowDiv.appendChild(col3);
                tdCollapse.appendChild(rowDiv);
                tr2.appendChild(tdCollapse);

                tbody.appendChild(tr2);
            });
        })
})
document.getElementById('orderHistory').addEventListener('click', function () {
    fetch('/order/order_history')
        .then(r => r.json())
        .then(data => {
            const tbody = document.getElementById('tbody');
            tbody.innerHTML = '';

            data.order_history.forEach(history => {
                const collapseId = `oh-detail-${history._id}`;


                const tr1 = document.createElement('tr');
                tr1.classList.add('align-middle');

                const tdRfrNum = document.createElement('td');
                const tdName = document.createElement('td');
                const tdDate = document.createElement('td');
                const tdAction = document.createElement('td');
                tdAction.classList.add('text-center');

                const group = document.createElement('div');
                group.classList.add('btn-group', 'btn-group-sm');

                const btnCollapse = document.createElement('button');
                btnCollapse.classList.add('btn', 'btn-sm', 'btn-outline-secondary');
                btnCollapse.setAttribute('data-bs-toggle', 'collapse');
                btnCollapse.setAttribute('data-bs-target', `#${collapseId}`);
                btnCollapse.innerHTML = `Details`;
                btnCollapse.title = 'Toggle Details';

                group.appendChild(btnCollapse);
                tdAction.appendChild(group);

                tdRfrNum.innerText = history.reference_number;
                tdName.innerText = history.name;

                tdDate.innerHTML = history.date_html || `${history.order_date} ${history.order_time}`;

                tr1.appendChild(tdRfrNum);
                tr1.appendChild(tdName);
                tr1.appendChild(tdDate);
                tr1.appendChild(tdAction);

                tbody.appendChild(tr1);

                const tr2 = document.createElement('tr');
                tr2.classList.add('collapse');
                tr2.id = collapseId;

                const tdCollapse = document.createElement('td');
                tdCollapse.colSpan = 4;
                tdCollapse.classList.add('text-start', 'bg-light');

                const rowDiv = document.createElement('div');
                rowDiv.classList.add('row', 'g-3', 'p-3');

                const col1 = document.createElement('div');
                col1.classList.add('col-md-4');
                const emailP = document.createElement('p');
                emailP.classList.add('mb-2');
                emailP.innerHTML = `<strong>Email:</strong> ${history.email || 'N/A'}`;
                const stdP = document.createElement('p');
                stdP.classList.add('mb-2');
                stdP.innerHTML = `<strong>Student ID:</strong> ${history.student_id || 'N/A'}`;
                col1.appendChild(emailP);
                col1.appendChild(stdP);

                const col2 = document.createElement('div');
                col2.classList.add('col-md-4');
                const totalP = document.createElement('p');
                totalP.classList.add('mb-2');
                totalP.innerHTML = `<strong>Total:</strong> ₱${history.total_amount || 'N/A'}`;

                const invoiceP = document.createElement('p');
                invoiceP.classList.add('mb-2');
                invoiceP.innerHTML = `<strong>Invoice:</strong> ${history.invoiceNumber || 'N/A'}`;

                col2.appendChild(totalP);
                col2.appendChild(invoiceP);

                const col3 = document.createElement('div');
                col3.classList.add('col-12', 'col-md-4');
                const label = document.createElement('p');
                label.classList.add('mb-2', 'fw-bold');
                label.innerHTML = 'Items Ordered:';
                const itemList = document.createElement('ul');
                itemList.classList.add('list-unstyled', 'mb-0');

                (history.items || []).forEach(item => {
                    const li = document.createElement('li');
                    const sizeText = item.size ? ` (${item.size})` : '';
                    li.innerText = `${item.item_name}${sizeText} - ${item.quantity} pcs - ₱${item.price}`;
                    itemList.appendChild(li);
                });

                col3.appendChild(label);
                col3.appendChild(itemList);

                rowDiv.appendChild(col1);
                rowDiv.appendChild(col2);
                rowDiv.appendChild(col3);
                tdCollapse.appendChild(rowDiv);
                tr2.appendChild(tdCollapse);

                tbody.appendChild(tr2);
            })
        })
})




document.getElementById('openDecline1').addEventListener('click', function () {
    const receiptModal = document.getElementById('receiptModal1');
    const declineModal = document.getElementById('declineModal1');

    // Hide receipt modal first
    const receiptInstance = bootstrap.Modal.getInstance(receiptModal) || new bootstrap.Modal(receiptModal);
    receiptInstance.hide();

    // Show decline modal once receipt is hidden
    receiptModal.addEventListener('hidden.bs.modal', function handleHidden() {
        const declineInstance = new bootstrap.Modal(declineModal);
        declineInstance.show();
        receiptModal.removeEventListener('hidden.bs.modal', handleHidden);
    });
});