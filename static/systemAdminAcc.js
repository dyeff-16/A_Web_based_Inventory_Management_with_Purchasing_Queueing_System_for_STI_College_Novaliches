//basta dito get method iloload nalng ung 20 first account
function loadAccounts() {
    const tbody = document.getElementById('bodyAccount');
    tbody.innerHTML = '';

    fetch('/system_admin/getAccount')
        .then(r => r.json())
        .then(data => displayAccount(data.accounts))
}

//search dito yung account post method
function searchAccount() {
    const roleSelect = document.getElementById('roleSelect').value;
    const searchInput = document.getElementById('searchInput').value;
    const statusSelect = document.getElementById('statusSelect').value;

    //get element tbody ya
    const tbody = document.getElementById('bodyAccount');
    //Empty when reload the page
    tbody.innerText = '';

    fetch('/system_admin/getAccount', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ roleSelect, searchInput, statusSelect })
    })
        .then(r => r.json())
        .then(data => {
            console.log('POST response:', data);
            displayAccount(data.accounts);
        })
        .catch(err => console.error('POST error:', err));

}
//display lang ung accounts
function displayAccount(accounts) {
    //get element tbody ya
    const tbody = document.getElementById('bodyAccount');
    //Empty when reload the page
    tbody.innerText = '';
    accounts.forEach(acc => {

        //tr element create and center ung text
        const row = document.createElement('tr');
        row.classList.add('text-center');

        //td element create
        const tdEmail = document.createElement('td');
        const tdStatus = document.createElement('td');
        const tdRoles = document.createElement('td');

        //create button add class and attributes
        const myBtn = document.createElement('button');
        myBtn.classList.add('btn', 'text-light', 'bg-dark', 'btn-sm', 'm-2');
        myBtn.innerText = 'Edit';
        myBtn.setAttribute('onclick', 'editAcc(this.value)');

        //span element create and add class attribute badge i2
        const spanStatus = document.createElement('span');
        spanStatus.classList.add('badge');

        //check if active and inactive for color
        if (acc.status === 'active') {
            spanStatus.classList.add('bg-success');
            spanStatus.textContent = acc.status;
        } else {
            spanStatus.classList.add('bg-secondary');
            spanStatus.textContent = acc.status;
        }

        tdEmail.innerText = acc.email;
        tdRoles.innerText = acc.roles;
        myBtn.value = acc.student_id;
        myBtn.addEventListener('click', () => {
            console.log('Selected student ID:', myBtn.value);
        });
        tdStatus.appendChild(spanStatus);
        row.appendChild(tdEmail);
        row.appendChild(tdRoles);
        row.appendChild(tdStatus);
        row.appendChild(myBtn);
        tbody.appendChild(row);



    });
}
document.addEventListener("DOMContentLoaded", () => {
    displayPendingAccount();
});


function displayPendingAccount() {
    const tbody = document.getElementById("tbodypending");

    fetch("/system_admin/getPending")
        .then(res => res.json())
        .then(data => {
            tbody.innerHTML = "";

            // ✅ data is an object: { accounts: [...] }
            if (!data.accounts || data.accounts.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="2" class="text-center text-muted py-3">
                            No pending accounts.
                        </td>
                    </tr>
                `;
                return;
            }

            data.accounts.forEach(acc => {
                const row = document.createElement("tr");
                row.classList.add("align-middle");

                row.innerHTML = `
                    <td class="text-center">${acc.email}</td>
                    <td class="text-center">
                        <span class="icon-btn text-success me-2"
                              title="Approve"
                              onclick="handlePendingAction('approve', '${acc.email}')">
                          <i class="bi bi-check-circle-fill"></i>
                        </span>

                        <span class="icon-btn text-danger"
                              title="Reject"
                              onclick="handlePendingAction('reject', '${acc.email}')">
                          <i class="bi bi-x-circle-fill"></i>
                        </span>
                    </td>
                `;

                tbody.appendChild(row);
            });
        })
        .catch(err => {
            console.error("Error loading pending accounts:", err);
        });
}

function handlePendingAction(action, email) {
    const msg =
        action === "approve"
            ? `Are you sure you want to APPROVE this account?\n\n${email}`
            : `Are you sure you want to REJECT this account?\n\n${email}`;

    const ok = window.confirm(msg);
    if (!ok) return;

    updatePendingAccount(action, email);
}

function updatePendingAccount(action, email) {
    fetch("/system_admin/updatePending", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, email })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                displayPendingAccount(); // refresh table
            } else {
                alert(data.message || "Something went wrong.");
            }
        })
        .catch(err => {
            console.error("Error updating account:", err);
            alert("Error updating account.");
        });
}




function editAcc(studentId) {
    window.location.href = `/system_admin/edit_account/${studentId}`;
}
function changePermission() {
    const selectRoles = document.getElementById('selectRoles').value;
    let studentPermission = document.getElementById('studentPermission');
    let adminPermission = document.getElementById('adminPermission');

    if (selectRoles == 'admin') {
        adminPermission.style.display = 'block';
        studentPermission.style.display = 'none';
    }
    else if (selectRoles == 'student') {
        adminPermission.style.display = 'none';
        studentPermission.style.display = 'block';
    }
}
function submitRoles(email) {
    const selectRoles = document.getElementById('selectRoles').value;
    const selectStatus = document.getElementById('selectStatus').value;


    fetch('/system_admin/submitRoles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, selectRoles, selectStatus })
    })
        .then(r => r.json())
        .then(data => console.log(data.message))
    window.location.href = '/system_admin/accounts';
}

document.addEventListener('DOMContentLoaded', loadAccounts);
