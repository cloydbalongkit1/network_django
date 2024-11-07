document.addEventListener('DOMContentLoaded', () => {
    
    likeButton()

})


function likeButton() {
    document.querySelectorAll('.like_button').forEach(button => {
        button.addEventListener('click', () => {
            const postId = button.getAttribute('data-post-id');
            const csrfToken = document.querySelector('input[name="csrf_token"]').value;
    
            fetch("/liked", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ post_id: postId })
            })
            .then(response => response.json())
            .then(data => {
                const messageDiv = document.getElementById('#message')
                if (data.success) {
                    const likeCount = button.querySelector('small');
                    likeCount.textContent = parseInt(likeCount.textContent) + 1;
                } else { 
                    messageDiv.innerHTML = `<div class="alert alert-danger" role="alert">${data.message}</div>`;
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
}


