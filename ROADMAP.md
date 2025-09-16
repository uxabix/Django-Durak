# Django - Durak card game — Roadmap

## Technologies
- Django, Channels
- PostgreSQL
- Docker
- GitFlow
- Sphinx

## Documentation & Tests
- Documentation with Sphinx
- README with setup instructions
- Unit and integration tests throughout the development process

---

## -v0.1
Docker
Django
GitFlow

## v0.0 — Setup (infrastructure)
- [ ] Initialize Django project
- [ ] Create base app (`core`)
- [ ] Connect PostgreSQL (`settings.py`)
- [ ] Dockerfile for Django
- [ ] docker-compose (Django + PostgreSQL)
- [ ] Initialize Git repository, set up GitFlow
- [ ] Configure CI (linter + tests on GitHub Actions)
- [ ] Basic tests (server startup, endpoint availability)

---

## v0.1 — Users & Base models
- [ ] Create models: `User`, `Card`, `Game` (draft)
- [ ] Run migrations
- [ ] Add admin panel for User/Game
- [ ] Integrate Django Channels
- [ ] Write a test WebSocket consumer (echo/ping)
- [ ] Implement registration (Django/DRF)
- [ ] Implement login (JWT or session-based)
- [ ] Tests: user creation, login/logout, WebSocket connection

---

## v0.2 — Lobby system
- [ ] Model `Lobby` (id, owner, players, status)
- [ ] API: create lobby / join / leave
- [ ] WebSocket: notify players when lobby state changes
- [ ] Main page (Django template SSR or API)
- [ ] API: list of lobbies (filtering, search)
- [ ] API: friend search (by nickname/email)
- [ ] Model `Friendship` (user_from, user_to, status)
- [ ] Tests: lobby creation, joining, API queries, friendship

---

## v1.0 — MVP (1v1 game, basic rules)
- [ ] Model `GameRound` (deck, current player, table)
- [ ] Implement basic “Durak” rules (2 players)
- [ ] Card dealing, trump suit selection
- [ ] WebSocket: exchange game events (move → update all players)
- [ ] API: start game from lobby
- [ ] Notifications (via WebSocket events + DB logging)
- [ ] Docker production config (gunicorn/daphne + nginx)
- [ ] Minimal deploy (Railway/Heroku/VPS)
- [ ] Tests: gameplay scenarios (deal cards, make a move, check winner)

---

## v1.1 — Lobby extensions
- [ ] Lobby settings (number of players, private/public, password)
- [ ] Game invitations (via friend list / invite link)
- [ ] Extended rules (chasing, finish deck, auto-pass)
- [ ] WebSocket: invitation events
- [ ] Tests: private lobby, invitations

---

## v1.2 — Social features
- [ ] Lobby chat (WebSocket, history storage)
- [ ] Profile settings (avatar, status, bio)
- [ ] Improved notifications (e-mail for invites)
- [ ] Tests: chat, profile updates

---

## v1.3+ (optional)
- [ ] Player rating system
- [ ] Game history
- [ ] Mobile-friendly frontend
- [ ] Support for 3–4 players

---

## Teamwork (3 backend devs)
Example task distribution for **v0.1**:
- **Dev1:** Models User/Game/Card + migrations + tests  
- **Dev2:** Channels + test WebSocket consumer  
- **Dev3:** Registration/login + API  

General rule: all tasks go through code review, roles may rotate.

---

## Kanban flow (for GitHub Projects)
- **To Do** — tasks from roadmap (not yet started)  
- **In Progress** — tasks currently being worked on  
- **Review** — pull requests waiting for review  
- **Done** — completed tasks  

---
