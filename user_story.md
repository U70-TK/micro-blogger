# Microblogging Web Application Requirements

## Overview

This project is a Twitter-like microblogging platform where users can create profiles, post short updates, like and reply to posts, and view a global feed. The application will be built with the following stack:

- **Backend:** NestJS (TypeScript)
- **Frontend:** Vite + React (TypeScript)
- **Database:** PostgreSQL
- **Containerization/Orchestration:** Docker, Docker Compose
- **Other Tools:** ESLint, Prettier, Jest (for testing), Nginx (for reverse proxy)

---

## User Stories

### 1. User Registration & Authentication
- As a new user, I want to register with a username, email, and password.
- As a registered user, I want to log in and log out securely.
- As a user, I want my session to persist securely (JWT or session cookies).

### 2. User Profile
- As a user, I want to create and edit my profile (username, display name, bio, avatar).
- As a user, I want to view my own profile and see all my posts.
- As a visitor, I want to view any user’s profile and see their posts.

### 3. Posting Updates
- As a user, I want to post short text updates (e.g., max 280 characters).
- As a user, I want to see my posts appear in the global feed immediately.

### 4. Global Feed
- As a user, I want to view a chronological feed of all posts from all users.
- As a user, I want to see who posted each update and when.

### 5. Likes
- As a user, I want to like or unlike any post.
- As a user, I want to see the number of likes on each post.

### 6. Replies
- As a user, I want to reply to any post (one level deep, no nested replies).
- As a user, I want to see replies under the original post.

### 7. General Constraints
- No private messaging between users.
- No retweets/reposts.
- No follower/following system; the feed is global.

---

## Database Schema

### Users

| Field         | Type           | Constraints                |
|---------------|----------------|----------------------------|
| id            | SERIAL         | PRIMARY KEY                |
| username      | VARCHAR(32)    | UNIQUE, NOT NULL           |
| email         | VARCHAR(255)   | UNIQUE, NOT NULL           |
| password_hash | VARCHAR(255)   | NOT NULL                   |
| display_name  | VARCHAR(64)    |                            |
| bio           | TEXT           |                            |
| avatar_url    | VARCHAR(255)   |                            |
| created_at    | TIMESTAMP      | DEFAULT now(), NOT NULL    |
| updated_at    | TIMESTAMP      | DEFAULT now(), NOT NULL    |

### Posts

| Field         | Type           | Constraints                |
|---------------|----------------|----------------------------|
| id            | SERIAL         | PRIMARY KEY                |
| user_id       | INTEGER        | REFERENCES users(id)       |
| content       | VARCHAR(280)   | NOT NULL                   |
| created_at    | TIMESTAMP      | DEFAULT now(), NOT NULL    |
| updated_at    | TIMESTAMP      | DEFAULT now(), NOT NULL    |

### Likes

| Field         | Type           | Constraints                |
|---------------|----------------|----------------------------|
| id            | SERIAL         | PRIMARY KEY                |
| user_id       | INTEGER        | REFERENCES users(id)       |
| post_id       | INTEGER        | REFERENCES posts(id)       |
| created_at    | TIMESTAMP      | DEFAULT now(), NOT NULL    |
| UNIQUE(user_id, post_id)       |                            |

### Replies

| Field         | Type           | Constraints                |
|---------------|----------------|----------------------------|
| id            | SERIAL         | PRIMARY KEY                |
| post_id       | INTEGER        | REFERENCES posts(id)       |
| user_id       | INTEGER        | REFERENCES users(id)       |
| content       | VARCHAR(280)   | NOT NULL                   |
| created_at    | TIMESTAMP      | DEFAULT now(), NOT NULL    |

---

## Technical Details

- **Backend:**  
  - NestJS (TypeScript), RESTful API
  - JWT-based authentication
  - Validation with class-validator
  - Testing with Jest
  - Dockerized for deployment

- **Frontend:**  
  - Vite + React (TypeScript)
  - State management (e.g., Redux Toolkit or React Context)
  - API calls via fetch/axios
  - Responsive design (CSS modules or styled-components)
  - Form validation (e.g., react-hook-form)

- **Database:**  
  - PostgreSQL
  - ORM: TypeORM or Prisma (recommended for NestJS)
  - Dockerized for local development

- **Other:**  
  - Nginx as reverse proxy (optional, for production)
  - ESLint & Prettier for code quality
  - Docker Compose for orchestration

---