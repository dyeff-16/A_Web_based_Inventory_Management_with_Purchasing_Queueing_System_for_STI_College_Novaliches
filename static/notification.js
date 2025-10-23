function setNotify() {
    const dot = document.getElementById('notifDot');
    if (!dot) return;

    fetch('/notification/getNotif')
        .then(r => r.json())
        .then(data => {
            const on = data && data.notif === true;
            dot.classList.toggle('d-none', !on);
        });
}
setNotify();
setInterval(setNotify, 5000);