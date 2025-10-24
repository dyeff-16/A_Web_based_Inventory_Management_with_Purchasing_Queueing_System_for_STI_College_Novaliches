    function generateReport(){
        const reportType = document.getElementById('reportType').value;
        const dateStart = document.getElementById('dateStart').value;
        const dateEnd = document.getElementById('dateEnd').value;
        const combined = {}
        const tBodyElement = document.getElementById('itemTableReports')
        tBodyElement.innerHTML = "";
        if(reportType == 'monthly'){
            fetch('/report/monthly')
            .then(r => r.json())
            .then(data => {
                // this part get the data from python backend and python will create that backend reports
                data.result.forEach(result => {
                    result.items.forEach(item => {
                        const code = item.itemCode;
                        const amt = Number(item.subtotal ?? 0); 

                        if (combined[code]) {
                        combined[code].total += amt;
                        } else {
                        combined[code] = {
                            name: item.item_name || "No name",
                            total: amt
                        };
                        }
                    });
                    });

                    // 2) Render one row per unique itemCode
                    for (const code in combined) {
                    const row = document.createElement('tr');

                    const tdName  = document.createElement('td');
                    const tdCode  = document.createElement('td');
                    const tdTotal = document.createElement('td');

                    tdName.innerText  = combined[code].name;
                    tdCode.innerText  = code;
                    tdTotal.innerText = combined[code].total; 

                    row.appendChild(tdName);
                    row.appendChild(tdCode);
                    row.appendChild(tdTotal);
                    tBodyElement.appendChild(row);
                    }
                
                const month = document.getElementById('setMonth');
                const year = document.getElementById('setYear');
                const tdTotalMonth = document.getElementById('setTotalMonth');
                
                tdTotalMonth.innerText = '₱ ' + data.totalMonthly + '.00';
                month.innerText = data.month;
                year.innerText = data.year + ': ';
                
            })
        }
        else if(reportType == 'weekly'){
            fetch('/report/weekly')
            .then(r => r.json())
            .then(data => {
                // this part get the data from python backend and python will create that backend reports
                 data.result.forEach(result => {
                    result.items.forEach(item => {
                        const code = item.itemCode;
                        const amt = Number(item.subtotal ?? 0); // or item.total_amount

                        if (combined[code]) {
                        combined[code].total += amt;
                        } else {
                        combined[code] = {
                            name: item.item_name || "No name",
                            total: amt
                        };
                        }
                    });
                    });

                    // 2) Render one row per unique itemCode
                    for (const code in combined) {
                    const row = document.createElement('tr');

                    const tdName  = document.createElement('td');
                    const tdCode  = document.createElement('td');
                    const tdTotal = document.createElement('td');

                    tdName.innerText  = combined[code].name;
                    tdCode.innerText  = code;
                    tdTotal.innerText = combined[code].total; // format if you want

                    row.appendChild(tdName);
                    row.appendChild(tdCode);
                    row.appendChild(tdTotal);
                    tBodyElement.appendChild(row);
                    }
                const year = document.getElementById('setYear');
                const tdTotalMonth = document.getElementById('setTotalMonth');
                const month = document.getElementById('setMonth');
                
                month.innerText = '';
                year.innerText = 'Weekly: ';
                tdTotalMonth.innerText = '₱ ' + data.totalWeekly + '.00';

            })
        }
        else if(reportType == 'range'){
            if(!dateStart || !dateEnd){
                alert("Choose start and end date")
            }
            else if(dateEnd < dateStart){
                alert("Start with start date not end date")
            }
            else{
            fetch('/report/rangeDate',{
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({reportType, dateStart, dateEnd})
            })
            .then(r => r.json())
            .then(data => {
                // this part get the data from python backend and python will create that backend reports
                data.result.forEach(result => {
                    result.items.forEach(item => {
                        const code = item.itemCode;
                        const amt = Number(item.subtotal ?? 0); // or item.total_amount

                        if (combined[code]) {
                        combined[code].total += amt;
                        } else {
                        combined[code] = {
                            name: item.item_name || "No name",
                            total: amt
                        };
                        }
                    });
                    });
                for (const code in combined) {
                    const row = document.createElement('tr');

                    const tdName  = document.createElement('td');
                    const tdCode  = document.createElement('td');
                    const tdTotal = document.createElement('td');

                    tdName.innerText  = combined[code].name;
                    tdCode.innerText  = code;
                    tdTotal.innerText = combined[code].total; // format if you want

                    row.appendChild(tdName);
                    row.appendChild(tdCode);
                    row.appendChild(tdTotal);
                    tBodyElement.appendChild(row);
                }
                const year = document.getElementById('setYear');
                const tdTotalMonth = document.getElementById('setTotalMonth');
                const month = document.getElementById('setMonth');
                
                month.innerText = 'From ' + data.dateStart;
                year.innerText = 'to  ' + data.dateEnd;
                tdTotalMonth.innerText = '₱ ' + data.totalRange + '.00';                
                    
            })
            }
        }
        else{
            //nothing for now
        }
    }
    
    function viewDate(){
    const reportType = document.getElementById('reportType').value;
    const dateStart = document.getElementById('dateStart');
    const dateEnd = document.getElementById('dateEnd');
    const textStartDate = document.getElementById('textStartDate');
    const textEndDate = document.getElementById('textEndDate');

    const show = (reportType === 'range') ? 'block' : 'none';
    dateStart.style.display     = show;
    dateEnd.style.display       = show;
    textStartDate.style.display = show;
    textEndDate.style.display   = show;
    
    }