document.addEventListener('DOMContentLoaded', () => {
    
    clickPost();
    likeButtonIndex();
    makePostIndex();
    newPostButton();
    initializeLikeButtons();
    editPost();
    postComment();
    collapseComments()

    const profileId = getProfileIdFromUrl();
    if (profileId) {
        profileInitialDisplay();
        editButtonProfile();
        followButton(); 
    }
});



function editPost() {
    document.querySelectorAll('.edit_post').forEach(editButton => {
        editButton.addEventListener('click', () => {
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const editId = editButton.getAttribute('data-edit-id');

            fetch(`/edit/posts/${editId}`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.text())
            .then(data => {
                document.body.innerHTML = data; 
                const saveButton = document.getElementById('submitEdit');

                saveButton.addEventListener('click', () => {
                    const content = document.getElementById('editContent').value;

                    fetch(`/edit/posts/${editId}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({ editPost: content })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            alert('Post updated successfully!');
                            window.location.reload();
                        } else {
                            alert(data.message);
                        }
                    });
                });
            });
        });
    });
}


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



function toTitleCase(str) {
    return str.replace(/\b\w/g, char => char.toUpperCase());
}



function newPostButton() {
    if (window.location.pathname === '/profile') {
        document.getElementById('new_post').style.display = 'none';
    } else {
        const postButton = document.getElementById('new_post');
        postButton.addEventListener('click', () => {
            const postForm = document.getElementById('post_form');
            postForm.style.display = 'block';
            postButton.style.display = 'none';
        });
    }
}



function makePostIndex() {
    const message = document.getElementById("post_form");
    const postButton = document.getElementById("new_post");
    message.style.display = 'none';
    postButton.style.display = 'block';
}



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



function clickPost() {
    document.querySelectorAll('.user_name').forEach(userName => {
        cursorGraphics(userName);

        userName.addEventListener('click', () => { 
            const csrfTokenInput = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const createdID = userName.getAttribute('data-user-id');
            const postID = userName.getAttribute('data-post-id');
            const currentUserId = document.getElementById('current_user_id').value; // assuming this field exists

            fetch(`/view/post/${postID}/`, { 
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
                newPostElement.className = 'p-3 border rounded bg-light each-post';

                if (data.success) {
                    newPostElement.innerHTML = 
                        `<div class="post-header"> 
                            <input type="hidden" name="csrf_profile_view" value="${ csrfTokenInput }" >
                            <h5 id="viewing-profile" data-user-id="${ data.post.created_by_id}" >
                                ${toTitleCase(data.post.created_by)}
                            </h5> 
                            <small class="text-muted">${new Date(data.post.date_created).toLocaleString()}</small> 
                        </div> 
                        <div class="post-body"> 
                            <p>${data.post.new_post}</p> 
                        </div> 
                        <div class="post-footer"> 
                            <button class="btn btn-outline-danger like-button" data-post-id="${data.post.id}"
                                ${data.post.created_by_id == currentUserId ? 'hidden' : ''}> 
                                ❤️ <small>${data.post.likes}</small> 
                            </button> 
                        </div>`;

                    document.querySelector('.body-container').style.display = 'none';
                    document.querySelector('.body').appendChild(newPostElement);
                    
                    initializeLikeButtons();
                    viewProfile();

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



function cursorGraphics(element) {
    element.addEventListener('mouseenter', () => { 
        element.classList.add('pointer-cursor');
        element.classList.add('hover-color');  
    });

    element.addEventListener('mouseleave', () => { 
        element.classList.remove('pointer-cursor'); 
        element.classList.remove('hover-color');  
    });
}



// clicking the profile name and rendering the profile page using JS -------------------------------------------------------------------
function viewProfile(page=1) {
    const profileName = document.getElementById('viewing-profile');
    cursorGraphics(profileName);

    profileName.addEventListener("click", () => {
        const userID = profileName.getAttribute('data-user-id');
        const csrfTokenInput = document.querySelector('input[name="csrf_profile_view"]').value;

        fetch(`/view/profile/${userID}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfTokenInput,
            }
        })
        .then(response => response.json())
        .then(data => {

            if (data.success) {
                const viewedUser = data.profile;
                const viewProfile = document.createElement('div');

                viewProfile.innerHTML = `
                    <div class="user_profile container">
                        <div class="profile-header">
                            <img src="${viewedUser.profile_picture_url || '/static/network/images/sample.jpg'}" alt="Profile Picture" class="profile-picture">
                        </div>
                        <div class="profile-info p-3 bg-light">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h3>${toTitleCase(viewedUser.first_name)} ${toTitleCase(viewedUser.last_name)}</h3>
                                    <p class="text-muted">@${viewedUser.username}</p>
                                </div>
                                <input type="hidden" name="csrf_follow" value="{{ csrf_token }}">
                                <button class="btn btn-primary follow-btn" 
                                    data-viewedUser-id="${viewedUser.id}"
                                    data-loggedUser-id="${data.logged_in_user_id}" 
                                    ${data.logged_in_user_id === viewedUser.id ? 'hidden' : ''}>
                                        ${viewedUser.is_following ? 'Unfollow' : 'Follow'}
                                </button>
                            </div>
                            <hr>
                            <div class="bio-details">
                                <p><strong>Bio:</strong> ${viewedUser.bio || 'No bio provided'}</p>
                            </div>
                            <div class="profile-details">
                                <p><strong>Work:</strong> ${viewedUser.work || 'Not specified'}</p>
                                <p><strong>Location:</strong> ${viewedUser.location || 'Not specified'}</p>
                                <p><strong>Joined:</strong> ${new Date(viewedUser.date_joined).toLocaleString('default', { month: 'long', year: 'numeric' })}</p>
                            </div>
                            <div class="profile-stats">
                                <p><strong class="following-count">${viewedUser.following}</strong> Following</p>
                                <p><strong class="followers-count" >${viewedUser.followers}</strong> Followers</p>
                            </div>
                        </div>
                        <div class="mt-3 p-3 border rounded bg-light user_posts">
                            <ul class="list-group">
                                ${viewedUser.posts.map(post => `
                                    <li class="list-group-item mb-3">
                                        <div class="d-flex justify-content-between align-items-center">
                                            <div>
                                                <h5 class="user_name mb-1" data-user-id="${post.created_by.id}" data-login-user="${viewedUser.id}">
                                                    ${toTitleCase(post.created_by)}
                                                </h5>
                                                <p class="mb-1">${post.new_post}</p>
                                                <small class="text-muted">Date Created: ${new Date(post.date_created).toLocaleString()}</small>
                                            </div>                   
                                        </div>
                                    </li>
                                `).join('')}
                            </ul>
                        </div>

                        <nav aria-label="Page navigation">
                            <ul class="pagination justify-content-center mt-3">
                                ${data.profile.has_previous ? `
                                    <li class="page-item">
                                        <a class="page-link" href="#" onclick="viewProfile(${data.profile.page_number - 1})">Previous</a>
                                    </li>
                                ` : `
                                    <li class="page-item disabled"><a class="page-link">Previous</a></li>
                                `}
                                ${Array.from({ length: data.profile.total_pages }, (_, i) => `
                                    <li class="page-item ${data.profile.page_number === i + 1 ? 'active' : ''}">
                                        <a class="page-link" href="#" onclick="viewProfile(${i + 1})">${i + 1}</a>
                                    </li>
                                `).join('')}
                                ${data.profile.has_next ? `
                                    <li class="page-item">
                                        <a class="page-link" href="#" onclick="viewProfile(${data.profile.page_number + 1})">Next</a>
                                    </li>
                                ` : `
                                    <li class="page-item disabled"><a class="page-link">Next</a></li>
                                `}
                            </ul>
                        </nav>
                    </div>
                `;

                document.querySelector('.each-post').style.display = 'none';
                document.querySelector('.body').appendChild(viewProfile);

                followButton("follow-btn");

            } else {
                console.error('Failed to fetch profile data:', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    })
}



function followButton(className) {
    const csrfTokenInput = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const button = document.querySelector(`.${className}`)

    if (button) {
        button.addEventListener('click', () => {
            const viewedUser = button.getAttribute('data-viewedUser-id');
            const action = button.innerText === "Follow" ? "follow" : "unfollow";

            fetch("/follow", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfTokenInput,
                },
                body: JSON.stringify({ 
                    viewed_user: viewedUser,
                    action: action,
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    button.innerText = action === "follow" ? "Unfollow" : "Follow";
                    const followersCountElem = document.querySelector('.followers-count');
                    let followersCount = parseInt(followersCountElem.innerText);
                    followersCountElem.innerText = action === "follow" ? followersCount + 1 : followersCount - 1;
                }
            })
            .catch(error => { console.error('Error:', error); });
        })
    }
}



function postComment() {
    document.querySelectorAll('.post_comment').forEach(button => {
        button.addEventListener('click', () => {
            const postId = button.getAttribute('data-post-id');
            const textarea = document.getElementById(`commentInput${postId}`);
            const commentText = textarea.value.trim();
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
            if (!commentText) {
                alert('Comment cannot be empty.');
                return;
            }
    
            fetch(`/post/comments/${postId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ comment: commentText })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const commentList = document.getElementById(`commentList${postId}`);
                    const newComment = document.createElement('li');
                    newComment.classList.add('list-group-item', 'border', 'rounded-3', 'ps-4', 'mb-2');
                    newComment.innerHTML = `
                        <div class="d-flex justify-content-between">
                            <strong>${data.comment.commented_by}</strong>
                            <small class="text-muted">${data.comment.commented_date}</small>
                        </div>
                        <p class="mb-1">${data.comment.comment}</p>
                    `;
                    commentList.appendChild(newComment);
                    textarea.value = '';

                    const commentCountElement = document.querySelector(`.view-comments[data-post-id="${postId}"] small`);
                    const currentCount = parseInt(commentCountElement.textContent.match(/\d+/) || 0);
                    commentCountElement.textContent = `View Comments (${currentCount + 1})`;

                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        });
    });
}



function collapseComments() {
    document.querySelectorAll('.view-comments').forEach(link => {
        link.addEventListener('click', () => {
            const postId = link.getAttribute('data-post-id');
            const commentsDiv = document.getElementById(`collapseComments${postId}`);

            if (commentsDiv) {
                commentsDiv.classList.toggle('collapse');
            }
        });
    });
}    
    
