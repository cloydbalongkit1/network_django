document.addEventListener('DOMContentLoaded', () => {
    newPostButton();
    clickUserName();

    if (window.location.pathname === '/') {
        makePostIndex();
        initializeLikeButtons(); // Initialize like buttons on static content
        likeButtonIndex(); // Set up event delegation for dynamic content
    }

    const profileId = getProfileIdFromUrl();
    if (profileId) {
        profileInitialDisplay();
        editButtonProfile();
        followButton(); 
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

function newPostButton() {
    if (window.location.pathname === '/') {
        const postButton = document.getElementById('new_post');
        postButton.addEventListener('click', () => {
            const postForm = document.getElementById('post_form');
            postForm.style.display = 'block';
            postButton.style.display = 'none';
        });
    }

    if (window.location.pathname === '/profile') {
        document.getElementById('new_post').style.display = 'none';
    }
}

// --------------- index ---------------
function makePostIndex() {
    const message = document.getElementById("post_form");
    const postButton = document.getElementById("new_post");
    message.style.display = 'none';
    postButton.style.display = 'block';
}

// Initialize static like buttons
function initializeLikeButtons() {
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', handleLikeClick);
    });
}

// Event delegation for dynamic like buttons
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
                // Check if #message container exists
                let messageDiv = document.getElementById('message');
                if (!messageDiv) {
                    // Create #message if it doesn't exist
                    messageDiv = document.createElement('div');
                    messageDiv.id = 'message';
                    messageDiv.className = 'container';
                    document.body.prepend(messageDiv); // Place at the top of the body, adjust as needed
                }

                if (data.success) {
                    // Update like count on success
                    const likeCount = button.querySelector('small');
                    likeCount.textContent = parseInt(likeCount.textContent) + 1;
                    messageDiv.innerHTML = ''; // Clear any previous messages on success
                } else {
                    // Display backend error message
                    messageDiv.innerHTML = `<div class="alert alert-danger" role="alert">${data.message}</div>`;
                }
            })
            .catch(error => {
                // Handle fetch error and display in #message
                let messageDiv = document.getElementById('message');
                if (!messageDiv) {
                    messageDiv = document.createElement('div');
                    messageDiv.id = 'message';
                    messageDiv.className = 'container';
                    document.body.prepend(messageDiv);
                }
                messageDiv.innerHTML = `<div class="alert alert-danger" role="alert">An error occurred. Please try again.</div>`;
                console.error('Error:', error);
            });
        });
    });
}


// Unified function to handle like button clicks
function handleLikeClick(event) {
    const button = event.currentTarget || event.target.closest('.like-button');
    if (!button) return;

    button.setAttribute('data-listened', 'true'); // Prevent duplicate listeners

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
            messageDiv.innerHTML = '';
        } else {
            messageDiv.innerHTML = `<div class="alert alert-danger" role="alert">${data.message}</div>`;
        }
    })
    .catch(error => {
        const messageDiv = document.getElementById('message');
        messageDiv.innerHTML = `<div class="alert alert-danger" role="alert">An error occurred. Please try again.</div>`;
        console.error('Error:', error);
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
    const editButton = document.querySelector('.edit-profile-btn');
    editButton.addEventListener('click', () => {
        document.querySelector('.edit_profile').style.display = 'block';
        document.querySelector('.user_profile').style.display = 'none';
        document.querySelector('.user_posts').style.display = 'none';
    });
}

// Follow button functionality
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
        })
        .catch(error => { console.error('Error:', error); });
    });
}

// Click user name functionality
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
            const csrfTokenInput = document.querySelector('input[name="csrf_token"]').value;
            const createdID = userName.getAttribute('data-user-id');
            const postID = userName.getAttribute('data-post-id');
            const currentUserId = document.getElementById('current_user_id').value; // assuming this field exists

            fetch(`view/post/${postID}/`, { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfTokenInput,
                },
                body: JSON.stringify({ 
                    user_id: createdID
                })
            })
            .then(response => response.json())
            .then(data => { 
                const newPostElement = document.createElement('div');
                newPostElement.className = 'p-3 border rounded bg-light';

                if (data.success) {
                    newPostElement.innerHTML = 
                        `<div class="post-header"> 
                            <h5>${data.post.created_by}</h5> 
                            <small class="text-muted">${new Date(data.post.date_created).toLocaleString()}</small> 
                        </div> 
                        <div class="post-body"> 
                            <p>${data.post.new_post}</p> 
                        </div> 
                        <div class="post-footer"> 
                            <button class="btn btn-outline-danger like-button" data-post-id="${data.post.id}"
                                ${data.post.created_by_id == currentUserId ? 'disabled' : ''}> 
                                ❤️ <small>${data.post.likes}</small> 
                            </button> 
                        </div>`;

                    document.querySelector('.body-container').style.display = 'none';
                    document.querySelector('.body').appendChild(newPostElement);
                    
                    initializeLikeButtons(); // Initialize like buttons on newly created content
                } else { 
                    const messageDiv = document.getElementById('message');
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






