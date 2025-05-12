from flask_socketio import join_room
from flask_login import current_user
from flask import request
from app import socketio
import logging

logger = logging.getLogger(__name__)

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    if current_user.is_authenticated:
        logger.info(f"Authenticated user connected: {current_user.id}")

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")
    if current_user.is_authenticated:
        logger.info(f"Authenticated user disconnected: {current_user.id}")

@socketio.on('join')
def handle_join(data):
    user_id = data.get('user_id')
    if user_id:
        room = f"user_{user_id}"
        logger.info(f"User {user_id} joining room: {room}")
        join_room(room)
        logger.info(f"User {user_id} successfully joined room: {room}")
    else:
        logger.error("Join event received without user_id")

@socketio.on_error()
def error_handler(e):
    logger.error(f"Socket error: {str(e)}")
    if current_user.is_authenticated:
        logger.error(f"Error occurred for user: {current_user.id}")
