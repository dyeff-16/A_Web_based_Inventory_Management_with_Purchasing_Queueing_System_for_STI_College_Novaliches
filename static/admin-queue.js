//    function startQueue(){
//   const queueLimit = document.getElementById('queueLimit').value;
//   document.getElementById('limitSetup').style.display = 'none';
//   document.getElementById('queuePage').style.display = 'block';

//   fetch('/queue_admin/startQueue', {
//     method: 'POST',
//     headers: {'Content-Type': 'application/json'},
//     body: JSON.stringify({ queueLimit })
//   })
//   .then(r => r.json())
//   .then(data => {
//     // Helpful to see the shape
//     console.log('startQueue data:', data);
//     displayQueue(data.queue || [], data.skip || []);
//   })
//   .catch(err => console.error('startQueue error:', err));
// }

// function displayQueue(queue, skip) {
//   // normalize
//   if (!Array.isArray(queue)) queue = [];
//   if (!Array.isArray(skip))  skip  = [];

//   const servingRefOrder = document.getElementById('servingRefOrder');
//   const servingName     = document.getElementById('servingName');
//   servingRefOrder.innerText = queue[0]?.reference_number || '-';
//   servingName.innerText     = queue[0]?.name || '-';

//   queue.slice(1).forEach(waiting => {
//     document.getElementById('waitingRefOrder').innerText = waiting.reference_number || '-';
//     document.getElementById('waitingName').innerText     = waiting.name || '-';
//   });

//   skip.forEach(skipped => {
//     document.getElementById('skipRefOrder').innerText = skipped.reference_number || '-';
//     document.getElementById('skipName').innerText     = skipped.name || '-';
//   });
// }

//     function doneQueue(){

//     }
//     function skipQueue(){

//     }
//     function stopQueue(){
        

//     }
// document.addEventListener('DOMContentLoaded', displayQueue);