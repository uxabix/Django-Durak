"""Accounts models for the Durak card game application.

This module contains all the Django models used in the account system for
the online multiplayer Durak card game.
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended User model for the Durak card game application.
    
    This model extends Django's AbstractUser to include additional fields
    specific to the game functionality such as avatar and creation timestamp.
    Uses UUID as primary key for better security and scalability.
    
    Attributes:
        id (UUIDField): Primary key using UUID4 instead of sequential integers.
        avatar_url (URLField, optional): URL to user's avatar image.
        created_at (DateTimeField): Timestamp when the account was created.
        
    Inherits from AbstractUser:
        username, email, password, first_name, last_name, is_active, 
        is_staff, is_superuser, date_joined, last_login
        
    Related Objects:
        sent_messages: Messages sent by this user (reverse FK from Message.sender)
        received_messages: Private messages received by this user (reverse FK from Message.receiver)
        owned_lobbies: Game lobbies created by this user (reverse FK from Lobby.owner)
        lobby_participations: Lobby memberships (reverse FK from LobbyPlayer.user)
        
    Example:
        # Create a new user
        user = User.objects.create_user(
            username='player1',
            email='player1@example.com',
            password='secure_password'
        )
        user.avatar_url = 'https://example.com/avatar.jpg'
        user.save()
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avatar_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return string representation of the user.
        
        Returns:
            str: The username of the user.
        """
        return self.username
    
    def get_full_display_name(self):
        """Get user's display name with fallback to username.
        
        Returns:
            str: Full name if available, otherwise username.
        """
        full_name = self.get_full_name()
        return full_name if full_name else self.username
    
    def has_avatar(self):
        """Check if user has an avatar set.
        
        Returns:
            bool: True if avatar_url is set, False otherwise.
        """
        return bool(self.avatar_url)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']
