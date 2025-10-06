import uuid
from django.db import models


class CardSuit(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=20)
    color = models.CharField(max_length=5, choices=[('red', 'Red'), ('black', 'Black')])


class CardRank(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=20)
    value = models.IntegerField()


class Lobby(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_private = models.BooleanField(default=False)
    password_hash = models.CharField(max_length=128, null=True, blank=True)
    status = models.CharField(max_length=10,
                              choices=[('waiting', 'Waiting'), ('playing', 'Playing'), ('closed', 'Closed')])
    created_at = models.DateTimeField(auto_now_add=True)


class LobbySettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lobby = models.OneToOneField(Lobby, on_delete=models.CASCADE, related_name='settings')
    max_players = models.PositiveIntegerField()
    card_count = models.IntegerField(choices=[(24, '24'), (36, '36'), (52, '52')])
    is_transferable = models.BooleanField(default=False)
    neighbor_throw_only = models.BooleanField(default=False)
    allow_jokers = models.BooleanField(default=False)
    turn_time_limit = models.IntegerField(null=True, blank=True)
    special_rule_set = models.ForeignKey('SpecialRuleSet', on_delete=models.SET_NULL, null=True, blank=True)


class LobbyPlayer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE, related_name='players')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=10,
                              choices=[('waiting', 'Waiting'), ('ready', 'Ready'), ('playing', 'Playing'),
                                       ('left', 'Left')])


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE)
    trump_card = models.ForeignKey('Card', on_delete=models.PROTECT, related_name='as_trump')
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=[('in_progress', 'In Progress'), ('finished', 'Finished')])
    loser = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)


class GamePlayer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    seat_position = models.IntegerField()
    cards_remaining = models.IntegerField()


class Card(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    suit = models.ForeignKey(CardSuit, on_delete=models.CASCADE)
    rank = models.ForeignKey(CardRank, on_delete=models.CASCADE)
    special_card = models.ForeignKey('SpecialCard', on_delete=models.SET_NULL, null=True, blank=True)


class GameDeck(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    position = models.IntegerField()


class PlayerHand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    order_in_hand = models.IntegerField(null=True, blank=True)


class TableCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    attack_card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='attack_card')
    defense_card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='defense_card')


class DiscardPile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    position = models.IntegerField(null=True, blank=True)


class SpecialRuleSet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    min_players = models.PositiveIntegerField()


class SpecialCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    effect_type = models.CharField(max_length=10, choices=[
        ('skip', 'Skip'),
        ('reverse', 'Reverse'),
        ('draw', 'Draw'),
        ('custom', 'Custom'),
    ])
    effect_value = models.JSONField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)


class SpecialRuleSetCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_set = models.ForeignKey(SpecialRuleSet, on_delete=models.CASCADE)
    card = models.ForeignKey(SpecialCard, on_delete=models.CASCADE)


class Turn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    turn_number = models.IntegerField()


class Move(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    turn = models.ForeignKey(Turn, on_delete=models.CASCADE)
    table_card = models.ForeignKey(TableCard, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=10,
                                   choices=[('attack', 'Attack'), ('defend', 'Defend'), ('pickup', 'Pickup')])
    created_at = models.DateTimeField(auto_now_add=True)
