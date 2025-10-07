"""Game models for the Durak card game application.

This module contains all the Django models that define the game logic,
lobby management, card representations, and player interactions for
the online multiplayer Durak card game.
"""

import uuid
from django.db import models


class CardSuit(models.Model):
    """Card suit model representing playing card suits (Hearts, Diamonds, etc.).
    
    Defines the four traditional card suits with their display names and colors.
    Used as a lookup table for card generation and game logic.
    
    Attributes:
        id (SmallAutoField): Primary key with small integer for efficiency.
        name (CharField): Display name of the suit (e.g., "Hearts", "Spades").
        color (CharField): Color of the suit, either "red" or "black".
        
    Color Choices:
        - 'red': For Hearts and Diamonds
        - 'black': For Clubs and Spades
        
    Example:
        # Create a heart suit
        hearts = CardSuit.objects.create(
            name="Hearts", 
            color="red"
        )
    """
    
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=20)
    color = models.CharField(max_length=5, choices=[('red', 'Red'), ('black', 'Black')])

    def __str__(self):
        """Return string representation of the card suit.
        
        Returns:
            str: The name of the suit.
        """
        return self.name

    def is_red(self):
        """Check if the suit is red (Hearts or Diamonds).
        
        Returns:
            bool: True if the suit is red, False otherwise.
        """
        return self.color == 'red'

    class Meta:
        verbose_name = 'Card Suit'
        verbose_name_plural = 'Card Suits'
        ordering = ['name']


class CardRank(models.Model):
    """Card rank model representing playing card values (Ace, King, etc.).
    
    Defines the ranks/values of playing cards with their display names
    and numeric values for comparison during gameplay.
    
    Attributes:
        id (SmallAutoField): Primary key with small integer for efficiency.
        name (CharField): Display name of the rank (e.g., "Ace", "King").
        value (IntegerField): Numeric value used for card comparison and game logic.
        
    Example:
        # Create an Ace card rank
        ace = CardRank.objects.create(
            name="Ace", 
            value=14  # Highest value in most variations
        )
    """
    
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=20)
    value = models.IntegerField()

    def __str__(self):
        """Return string representation of the card rank.
        
        Returns:
            str: The name of the rank.
        """
        return self.name

    def is_face_card(self):
        """Check if this is a face card (Jack, Queen, King).
        
        Returns:
            bool: True if value indicates a face card (typically 11-13).
        """
        return 11 <= self.value <= 13

    class Meta:
        verbose_name = 'Card Rank'
        verbose_name_plural = 'Card Ranks'
        ordering = ['value']


class Lobby(models.Model):
    """Game lobby model for organizing players before starting games.
    
    Represents a game room where players can gather, chat, and prepare
    to start a Durak game session. Handles lobby ownership, privacy
    settings, and player management.
    
    Attributes:
        id (UUIDField): Unique identifier for the lobby.
        owner (ForeignKey): Reference to the User who created the lobby.
        name (CharField): Display name of the lobby.
        is_private (BooleanField): Whether the lobby requires a password to join.
        password_hash (CharField, optional): Hashed password for private lobbies.
        status (CharField): Current lobby state.
        created_at (DateTimeField): When the lobby was created.
        
    Related Objects:
        settings: LobbySettings object with game configuration (OneToOne).
        players: LobbyPlayer objects representing users in this lobby.
        games: Game objects that have been played in this lobby.
        messages: Chat messages sent in this lobby.
        
    Status Choices:
        - 'waiting': Lobby is open and waiting for players
        - 'playing': Game is currently in progress
        - 'closed': Lobby has been closed and is no longer accessible
        
    Example:
        # Create a public lobby
        lobby = Lobby.objects.create(
            owner=user,
            name="Beginner's Game",
            is_private=False,
            status='waiting'
        )
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_private = models.BooleanField(default=False)
    password_hash = models.CharField(max_length=128, null=True, blank=True)
    status = models.CharField(max_length=10,
                              choices=[('waiting', 'Waiting'), ('playing', 'Playing'), ('closed', 'Closed')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return string representation of the lobby.
        
        Returns:
            str: The name of the lobby.
        """
        return self.name

    def is_full(self):
        """Check if the lobby has reached its maximum player capacity.
        
        Returns:
            bool: True if lobby is at max capacity, False otherwise.
        """
        current_players = self.players.filter(status__in=['waiting', 'ready', 'playing']).count()
        return current_players >= self.settings.max_players

    def can_start_game(self):
        """Check if the lobby has enough ready players to start a game.
        
        Returns:
            bool: True if there are at least 2 ready players and lobby is waiting.
        """
        if self.status != 'waiting':
            return False
        ready_players = self.players.filter(status='ready').count()
        return ready_players >= 2

    def get_active_players(self):
        """Get all active players in the lobby.
        
        Returns:
            QuerySet: LobbyPlayer objects with active status.
        """
        return self.players.filter(status__in=['waiting', 'ready', 'playing'])

    class Meta:
        verbose_name = 'Lobby'
        verbose_name_plural = 'Lobbies'
        ordering = ['-created_at']


class LobbySettings(models.Model):
    """Configuration settings for a game lobby.
    
    Defines the rules and parameters that will be applied to games
    started within the associated lobby. Each lobby has exactly one
    settings configuration.
    
    Attributes:
        id (UUIDField): Unique identifier for the settings.
        lobby (OneToOneField): Reference to the associated Lobby.
        max_players (PositiveIntegerField): Maximum number of players allowed.
        card_count (IntegerField): Number of cards to use in the deck.
        is_transferable (BooleanField): Whether cards can be transferred between players.
        neighbor_throw_only (BooleanField): Whether only neighbors can throw in additional cards.
        allow_jokers (BooleanField): Whether joker cards are included in the deck.
        turn_time_limit (IntegerField, optional): Time limit per turn in seconds.
        special_rule_set (ForeignKey, optional): Reference to a special rule configuration.
        
    Card Count Choices:
        - 24: Short deck (9, 10, J, Q, K, A of each suit)
        - 36: Standard deck (6, 7, 8, 9, 10, J, Q, K, A of each suit)
        - 52: Full deck (all cards including 2-5)
        
    Example:
        # Create standard game settings
        settings = LobbySettings.objects.create(
            lobby=lobby,
            max_players=4,
            card_count=36,
            is_transferable=True,
            neighbor_throw_only=False,
            allow_jokers=False
        )
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lobby = models.OneToOneField(Lobby, on_delete=models.CASCADE, related_name='settings')
    max_players = models.PositiveIntegerField()
    card_count = models.IntegerField(choices=[(24, '24'), (36, '36'), (52, '52')])
    is_transferable = models.BooleanField(default=False)
    neighbor_throw_only = models.BooleanField(default=False)
    allow_jokers = models.BooleanField(default=False)
    turn_time_limit = models.IntegerField(null=True, blank=True)
    special_rule_set = models.ForeignKey('SpecialRuleSet', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        """Return string representation of the lobby settings.
        
        Returns:
            str: Summary of key settings.
        """
        return f"{self.lobby.name} Settings ({self.card_count} cards, {self.max_players} players)"

    def has_time_limit(self):
        """Check if the lobby has a turn time limit enabled.
        
        Returns:
            bool: True if turn_time_limit is set, False otherwise.
        """
        return self.turn_time_limit is not None

    def is_beginner_friendly(self):
        """Check if settings are suitable for beginner players.
        
        Returns:
            bool: True if settings use standard rules without complex features.
        """
        return (not self.is_transferable and 
                not self.allow_jokers and 
                self.special_rule_set is None)

    class Meta:
        verbose_name = 'Lobby Settings'
        verbose_name_plural = 'Lobby Settings'


class LobbyPlayer(models.Model):
    """Relationship model connecting users to lobbies with their status.
    
    Represents a player's membership in a specific lobby, tracking their
    current status and readiness to play. Handles the player lifecycle
    from joining to leaving the lobby.
    
    Attributes:
        id (UUIDField): Unique identifier for the lobby membership.
        lobby (ForeignKey): Reference to the Lobby the player has joined.
        user (ForeignKey): Reference to the User who joined the lobby.
        status (CharField): Current status of the player in the lobby.
        
    Status Choices:
        - 'waiting': Player has joined but is not ready to start
        - 'ready': Player is ready to start a game
        - 'playing': Player is currently in an active game
        - 'left': Player has left the lobby
        
    Example:
        # Add a player to a lobby
        player = LobbyPlayer.objects.create(
            lobby=lobby,
            user=user,
            status='waiting'
        )
        
        # Mark player as ready
        player.status = 'ready'
        player.save()
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE, related_name='players')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=10,
                              choices=[('waiting', 'Waiting'), ('ready', 'Ready'), ('playing', 'Playing'),
                                       ('left', 'Left')])

    def __str__(self):
        """Return string representation of the lobby player.
        
        Returns:
            str: Username and status in the lobby.
        """
        return f"{self.user.username} ({self.status}) in {self.lobby.name}"

    def is_active(self):
        """Check if the player is actively participating in the lobby.
        
        Returns:
            bool: True if player status is not 'left', False otherwise.
        """
        return self.status != 'left'

    def can_start_game(self):
        """Check if the player is ready to start a game.
        
        Returns:
            bool: True if player status is 'ready', False otherwise.
        """
        return self.status == 'ready'

    def leave_lobby(self):
        """Mark the player as having left the lobby.
        
        Updates the player's status to 'left' and saves the record.
        """
        self.status = 'left'
        self.save(update_fields=['status'])

    class Meta:
        verbose_name = 'Lobby Player'
        verbose_name_plural = 'Lobby Players'
        unique_together = ['lobby', 'user']
        ordering = ['lobby', 'user__username']


class Game(models.Model):
    """Core game session model for Durak card game.
    
    Represents an active or completed game session within a lobby.
    Handles game state, trump card selection, and player management.
    Each game is linked to a specific lobby and tracks all game-related data.
    
    Attributes:
        id (UUIDField): Unique identifier for the game session.
        lobby (ForeignKey): Reference to the Lobby where this game is played.
        trump_card (ForeignKey): The card that determines the trump suit for this game.
        started_at (DateTimeField): When the game session began.
        finished_at (DateTimeField, optional): When the game ended (null for active games).
        status (CharField): Current game state ('in_progress' or 'finished').
        loser (ForeignKey, optional): Reference to the User who lost the game.
        
    Related Objects:
        players: GamePlayer objects representing players in this game session.
        deck_cards: GameDeck objects representing cards remaining in the deck.
        hands: PlayerHand objects showing which cards each player holds.
        table_cards: TableCard objects representing cards currently on the table.
        discarded_cards: DiscardPile objects for cards that have been discarded.
        turns: Turn objects tracking the sequence of player turns.
        
    Status Choices:
        - 'in_progress': Game is currently being played
        - 'finished': Game has ended with a winner/loser determined
        
    Example:
        # Start a new game
        game = Game.objects.create(
            lobby=lobby,
            trump_card=selected_trump_card,
            status='in_progress'
        )
        
        # End the game with a loser
        game.status = 'finished'
        game.loser = losing_player
        game.finished_at = timezone.now()
        game.save()
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE)
    trump_card = models.ForeignKey('Card', on_delete=models.PROTECT, related_name='as_trump')
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=[('in_progress', 'In Progress'), ('finished', 'Finished')])
    loser = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        """Return string representation of the game.
        
        Returns:
            str: Game info with lobby name and status.
        """
        return f"Game in {self.lobby.name} ({self.status})"

    def is_active(self):
        """Check if the game is currently in progress.
        
        Returns:
            bool: True if status is 'in_progress', False otherwise.
        """
        return self.status == 'in_progress'

    def get_trump_suit(self):
        """Get the trump suit for this game.
        
        Returns:
            CardSuit: The suit of the trump card.
        """
        return self.trump_card.suit

    def get_player_count(self):
        """Get the number of players in this game.
        
        Returns:
            int: Count of GamePlayer objects associated with this game.
        """
        return self.players.count()

    def get_winner(self):
        """Get the winner of the game (all players except the loser).
        
        Returns:
            QuerySet: GamePlayer objects representing winners, or None if game is active.
        """
        if self.status != 'finished' or not self.loser:
            return None
        return self.players.exclude(user=self.loser)

    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'
        ordering = ['-started_at']


class GamePlayer(models.Model):
    """Relationship model connecting users to game sessions with game-specific data.
    
    Represents a player's participation in a specific game, tracking their
    position, remaining cards, and other game-state information.
    
    Attributes:
        id (UUIDField): Unique identifier for the game participation.
        game (ForeignKey): Reference to the Game session.
        user (ForeignKey): Reference to the participating User.
        seat_position (IntegerField): Player's position around the table (turn order).
        cards_remaining (IntegerField): Number of cards currently in player's hand.
        
    Example:
        # Add a player to a game
        game_player = GamePlayer.objects.create(
            game=game,
            user=user,
            seat_position=1,
            cards_remaining=6
        )
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    seat_position = models.IntegerField()
    cards_remaining = models.IntegerField()

    def __str__(self):
        """Return string representation of the game player.
        
        Returns:
            str: Player info with username and card count.
        """
        return f"{self.user.username} ({self.cards_remaining} cards) - Position {self.seat_position}"

    def has_cards(self):
        """Check if the player still has cards in their hand.
        
        Returns:
            bool: True if cards_remaining > 0, False otherwise.
        """
        return self.cards_remaining > 0

    def is_eliminated(self):
        """Check if the player has been eliminated (no cards left).
        
        Returns:
            bool: True if player has no cards remaining, False otherwise.
        """
        return self.cards_remaining == 0

    def get_hand_cards(self):
        """Get all cards currently in this player's hand.
        
        Returns:
            QuerySet: PlayerHand objects representing cards in hand.
        """
        return PlayerHand.objects.filter(game=self.game, player=self.user)

    class Meta:
        verbose_name = 'Game Player'
        verbose_name_plural = 'Game Players'
        unique_together = ['game', 'user']
        ordering = ['seat_position']


class Card(models.Model):
    """Playing card model combining suit, rank, and optional special properties.
    
    Represents an individual playing card with its suit, rank, and any
    special abilities. Cards can be standard playing cards or special
    cards with unique effects.
    
    Attributes:
        id (UUIDField): Unique identifier for the card.
        suit (ForeignKey): Reference to the CardSuit (Hearts, Diamonds, etc.).
        rank (ForeignKey): Reference to the CardRank (Ace, King, etc.).
        special_card (ForeignKey, optional): Reference to special card effects if applicable.
        
    Related Objects:
        attack_card: TableCard objects where this card is the attacking card.
        defense_card: TableCard objects where this card is the defending card.
        as_trump: Game objects where this card serves as the trump card.
        
    Example:
        # Create a standard playing card
        card = Card.objects.create(
            suit=hearts_suit,
            rank=ace_rank
        )
        
        # Create a special card
        special_card = Card.objects.create(
            suit=spades_suit,
            rank=joker_rank,
            special_card=skip_effect
        )
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    suit = models.ForeignKey(CardSuit, on_delete=models.CASCADE)
    rank = models.ForeignKey(CardRank, on_delete=models.CASCADE)
    special_card = models.ForeignKey('SpecialCard', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        """Return string representation of the card.
        
        Returns:
            str: Card rank and suit (e.g., "Ace of Hearts").
        """
        base_name = f"{self.rank.name} of {self.suit.name}"
        if self.special_card:
            return f"{base_name} ({self.special_card.name})"
        return base_name

    def is_trump(self, trump_suit):
        """Check if this card belongs to the trump suit.
        
        Args:
            trump_suit (CardSuit): The current trump suit for the game.
            
        Returns:
            bool: True if card's suit matches trump suit, False otherwise.
        """
        return self.suit == trump_suit

    def is_special(self):
        """Check if this card has special effects.
        
        Returns:
            bool: True if special_card is set, False otherwise.
        """
        return self.special_card is not None

    def can_beat(self, other_card, trump_suit):
        """Check if this card can beat another card according to Durak rules.
        
        Args:
            other_card (Card): The card to compare against.
            trump_suit (CardSuit): The current trump suit.
            
        Returns:
            bool: True if this card can beat the other card, False otherwise.
        """
        # Trump cards beat non-trump cards
        if self.is_trump(trump_suit) and not other_card.is_trump(trump_suit):
            return True
        
        # Non-trump cannot beat trump
        if not self.is_trump(trump_suit) and other_card.is_trump(trump_suit):
            return False
        
        # Same suit comparison by rank value
        if self.suit == other_card.suit:
            return self.rank.value > other_card.rank.value
        
        # Different non-trump suits cannot beat each other
        return False

    class Meta:
        verbose_name = 'Card'
        verbose_name_plural = 'Cards'
        unique_together = ['suit', 'rank', 'special_card']


class GameDeck(models.Model):
    """Model representing cards remaining in the deck during a game.
    
    Tracks the position and order of cards in the game deck. Cards are
    drawn from this deck when players need to replenish their hands.
    
    Attributes:
        id (UUIDField): Unique identifier for the deck entry.
        game (ForeignKey): Reference to the Game session.
        card (ForeignKey): Reference to the Card in the deck.
        position (IntegerField): Position of the card in the deck (for draw order).
        
    Example:
        # Add a card to the game deck
        GameDeck.objects.create(
            game=game,
            card=card,
            position=1
        )
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    position = models.IntegerField()

    def __str__(self):
        """Return string representation of the deck card.
        
        Returns:
            str: Card info with position in deck.
        """
        return f"{self.card} at position {self.position} in {self.game}"

    @classmethod
    def get_top_card(cls, game):
        """Get the top card from the deck (lowest position number).
        
        Args:
            game (Game): The game to get the top card for.
            
        Returns:
            GameDeck: The deck entry with the lowest position, or None if deck is empty.
        """
        return cls.objects.filter(game=game).order_by('position').first()

    @classmethod
    def draw_card(cls, game):
        """Draw and remove the top card from the deck.
        
        Args:
            game (Game): The game to draw a card from.
            
        Returns:
            Card: The drawn card, or None if deck is empty.
        """
        deck_card = cls.get_top_card(game)
        if deck_card:
            card = deck_card.card
            deck_card.delete()
            return card
        return None

    def is_last_card(self):
        """Check if this is the last card in the deck.
        
        Returns:
            bool: True if no other cards have higher positions, False otherwise.
        """
        return not GameDeck.objects.filter(
            game=self.game, 
            position__gt=self.position
        ).exists()

    class Meta:
        verbose_name = 'Game Deck Card'
        verbose_name_plural = 'Game Deck Cards'
        unique_together = ['game', 'position']
        ordering = ['position']


class PlayerHand(models.Model):
    """Model representing cards in a player's hand during a game.
    
    Tracks which cards each player holds, with optional ordering
    information for UI display purposes.
    
    Attributes:
        id (UUIDField): Unique identifier for the hand entry.
        game (ForeignKey): Reference to the Game session.
        player (ForeignKey): Reference to the User who holds the card.
        card (ForeignKey): Reference to the Card in the player's hand.
        order_in_hand (IntegerField, optional): Display order of card in hand.
        
    Example:
        # Add a card to a player's hand
        PlayerHand.objects.create(
            game=game,
            player=user,
            card=card,
            order_in_hand=1
        )
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    order_in_hand = models.IntegerField(null=True, blank=True)

    def __str__(self):
        """Return string representation of the hand card.
        
        Returns:
            str: Player and card information.
        """
        return f"{self.player.username} holds {self.card} in {self.game}"

    @classmethod
    def get_player_hand(cls, game, player):
        """Get all cards in a specific player's hand for a game.
        
        Args:
            game (Game): The game session.
            player (User): The player whose hand to retrieve.
            
        Returns:
            QuerySet: PlayerHand objects ordered by order_in_hand.
        """
        return cls.objects.filter(
            game=game, 
            player=player
        ).order_by('order_in_hand')

    @classmethod
    def get_hand_size(cls, game, player):
        """Get the number of cards in a player's hand.
        
        Args:
            game (Game): The game session.
            player (User): The player whose hand size to count.
            
        Returns:
            int: Number of cards in the player's hand.
        """
        return cls.objects.filter(game=game, player=player).count()

    def remove_from_hand(self):
        """Remove this card from the player's hand.
        
        Deletes the PlayerHand record and updates the GamePlayer's
        cards_remaining counter.
        """
        game_player = GamePlayer.objects.get(game=self.game, user=self.player)
        game_player.cards_remaining = max(0, game_player.cards_remaining - 1)
        game_player.save(update_fields=['cards_remaining'])
        self.delete()

    class Meta:
        verbose_name = 'Player Hand Card'
        verbose_name_plural = 'Player Hand Cards'
        unique_together = ['game', 'player', 'card']
        ordering = ['order_in_hand']


class TableCard(models.Model):
    """Model representing attack and defense card pairs on the table.
    
    During a Durak game round, attacking cards are placed on the table
    and can be defended by appropriate defending cards. This model
    tracks these attack-defense pairs.
    
    Attributes:
        id (UUIDField): Unique identifier for the table card pair.
        game (ForeignKey): Reference to the Game session.
        attack_card (ForeignKey): The card used for attack.
        defense_card (ForeignKey, optional): The card used for defense (null if undefended).
        
    Related Objects:
        moves: Move objects referencing this table card pair.
        
    Example:
        # Place an attack card on the table
        table_card = TableCard.objects.create(
            game=game,
            attack_card=seven_of_hearts
        )
        
        # Defend the attack
        table_card.defense_card = ten_of_hearts
        table_card.save()
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    attack_card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='attack_card')
    defense_card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='defense_card')

    def __str__(self):
        """Return string representation of the table card.
        
        Returns:
            str: Attack and defense card information.
        """
        if self.defense_card:
            return f"{self.attack_card} defended by {self.defense_card}"
        return f"{self.attack_card} (undefended)"

    def is_defended(self):
        """Check if the attack card has been defended.
        
        Returns:
            bool: True if defense_card is set, False otherwise.
        """
        return self.defense_card is not None

    def is_valid_defense(self, defense_card, trump_suit):
        """Check if a card can validly defend this attack.
        
        Args:
            defense_card (Card): The card being used for defense.
            trump_suit (CardSuit): The current trump suit.
            
        Returns:
            bool: True if the defense is valid according to Durak rules.
        """
        if self.is_defended():
            return False  # Already defended
        
        return defense_card.can_beat(self.attack_card, trump_suit)

    def defend_with(self, defense_card, trump_suit):
        """Attempt to defend this attack with a card.
        
        Args:
            defense_card (Card): The card being used for defense.
            trump_suit (CardSuit): The current trump suit.
            
        Returns:
            bool: True if defense was successful, False otherwise.
        """
        if self.is_valid_defense(defense_card, trump_suit):
            self.defense_card = defense_card
            self.save(update_fields=['defense_card'])
            return True
        return False

    class Meta:
        verbose_name = 'Table Card'
        verbose_name_plural = 'Table Cards'
        ordering = ['id']


class DiscardPile(models.Model):
    """Model representing cards that have been discarded from the game.
    
    After successful defense rounds or when cards are played out,
    they are moved to the discard pile and removed from active play.
    
    Attributes:
        id (UUIDField): Unique identifier for the discard entry.
        game (ForeignKey): Reference to the Game session.
        card (ForeignKey): Reference to the discarded Card.
        position (IntegerField, optional): Order in which cards were discarded.
        
    Example:
        # Discard cards after a successful defense
        DiscardPile.objects.create(
            game=game,
            card=attack_card,
            position=1
        )
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        """Return string representation of the discarded card.
        
        Returns:
            str: Card and position information.
        """
        pos_info = f" (position {self.position})" if self.position else ""
        return f"Discarded {self.card}{pos_info}"

    @classmethod
    def discard_cards(cls, game, cards):
        """Discard multiple cards at once.
        
        Args:
            game (Game): The game session.
            cards (list): List of Card objects to discard.
            
        Returns:
            list: List of created DiscardPile objects.
        """
        last_position = cls.objects.filter(game=game).count()
        discard_entries = []
