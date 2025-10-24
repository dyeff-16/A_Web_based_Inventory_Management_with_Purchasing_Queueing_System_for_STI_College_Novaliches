    function postAuditLog(){
        const tbody = document.getElementById('tbAuditLog');
        const selectFilter = document.getElementById('selectFilter').value;
        const inputAuditlog = document.getElementById('inputAuditlog').value;
        tbody.innerHTML = '';

        fetch('/system_admin/auditLog',{
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ inputAuditlog, selectFilter }) 
        })
        .then(r => r.json())
        .then(data => {
            displayAuditLog(data.auditlog);
        })
    }

    function getAuditLog(){
        fetch('/system_admin/auditLog')
        .then(r => r.json())
        .then(data => displayAuditLog(data.auditlog))
    }

    function displayAuditLog(data){
         //get element tbody ya
        const tbody = document.getElementById('tbAuditLog');
        //Empty when reload the page
        tbody.innerText = ''; 

        data.forEach(audit => {
            const row = document.createElement('tr');
            row.classList.add('text-center');

            const tdEmail = document.createElement('td');
            const tdDateTime = document.createElement('td');
            const tdAction = document.createElement('td');

            tdEmail.innerText = audit.email;
            tdDateTime.innerText = audit.timestamp_str;
            tdAction.innerText = audit.action;

            row.appendChild(tdEmail);
            row.appendChild(tdDateTime);
            row.appendChild(tdAction);
            tbody.appendChild(row);
        });
    }

document.addEventListener('DOMContentLoaded', getAuditLog);
