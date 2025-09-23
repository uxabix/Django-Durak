# Project Structure Plan: "Durak" Card Game

## Overview
This Django project implements an online card game "Durak" with user profiles, game rooms, real-time gameplay, and chat functionality. The project uses **Django REST Framework** for API development, **Django templates** for temporary front-end rendering, and **WebSocket (Django Channels)** for real-time updates. The architecture is modular, maintainable, and ready for future SPA integration (React/Vue).

> Note: The structure below is a proposed plan. It may evolve or change over time according to the best development practices and project growth. The `Common / Utilities` application may not be necessary depending on project needs.

---

## 1. Applications

### 1️⃣ Accounts (`accounts`)
**Purpose:** User management, authentication, and profile system.

**Models:**
- `User` (custom `AbstractUser`)  
- `Profile` (OneToOne with User; stores rating, statistics, avatar)

**Views / URLs:**
- Templates:
  - `/accounts/login/` – login page  
  - `/accounts/register/` – registration page  
  - `/accounts/profile/` – personal profile  
  - `/accounts/profile/<id>/` – view other users’ profiles
- REST API:
  - `/api/accounts/` – list of users (for admin/testing)  
  - `/api/accounts/<id>/` – user details (statistics, rating)

**Responsibilities:**
- Registration, login/logout, profile viewing  
- API endpoints for user data for front-end consumption

---

### 2️⃣ Game (`game`)
**Purpose:** Core game logic, room management, and real-time gameplay.

**Models:**
- `Room` – game room (name, status)  
- `Game` – game session (room, start/end time)  
- `PlayerInGame` – relation User ↔ Game (role, cards, order)  
- `Card` – card entity (suit, value)  
- `Move` – game moves (attack, defense, draw)

**Views / URLs:**
- Templates:
  - `/rooms/` – list of all rooms (HTML skeleton, JS pulls data)  
  - `/rooms/<room_id>/` – game room page (HTML skeleton, JS pulls players, game state)
- REST API:
  - `/api/rooms/` – list of rooms  
  - `/api/rooms/<id>/` – room details  
  - `/api/rooms/<id>/players/` – players in room  
  - `/api/games/<id>/` – current game state  
  - `/api/games/<id>/moves/` – game history

**WebSocket:**
- `/ws/game/<room_id>/` – real-time game events (player moves, card updates)

**Responsibilities:**
- Game mechanics implementation in `services.py` or `logic.py`  
- Room creation/joining, game state management  
- WebSocket consumer for real-time gameplay

---

### 3️⃣ Chat (`chat`)
**Purpose:** Real-time communication between players in rooms.

**Models:**
- `Message` – chat messages (author, text, timestamp, room)

**Views / URLs:**
- REST API:
  - `/api/chat/rooms/<room_id>/messages/` – chat history  
  - `/api/chat/rooms/<room_id>/send/` – send a new message (POST)
- WebSocket:
  - `/ws/chat/<room_id>/` – real-time chat updates

**Responsibilities:**
- WebSocket consumer for chat messages  
- Optional AJAX fallback for REST API access to chat history  

---

### 4️⃣ Common / Utilities (`common`) (Optional)
**Purpose:** Shared utilities, helper functions, mixins, and validation logic.

**Responsibilities:**
- Reusable code across apps (validators, serializers, helper functions)  
- Base classes for models, views, or consumers

> May be omitted if not needed.

---

## 2. URL Organization

**Templates (HTML pages, JS loads data from API):**
/accounts/login/
/accounts/register/
/accounts/profile/
/accounts/profile/<id>/
/rooms/
/rooms/<room_id>/

**REST API (JSON data for front-end):**
/api/accounts/
/api/accounts/<id>/
/api/rooms/
/api/rooms/<id>/
/api/rooms/<id>/players/
/api/games/<id>/
/api/games/<id>/moves/
/api/chat/rooms/<room_id>/messages/
/api/chat/rooms/<room_id>/send/

**WebSocket (real-time updates):**
/ws/game/<room_id>/
/ws/chat/<room_id>/


---

## 3. Front-End Integration Approach

- Initial front-end uses **Django templates** with minimal JS.  
- JS requests data from REST API endpoints to render game state, player list, and chat messages.  
- WebSocket used for real-time updates (game moves, chat messages).  
- This approach allows **easy future migration to SPA** (React/Vue) without changes to the backend API or WebSocket logic.  

---

## 4. Team Responsibilities

| App        | Suggested Team Member Focus                  |
|------------|----------------------------------------------|
| `accounts` | Authentication, user profiles, API           |
| `game`     | Core game logic, room management, WebSocket  |
| `chat`     | Chat logic, WebSocket, API endpoints         |
| `common`   | Shared utilities and helpers (optional)      |
