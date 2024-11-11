document.addEventListener('DOMContentLoaded', () => {

    newPostButton();
    clickUserName();

    if (window.location.pathname === '/') {
        makePostIndex();
        likeButtonIndex();
        
    }

    const profileId = getProfileIdFromUrl();
    if (profileId) {
        profileInitialDisplay();
        editButtonProfile(); // adding description from user profile
        followButton(); // ongoing for backend and JS
    }

});



// --------------- common function ---------------

function getProfileIdFromUrl() { 
    const path = window.location.pathname; 
    const pathParts = path.split('/');
    const profileIndex = pathParts.indexOf('profile');

    if (profileIndex !== -1 && pathParts[profileIndex + 1]) {
        return pathParts[profileIndex + 1];
    } 
    return null;
}



function newPostButton(){
    if (window.location.pathname === '/') {
        const postButton = document.getElementById('new_post')
        postButton.addEventListener('click', () => {
            const postForm = document.getElementById('post_form');
            postForm.style.display = 'block';
            postButton.style.display = 'none';
        })
    }

    if (window.location.pathname === '/profile') {
        document.getElementById('new_post').style.display = 'none';
    }

}



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



// --------------- profile ---------------

function profileInitialDisplay() {
    const editProfile = document.querySelector('.edit_profile');
    const userProfile = document.querySelector('.user_profile');
    const newPostDiv = document.querySelector('.new_post_div');
    editProfile.style.display = 'none';
    newPostDiv.style.display = 'none';
    userProfile.style.display = 'block';
    
}


function editButtonProfile() {
    const editButton = document.querySelector('.edit-profile-btn')
    editButton.addEventListener('click', () => {
        document.querySelector('.edit_profile').style.display = 'block';
        document.querySelector('.user_profile').style.display = 'none';
        document.querySelector('.user_posts').style.display = 'none';
    })
}


///------------------------------on-going
function followButton() {
    const followButton = document.querySelector('.follow-btn');
    followButton.addEventListener('click', () => {
        const csrfTokenInput = document.querySelector('input[name="csrf_follow"]').value;
        const userId = followButton.getAttribute('data-user-id');

        fetch("/follow", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfTokenInput,
            },
            body: JSON.stringify({ user_id: userId })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Follow action completed:', data); 
            // Optionally, update the button text or state based on the response })
        })
        .catch(error => { console.error('Error:', error);
        })
    })
}

// ------------ clicking USER Name

function clickUserName() {
    document.querySelectorAll('.user_name').forEach(userName => {

        userName.addEventListener('mouseenter', () => { 
            userName.classList.add('pointer-cursor');
            userName.classList.add('hover-color');  
        });

        userName.addEventListener('mouseleave', () => { 
            userName.classList.remove('pointer-cursor'); 
            userName.classList.remove('hover-color');  
        });


        userName.addEventListener('click', () => {
            const userId = userName.getAttribute('data-user-id');
            if (userId) { 
                window.location.href = `/profile/${userId}/`; 
            } else { 
                console.error('User ID is null or undefined'); 
            }
        })
    })
}

