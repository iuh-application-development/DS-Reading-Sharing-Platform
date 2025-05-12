document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    
    // Kiểm tra kết nối
    socket.on('connect', () => {
        console.log('Connected to socket server');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from socket server');
    });

    socket.on('connect_error', (error) => {
        console.error('Socket connection error:', error);
    });

    // Test event
    socket.emit('join', { user_id: 'test_user' });
    
    // Listen for new post notifications
    socket.on('new_post', function(data) {
        console.log('Received new post notification:', data);
    });
}); 