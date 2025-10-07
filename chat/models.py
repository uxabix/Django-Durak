"""Chat models for the Durak card game application.

This module contains all the Django models used in the chat system for
the online multiplayer Durak card game.
"""

import uuid
from django.db import models


class Message(models.Model):
    """Chat message model for storing messages in lobbies and private conversations.
    
    This model handles both lobby-based group messages and private direct messages
    between users. Messages can be associated with either a lobby (for public chat)
    or a receiver (for private messaging).
    
    Attributes:
        id (UUIDField): Primary key using UUID4 for unique message identification.
        sender (ForeignKey): Reference to the User who sent the message.
        receiver (ForeignKey, optional): Target User for private messages. Null for lobby messages.
        lobby (ForeignKey, optional): Target Lobby for group messages. Null for private messages.
        content (TextField): The actual message content/text.
        sent_at (DateTimeField): Timestamp when the message was created (auto-generated).
        
    Note:
        Either 'receiver' or 'lobby' should be set, but not both. This creates a logical
        separation between private messages and lobby-based group chat.
        
    Example:
        # Create a lobby message
        Message.objects.create(
            sender=user,
            lobby=lobby,
            content="Hello everyone!"
        )
        
        # Create a private message
        Message.objects.create(
            sender=user1,
            receiver=user2,
            content="Private message"
        )
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='received_messages')
    lobby = models.ForeignKey('game.Lobby', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return string representation of the message.
        
        Returns:
            str: Formatted string showing sender and message preview.
        """
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.sender.username}: {preview}"
    
    def is_private(self):
        """Check if this is a private message between users.
        
        Returns:
            bool: True if message has a receiver (private), False if lobby message.
        """
        return self.receiver is not None
    
    def is_lobby_message(self):
        """Check if this is a lobby/group message.
        
        Returns:
            bool: True if message belongs to a lobby, False if private message.
        """
        return self.lobby is not None
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
