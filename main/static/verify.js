window.addEventListener("DOMContentLoaded", () => {
    document.getElementById('code-form').addEventListener('submit', function(e) {
        e.preventDefault();
        verifyCode();
    });

    document.getElementById('phone-form').addEventListener('submit', function(e) {
        e.preventDefault();
        verifyCode();
    });
});


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function verifyCode() {
    csrftoken = getCookie('csrftoken');
    code = document.getElementById('code').value.trim();
    fetch('/main/verify/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            has_code: 'true',
            code: code
        })
    })
    .then(response => response.json())
    .then(data => {
        // Handle success
        console.log(data)
        if (data.success) {
            window.location.href = data.url;
            console.log("huh");
        } else {
            alert("Not valid code!");
        }
    })
    .catch(error => {
        // Handle error
        console.log("ERR: " + error)
    });
    
}