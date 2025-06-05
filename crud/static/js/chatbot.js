document.getElementById('chatToggle').addEventListener('click', function () {
    const popup = document.getElementById('chatPopup');
    popup.classList.toggle('hidden');
});

function sendQuery() {
    const input = document.getElementById('chatInput');
    const responseBox = document.getElementById('chatResponse');
    const query = input.value;

    if (!query.trim()) return;

    fetch(`/chatbot/query/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            responseBox.innerHTML += `<div class="mb-2">👩‍⚕️ ${data.response}</div>`;
            input.value = '';
            responseBox.scrollTop = responseBox.scrollHeight;
        });
}