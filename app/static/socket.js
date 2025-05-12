document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM loaded, initializing socket...');
    
    const socket = io();

    socket.on('connect', () => {
        console.log('Socket connected successfully');
        const userInfo = document.getElementById('user-info');
        if (userInfo) {
            const userId = userInfo.dataset.userId;
            console.log('Joining room for user:', userId);
            socket.emit('join', { user_id: userId });
        } else {
            console.warn('No user info element found');
        }
    });

    socket.on('disconnect', () => {
        console.log('Socket disconnected');
    });

    socket.on('connect_error', (error) => {
        console.error('Socket connection error:', error);
    });

    // Handle all post-related notifications
    socket.on('action_post', (data) => {
        console.log('Received action_post:', data);

        const userInfo = document.getElementById('user-info');
        const currentUserId = userInfo?.dataset.userId;

        if (currentUserId === data.user_id) {
            console.log('Skipping notification for own action');
            return;
        }

        // Tùy loại thông báo
        let link = `/post/${data.post_id}`;
        let message = data.message;

        if (data.type === 'like-post') {
            message = data.message || 'Ai đó đã thích bài viết của bạn!';
        } else if (data.type === 'create-post') {
            message = data.message || 'Có bài viết mới!';
        }else if (data.type === 'comment-post') {
            message = data.message || 'Ai đó đã bình luận vào bài viết của bạn';
        } else {
            console.warn('Không rõ type:', data.type);
            return;
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-message">${message}</div>
                <a href="${link}" class="notification-link">Xem bài viết</a>
            </div>
        `;

        // Style
        const style = document.createElement('style');
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                padding: 15px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 1000;
                max-width: 300px;
                animation: slideIn 0.3s ease-out;
            }
            .notification-content {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            .notification-message {
                font-size: 14px;
                color: #333;
            }
            .notification-link {
                color: #2563eb;
                text-decoration: none;
                font-size: 12px;
            }
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                document.body.removeChild(notification);
                document.head.removeChild(style);
            }, 300);
        }, 5000);
    });
});
