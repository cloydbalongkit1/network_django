document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname === '/') {
        makePostIndex();
        likeButtonIndex();
        newPostButtonIndex();
    }


    if (window.location.pathname === '/profile'){
        profileInitialDisplay();
    }


});


// --------------- index ---------------

function makePostIndex() {
    const message = document.getElementById("post_form")
    const postButton = document.getElementById("new_post")
    message.style.display = 'none'
    postButton.style.display = 'block'
}


function likeButtonIndex() {
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
                const messageDiv = document.getElementById('message');
                if (data.success) {
                    const likeCount = button.querySelector('small');
                    likeCount.textContent = parseInt(likeCount.textContent) + 1;
                } else {
                    messageDiv.innerHTML = `<div class="alert alert-danger" role="alert">${data.message}</div>`;
                }
            })
            .catch(error => {
                const messageDiv = document.getElementById('message');
                messageDiv.innerHTML = `<div class="alert alert-danger" role="alert">An error occurred. Please try again.</div>`;
                console.error('Error:', error);
            });
        });
    });
}


function newPostButtonIndex(){
    const postButton = document.getElementById('new_post')
    postButton.addEventListener('click', () => {
        const postForm = document.getElementById('post_form');
        postForm.style.display = 'block';
        postButton.style.display = 'none';
    })
}


// --------------- profile ---------------

function profileInitialDisplay() {
    const editProfile = document.querySelector('.edit_profile');
    const userProfile = document.querySelector('.user_profile');
    editProfile.style.display = 'none';
    userProfile.style.display = 'block';
}

