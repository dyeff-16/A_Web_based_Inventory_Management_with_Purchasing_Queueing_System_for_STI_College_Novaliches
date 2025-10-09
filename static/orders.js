 function showUploadModal(index) {
  const fileInput = document.getElementById('fileInput' + index);
  const file = fileInput.files[0];
  const preview = document.getElementById('previewImage' + index);

  if (!file) {
    alert('Please select a file first.');
    return;
  }

  // Show preview
  const reader = new FileReader();
  reader.onload = function(e) {
    preview.src = e.target.result;
    preview.style.display = 'block';
  }
  reader.readAsDataURL(file);

  // Show confirmation modal
  const modal = new bootstrap.Modal(document.getElementById('confirmUploadModal' + index));
  modal.show();
}

function confirmYes(index) {
  const form = document.getElementById('uploadForm' + index);
  form.submit();

  // Hide modal
  const modalEl = document.getElementById('confirmUploadModal' + index);
  const modal = bootstrap.Modal.getInstance(modalEl);
  if (modal) modal.hide();
}

function getImageItem(item_id){
    fetch('/purchase/getImageItem', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({item_id: item_id})
    })
    .then(r => r.json())
    .then(data => {
        const imageElement = document.getElementById('item-image-' + item_id);
        
        if (imageElement && data.imageBase64) {
            imageElement.src = `data:image/jpeg;base64,${data.imageBase64}`;
            console.log(`Image for item ${item_id} loaded successfully.`);
        }
    })
    .catch(error => {
        console.error('Error loading image:', error);
    });
}

    function setStatus(ref_num){
        fetch('/purchase/setClaim', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ref_num: ref_num})
        })
        .then(r => r.json())
        .then(data => {
            console.log(data.message)
            if(data.redirect_url){
              window.location.href = data.redirect_url;
            }
        })
    }