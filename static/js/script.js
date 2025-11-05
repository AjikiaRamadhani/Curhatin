// Theme Toggle
const themeToggle = document.getElementById('theme-toggle');
if (themeToggle) {
    const themeIcon = themeToggle.querySelector('i');
    
    // Check for saved theme or prefer color scheme
    const savedTheme = localStorage.getItem('theme') || 
                      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
    
    function updateThemeIcon(theme) {
        themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// Dropdown functionality - FIXED VERSION
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 JavaScript loaded - setting up dropdowns');
    
    const dropdowns = document.querySelectorAll('.nav-dropdown');
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        console.log('📝 Document clicked');
        let clickedInsideDropdown = false;
        
        dropdowns.forEach(dropdown => {
            if (dropdown.contains(e.target)) {
                clickedInsideDropdown = true;
            }
        });
        
        if (!clickedInsideDropdown) {
            console.log('🚪 Closing all dropdowns');
            dropdowns.forEach(dropdown => {
                const dropdownContent = dropdown.querySelector('.nav-dropdown-content');
                if (dropdownContent) {
                    dropdownContent.classList.remove('show');
                }
            });
        }
    });

    // Toggle dropdown on button click
    dropdowns.forEach(dropdown => {
        const button = dropdown.querySelector('.nav-dropdown-btn');
        const content = dropdown.querySelector('.nav-dropdown-content');
        
        if (button && content) {
            console.log('🎯 Setting up dropdown button');
            
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('🔼 Dropdown button clicked');
                
                // Close all other dropdowns
                dropdowns.forEach(otherDropdown => {
                    if (otherDropdown !== dropdown) {
                        const otherContent = otherDropdown.querySelector('.nav-dropdown-content');
                        if (otherContent) {
                            otherContent.classList.remove('show');
                        }
                    }
                });
                
                // Toggle current dropdown
                content.classList.toggle('show');
                console.log('📋 Dropdown visibility:', content.classList.contains('show'));
            });
            
            // Prevent dropdown content clicks from closing dropdown
            content.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
    });
    
    // Category Tabs Functionality
    const categoryTabs = document.querySelectorAll('.category-tab');
    const storyCategories = document.querySelectorAll('.stories-category');
    
    categoryTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const category = this.dataset.category;
            console.log('📂 Switching to category:', category);
            
            // Update active tab
            categoryTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Show corresponding category
            storyCategories.forEach(cat => {
                cat.classList.remove('active');
                if (cat.id === `${category}-stories`) {
                    cat.classList.add('active');
                }
            });
        });
    });
});

// Like Story Functionality
function likeStory(storyId, button) {
    if (!button) {
        console.error('Button element not found');
        return;
    }
    
    console.log('❤️ Liking story:', storyId);
    
    fetch(`/like_story/${storyId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.liked) {
            button.classList.add('liked');
            button.querySelector('.fa-heart').classList.add('fas');
            button.querySelector('.fa-heart').classList.remove('far');
        } else {
            button.classList.remove('liked');
            button.querySelector('.fa-heart').classList.remove('fas');
            button.querySelector('.fa-heart').classList.add('far');
        }
        button.querySelector('.like-count').textContent = data.like_count;
    })
    .catch(error => {
        console.error('Error:', error);
        showFlashMessage('Terjadi kesalahan saat menyukai curhatan', 'error');
    });
}

function likeComment(commentId, button) {
    if (!button) {
        console.error('Button element not found');
        return;
    }
    
    console.log('❤️ Liking comment:', commentId);
    
    fetch(`/like_comment/${commentId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.liked) {
            button.classList.add('liked');
            button.querySelector('.fa-heart').classList.add('fas');
            button.querySelector('.fa-heart').classList.remove('far');
        } else {
            button.classList.remove('liked');
            button.querySelector('.fa-heart').classList.remove('fas');
            button.querySelector('.fa-heart').classList.add('far');
        }
        button.querySelector('.like-count').textContent = data.like_count;
    })
    .catch(error => {
        console.error('Error:', error);
        showFlashMessage('Terjadi kesalahan saat menyukai komentar', 'error');
    });
}

// Reply Form Functions
function showReplyForm(commentId) {
    const replyForm = document.getElementById(`reply-form-${commentId}`);
    if (replyForm) {
        replyForm.style.display = 'block';
        replyForm.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        replyForm.querySelector('textarea').focus();
    }
}

function hideReplyForm(commentId) {
    const replyForm = document.getElementById(`reply-form-${commentId}`);
    if (replyForm) {
        replyForm.style.display = 'none';
        replyForm.querySelector('textarea').value = '';
    }
}

// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateX(100%)';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
    // Mobile Search Toggle
const mobileSearchToggle = document.querySelector('.mobile-search-toggle');
const mobileSearchForm = document.querySelector('.mobile-search-form');

if (mobileSearchToggle && mobileSearchForm) {
    mobileSearchToggle.addEventListener('click', function() {
        mobileSearchForm.classList.toggle('active');
        if (mobileSearchForm.classList.contains('active')) {
            mobileSearchForm.querySelector('input').focus();
        }
    });
    
    // Close mobile search when clicking outside
    document.addEventListener('click', function(e) {
        if (!mobileSearchToggle.contains(e.target) && !mobileSearchForm.contains(e.target)) {
            mobileSearchForm.classList.remove('active');
        }
    });
}

// Search input auto-focus
const searchInput = document.querySelector('.search-input');
if (searchInput && !searchInput.value) {
    searchInput.focus();
}
});

// Utility function to show flash messages
function showFlashMessage(message, type = 'info') {
    let flashContainer = document.querySelector('.flash-messages');
    if (!flashContainer) {
        // Create flash container if it doesn't exist
        flashContainer = document.createElement('div');
        flashContainer.className = 'flash-messages';
        document.querySelector('.main-content').prepend(flashContainer);
    }
    
    const flashMessage = document.createElement('div');
    flashMessage.className = `flash-message ${type}`;
    flashMessage.innerHTML = `
        ${message}
        <button class="flash-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    flashContainer.appendChild(flashMessage);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (flashMessage.parentElement) {
            flashMessage.style.opacity = '0';
            flashMessage.style.transform = 'translateX(100%)';
            setTimeout(() => flashMessage.remove(), 300);
        }
    }, 5000);
}

// Di script.js
let page = 1;
let loading = false;

window.addEventListener('scroll', function() {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500 && !loading) {
        loadMoreStories();
    }
});

// Smooth scroll to top when paginating
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Add scroll to top for pagination links
document.addEventListener('DOMContentLoaded', function() {
    const paginationLinks = document.querySelectorAll('.pagination-btn:not(.disabled), .pagination-page:not(.active)');
    
    paginationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Only scroll if it's not a disabled link
            if (!this.classList.contains('disabled')) {
                setTimeout(scrollToTop, 100);
            }
        });
    });
    
    // Existing dropdown and category code...
});

// Relative time function
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'baru saja';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} menit lalu`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} jam lalu`;
    } else if (diffInSeconds < 2592000) {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days} hari lalu`;
    } else {
        // Return formatted date for older posts
        return date.toLocaleDateString('id-ID', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
    }
}

// Update all timestamps on page load
document.addEventListener('DOMContentLoaded', function() {
    // You can optionally use this to show relative time
    const timeElements = document.querySelectorAll('.story-time, .comment-time');
    
    timeElements.forEach(element => {
        const originalTime = element.getAttribute('title') || element.textContent;
        // Uncomment below if you want relative time instead of absolute time
        // element.textContent = formatRelativeTime(originalTime);
    });
    
    // ... existing code ...
});

// // Infinite Scroll Functionality
// let currentPage = 1;
// let isLoading = false;
// let currentCategory = 'latest';

// function initInfiniteScroll() {
//     window.addEventListener('scroll', function() {
//         if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000 && !isLoading) {
//             loadMoreStories();
//         }
//     });
// }

async function loadMoreStories() {
    if (isLoading) return;
    
    isLoading = true;
    currentPage++;
    
    // Show loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memuat cerita lainnya...';
    document.querySelector('.stories-container-grid').appendChild(loadingIndicator);
    
    try {
        const response = await fetch(`/api/stories?page=${currentPage}&category=${currentCategory}`);
        const data = await response.json();
        
        if (data.stories && data.stories.length > 0) {
            // Remove loading indicator
            loadingIndicator.remove();
            
            // Append new stories
            data.stories.forEach(story => {
                const storyElement = createStoryElement(story);
                document.querySelector('.stories-container-grid').appendChild(storyElement);
            });
            
            // Update state
            if (!data.has_next) {
                // Remove scroll listener if no more stories
                window.removeEventListener('scroll', loadMoreStories);
                
                // Show end message
                const endMessage = document.createElement('div');
                endMessage.className = 'end-message';
                endMessage.innerHTML = '<p>🎉 Anda telah melihat semua cerita!</p>';
                document.querySelector('.stories-container-grid').appendChild(endMessage);
            }
        } else {
            loadingIndicator.remove();
        }
    } catch (error) {
        console.error('Error loading more stories:', error);
        loadingIndicator.remove();
    }
    
    isLoading = false;
}

function createStoryElement(story) {
    const storyDiv = document.createElement('div');
    storyDiv.className = 'story-card';
    storyDiv.id = `story-${story.id}`;
    
    // ✅ PERBAIKI: Handle image URL dengan benar
    const imageHtml = story.image_url ? 
        `<div class="story-image">
            <img src="${story.image_url}" alt="Story image" loading="lazy" onerror="this.style.display='none'">
        </div>` : '';
    
    const deleteHtml = story.can_delete ? 
        `<form action="/delete_story/${story.id}" method="POST" class="delete-form">
            <button type="submit" class="btn-delete" onclick="return confirm('Hapus curhatan ini?')">
                <i class="fas fa-trash"></i>
            </button>
        </form>` : '';
    
    const likeButtonHtml = currentUserIsAuthenticated ? 
        `<button class="btn-like ${story.user_has_liked ? 'liked' : ''}" 
                onclick="likeStory(${story.id}, this)">
            <i class="fas fa-heart"></i>
            <span class="like-count">${story.like_count}</span>
        </button>` :
        `<button class="btn-like" onclick="window.location.href='/login'">
            <i class="fas fa-heart"></i>
            <span class="like-count">${story.like_count}</span>
        </button>`;
    
    storyDiv.innerHTML = `
        <div class="story-header">
            <div class="story-author">
                <span class="author-name">${story.author_name}</span>
                <span class="story-time">${story.created_at}</span>
            </div>
            ${deleteHtml}
        </div>
        
        ${imageHtml}
        
        <div class="story-content">
            ${story.content}
        </div>
        
        <div class="story-actions">
            <div class="action-group">
                ${likeButtonHtml}
                <a href="/story/${story.id}" class="btn-comment">
                    <i class="fas fa-comment"></i>
                    <span class="comment-count">${story.comment_count}</span>
                </a>
            </div>
        </div>
    `;
    
    return storyDiv;
}

// Update category tab switching
document.addEventListener('DOMContentLoaded', function() {
    initInfiniteScroll();
    
    const categoryTabs = document.querySelectorAll('.category-tab');
    categoryTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const category = this.dataset.category;
            currentCategory = category;
            currentPage = 1;
            
            // Clear existing stories
            document.querySelector('.stories-container-grid').innerHTML = '';
            
            // Load first page of new category
            loadMoreStories();
        });
    });
});

// Debug function to check if JavaScript is working
console.log('✅ script.js loaded successfully');