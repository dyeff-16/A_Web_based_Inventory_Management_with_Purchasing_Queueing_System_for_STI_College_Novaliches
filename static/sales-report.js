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
                            total: amt,
                            sizes: item.size
                        };
                        }
                    });
                    });

                    // 2) Render one row per unique itemCode
                    for (const code in combined) {
                    const row = document.createElement('tr');

                    const tdName  = document.createElement('td');
                    const tdSizes = document.createElement('td');
                    const tdCode  = document.createElement('td');
                    const tdTotal = document.createElement('td');

                    tdName.innerText  = combined[code].name;
                    tdSizes.innerText = combined[size].sizes
                    tdCode.innerText  = code;
                    tdTotal.innerText = combined[code].total; 

                    row.appendChild(tdName);
                    row.appendChild(tdSizes);
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
                    const tdSizes = document.createElement('td');
                    const tdCode  = document.createElement('td');
                    const tdTotal = document.createElement('td');

                    tdName.innerText  = combined[code].name;
                    tdSizes.innerText = combined[size].sizes
                    tdCode.innerText  = code;
                    tdTotal.innerText = combined[code].total; 

                    row.appendChild(tdName);
                    row.appendChild(tdSizes);
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
                            total: amt,
                            sizes: item.size
                        };
                        }
                    });
                    });
                for (const code in combined) {
                    const row = document.createElement('tr');
                    
                    const tdName  = document.createElement('td');
                    const tdSizes = document.createElement('td');
                    const tdCode  = document.createElement('td');
                    const tdTotal = document.createElement('td');

                    tdName.innerText  = combined[code].name;
                    tdSizes.innerText = combined[code].sizes;
                    tdCode.innerText  = code;
                    tdTotal.innerText = combined[code].total + '.00'; 

                    row.appendChild(tdName);
                    row.appendChild(tdSizes);
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

    function generateReportTxt(){
        const reportType = document.getElementById('reportTypeTxt').value;
        const dateStart = document.getElementById('dateStartTxt').value;
        const dateEnd = document.getElementById('dateEndTxt').value;
        const combined = {}
        const tBodyElement = document.getElementById('itemTableReportsTxt')
        tBodyElement.innerHTML = "";
        if(reportType == 'monthly'){
            fetch('/report/monthlyTxt')
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
                            total: amt,
                            sizes: item.size
                        };
                        }
                    });
                    });

                    // 2) Render one row per unique itemCode
                    for (const code in combined) {
                    const row = document.createElement('tr');

                    const tdName  = document.createElement('td');
                    const tdSizes = document.createElement('td');
                    const tdCode  = document.createElement('td');
                    const tdTotal = document.createElement('td');

                    tdName.innerText  = combined[code].name;
                    tdSizes.innerText = combined[size].sizes
                    tdCode.innerText  = code;
                    tdTotal.innerText = combined[code].total; 

                    row.appendChild(tdName);
                    row.appendChild(tdSizes);
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
            fetch('/report/weeklyTxt')
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
                    const tdSizes = document.createElement('td');
                    const tdCode  = document.createElement('td');
                    const tdTotal = document.createElement('td');

                    tdName.innerText  = combined[code].name;
                    tdSizes.innerText = combined[size].sizes
                    tdCode.innerText  = code;
                    tdTotal.innerText = combined[code].total; 

                    row.appendChild(tdName);
                    row.appendChild(tdSizes);
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
            fetch('/report/rangeDateTxt',{
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
                            total: amt,
                            sizes: item.size
                        };
                        }
                    });
                    });
                for (const code in combined) {
                    const row = document.createElement('tr');
                    
                    const tdName  = document.createElement('td');
                    const tdSizes = document.createElement('td');
                    const tdCode  = document.createElement('td');
                    const tdTotal = document.createElement('td');

                    tdName.innerText  = combined[code].name;
                    tdSizes.innerText = combined[code].sizes;
                    tdCode.innerText  = code;
                    tdTotal.innerText = combined[code].total + '.00'; 

                    row.appendChild(tdName);
                    row.appendChild(tdSizes);
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
function generateTextbookReport() {
    const reportType = document.getElementById('reportType').value;
    const dateStart = document.getElementById('dateStart').value;
    const dateEnd = document.getElementById('dateEnd').value;

    const combined = {};
    const tBodyElement = document.getElementById('itemTableReports');
    tBodyElement.innerHTML = "";

    if (reportType === 'monthly') {
        fetch('/report/monthlyTxt')
            .then(r => r.json())
            .then(data => {
                data.result.forEach(result => {
                    result.items.forEach(item => {
                        const code = item.itemCode;
                        const amt = Number(item.subtotal ?? 0);

                        if (combined[code]) combined[code].total += amt;
                        else {
                            combined[code] = {
                                name: item.item_name,
                                total: amt,
                                sizes: item.size
                            };
                        }
                    });
                });

                for (const code in combined) {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${combined[code].name}</td>
                        <td>${combined[code].sizes}</td>
                        <td>${code}</td>
                        <td>₱ ${combined[code].total}.00</td>
                    `;
                    tBodyElement.appendChild(row);
                }

                document.getElementById('setTotalMonth').innerText = "₱ " + data.totalMonthly + ".00";
                document.getElementById('setMonth').innerText = data.month;
                document.getElementById('setYear').innerText = data.year + ": ";
            });
    }

    else if (reportType === 'weekly') {
        fetch('/report/weeklyTxt')
            .then(r => r.json())
            .then(data => {
                data.result.forEach(result => {
                    result.items.forEach(item => {
                        const code = item.itemCode;
                        const amt = Number(item.subtotal ?? 0);

                        if (combined[code]) combined[code].total += amt;
                        else {
                            combined[code] = {
                                name: item.item_name,
                                total: amt,
                                sizes: item.size
                            };
                        }
                    });
                });

                for (const code in combined) {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${combined[code].name}</td>
                        <td>${combined[code].sizes}</td>
                        <td>${code}</td>
                        <td>₱ ${combined[code].total}.00</td>
                    `;
                    tBodyElement.appendChild(row);
                }

                document.getElementById('setMonth').innerText = "";
                document.getElementById('setYear').innerText = "Weekly: ";
                document.getElementById('setTotalMonth').innerText = "₱ " + data.totalWeekly + ".00";
            });
    }

    else if (reportType === 'range') {
        if (!dateStart || !dateEnd) return alert("Choose start and end date");
        if (dateEnd < dateStart) return alert("Start date must be before end date");

        fetch('/report/rangeDateTxt', {
            method: 'POST',
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ reportType, dateStart, dateEnd })
        })
        .then(r => r.json())
        .then(data => {
            data.result.forEach(result => {
                result.items.forEach(item => {
                    const code = item.itemCode;
                    const amt = Number(item.subtotal ?? 0);

                    if (combined[code]) combined[code].total += amt;
                    else {
                        combined[code] = {
                            name: item.item_name,
                            total: amt,
                            sizes: item.size
                        };
                    }
                });
            });

            for (const code in combined) {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${combined[code].name}</td>
                    <td>${combined[code].sizes}</td>
                    <td>${code}</td>
                    <td>₱ ${combined[code].total}.00</td>
                `;
                tBodyElement.appendChild(row);
            }

            document.getElementById('setMonth').innerText = "From " + data.dateStart;
            document.getElementById('setYear').innerText = "to " + data.dateEnd;
            document.getElementById('setTotalMonth').innerText = "₱ " + data.totalRange + ".00";
        });
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