    //basta dito get method iloload nalng ung 20 first account
    function loadAccounts() {
        const tbody = document.getElementById('bodyAccount');
        tbody.innerHTML = '';

        fetch('/system_admin/getAccount') 
            .then(r => r.json())
            .then(data => displayAccount(data.accounts))
    }
            
    //search dito yung account post method
    function searchAccount(){
        const roleSelect = document.getElementById('roleSelect').value;
        const searchInput = document.getElementById('searchInput').value;
        const statusSelect = document.getElementById('statusSelect').value;

        //get element tbody ya
        const tbody = document.getElementById('bodyAccount');
        //Empty when reload the page
        tbody.innerText = ''; 

        fetch('/system_admin/getAccount', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({roleSelect, searchInput, statusSelect})
        })
        .then(r => r.json())
        .then(data =>{
            console.log('POST response:', data);
            displayAccount(data.accounts);
            })
        .catch(err => console.error('POST error:', err));

        }
    //display lang ung accounts
    function displayAccount(accounts){
        //get element tbody ya
        const tbody = document.getElementById('bodyAccount');
        //Empty when reload the page
        tbody.innerText = ''; 
            accounts.forEach(acc =>  {

                    //tr element create and center ung text
                    const row = document.createElement('tr');
                    row.classList.add('text-center');   

                    //td element create
                    const tdEmail = document.createElement('td');
                    const tdStatus = document.createElement('td');
                    const tdRoles = document.createElement('td');

                    //create button add class and attributes
                    const myBtn = document.createElement('button');
                    myBtn.classList.add('btn', 'text-light','bg-dark','btn-sm', 'm-2');
                    myBtn.innerText = 'Edit';
                    myBtn.setAttribute('onclick', 'editAcc(this.value)');

                    //span element create and add class attribute badge i2
                    const spanStatus = document.createElement('span');
                    spanStatus.classList.add('badge');

                    //check if active and inactive for color
                    if(acc.status === 'active'){
                        spanStatus.classList.add('bg-success');
                        spanStatus.textContent = acc.status; 
                    }else{
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
    
    function editAcc(studentId) {
    window.location.href = `/system_admin/edit_account/${studentId}`;
    }
    function changePermission(){
        const selectRoles = document.getElementById('selectRoles').value;
        let studentPermission = document.getElementById('studentPermission');
        let adminPermission = document.getElementById('adminPermission');
        
        if(selectRoles == 'admin'){
            adminPermission.style.display = 'block';
            studentPermission.style.display = 'none';
        }
        else if(selectRoles == 'student'){
            adminPermission.style.display = 'none';
            studentPermission.style.display = 'block';
        }
    }
    function submitRoles(email){
        const selectRoles = document.getElementById('selectRoles').value;
        const selectStatus = document.getElementById('selectStatus').value;
        

        fetch('/system_admin/submitRoles', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, selectRoles, selectStatus})
        })
        .then(r => r.json())
        .then(data => console.log(data.message))
         window.location.href = '/system_admin/accounts';
    }

document.addEventListener('DOMContentLoaded', loadAccounts);
