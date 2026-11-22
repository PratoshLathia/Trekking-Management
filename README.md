# 🥾 TrekMate — Trekking Management Portal

A centralized full-stack web platform built with **Vue.js** and **Flask** that manages treks, trek staff, and trekker bookings, with role-based access control, an admin approval workflow, and automated background jobs powered by **Celery** and **Redis**.

---

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [Features](#features)
- [How It Works](#how-it-works)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Limitations & Future Enhancements](#limitations--future-enhancements)
- [Author](#author)

---

## About the Project

Trekking and adventure tourism organizations need an organized system to manage treks, coordinate trek staff, and handle trekker bookings, while keeping communication timely and giving administrators oversight across the whole trek lifecycle. TrekMate provides a single-page application with a JWT-secured REST API and role-based access control for three user types:

- **Admin** — Creates treks and staff, assigns staff, approves staff change requests, and manages all users
- **Trek Staff** — Manages assigned treks, views participants, and submits trek changes for approval
- **Trekker (User)** — Searches treks, books and cancels, and tracks and exports booking history

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python, JavaScript |
| Frontend Framework | Vue.js 3 (SPA) with Vue Router |
| Frontend Styling | Bootstrap 5 |
| Build Tool | Vite |
| Backend Framework | Flask 3.1.3 |
| ORM | SQLAlchemy 2.0.51 / Flask-SQLAlchemy 3.1.1 |
| Database | SQLite |
| Authentication | Flask-JWT-Extended 4.7.4 (token-based, role claims) |
| Password Hashing | Werkzeug 3.1.8 |
| Cross-Origin Requests | Flask-CORS 6.0.5 |
| Caching | Flask-Caching 2.4.1 + Redis |
| Background Jobs | Celery 5.6.3 + Celery Beat, with Redis as broker |
| Email | Flask-Mail 0.10.0 (SMTP) |
| Configuration | python-dotenv (environment variables) |

> Full dependency lists: see [`backend/requirements.txt`](backend/requirements.txt) and [`frontend/package.json`](frontend/package.json)

---

## Database Schema

The application uses **6 tables** with the following relationships:

```
users
 ├── staff_profiles          (One-to-One via user_id)
 ├── user_profiles           (One-to-One via user_id)
 ├── treks                   (One-to-Many via staff_id)
 │     ├── bookings          (Many-to-Many bridge: user ↔ trek)
 │     └── trek_change_requests   (One-to-Many via trek_id)
 └── trek_change_requests    (One-to-Many via staff_id)
```

An ER diagram is included in the repository: [`ER Diagram.png`](ER%20Diagram.png)

### Tables

**`users`** — Base user table for all roles  
`id` · `username` · `email (unique)` · `password` · `role (admin / staff / user)` · `status`

**`treks`** — Treks created by the admin and led by a staff member  
`id` · `staff_id (FK)` · `name` · `location` · `duration` · `difficulty` · `slots` · `start_date` · `end_date` · `status` · `stage`

**`bookings`** — Association table (User ↔ Trek many-to-many)  
`id` · `user_id (FK)` · `trek_id (FK)` · `booking_date` · `status` · `payment_status` · `reminder_sent`

**`trek_change_requests`** — Staff-submitted trek changes waiting for admin review  
`id` · `trek_id (FK)` · `staff_id (FK)` · `field` · `old_value` · `new_value` · `request_status` · `created_at`

**`staff_profiles`** — Extended staff info  
`id` · `user_id (FK)` · `contact_number` · `gender` · `address` · `medical_certification` · `experience`

**`user_profiles`** — Extended trekker info  
`id` · `user_id (FK)` · `contact_number` · `age` · `gender` · `address` · `medical_conditions` · `emergency_contact_name` · `emergency_contact_number`

> Trek status values: `Active` / `Closed`  
> Trek stage values: `Upcoming` → `Started` → `Ongoing` → `Completed`  
> Booking status values: `Booked` → `Completed` / `Cancelled`  
> Change request status values: `Pending` → `Approved` / `Rejected`

---

## Features

### 🔐 Admin
- Add and manage staff and trekker accounts
- Create, edit, and delete treks
- Assign or reassign staff, with scheduling-conflict checks
- Approve or reject staff change requests
- Blacklist or reactivate staff and trekkers
- View all bookings, dashboard statistics, and generated reports
- Trigger reminder and report jobs on demand

### 🧭 Trek Staff
- Create and update own profile
- View only their assigned treks and participants
- Remove a participant from a trek
- Submit status, slots, stage, and difficulty changes for admin approval

### 🥾 Trekker (User)
- Create and update own profile
- Search and filter treks by location, duration, and difficulty
- Book and cancel treks (duplicate booking prevention enforced)
- Track full booking history, including cancellations
- Export booking history as CSV in the background

### ⚙️ System
- JWT authentication with role checks on every protected route
- Redis caching of frequently used list endpoints, cleared on every write
- Automatic booking changes when a trek stage changes: any stage after `Upcoming` closes the trek, and `Completed` completes its bookings
- Daily trek reminder emails and monthly activity reports (Celery Beat)
- Server-side validation of dates, stages, statuses, and difficulty values
- Atomic slot claiming to prevent overbooking
- Secrets read from environment variables, never hard-coded
- Responsive UI with Bootstrap 5

---

## How It Works

1. **Setup (admin):** the admin adds staff, then creates treks with dates, slots, difficulty, and an assigned staff member.
2. **Booking (user):** a trekker registers, completes their profile, and books an open trek. Each booking takes one slot, and cancelling gives it back.
3. **Running the trek (staff and admin):** staff changes go into `trek_change_requests` as pending, and the admin approves or rejects them. Admin changes apply immediately.
4. **Background work (Celery):** reminder emails go out daily for treks starting within 3 days, a monthly report is saved to `backend/reports/` and emailed to admins, and CSV exports are built on request.

Redis plays two roles: it caches list endpoints (database 0) and acts as the Celery message broker and result store (database 1).

---

## API Endpoints

### Authentication
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/register` | Register a trekker |
| POST | `/login` | Login (shared by all roles) |

### Trek
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/trek/all` | List all treks (public) |
| POST | `/trek/add` | Create a trek (admin) |
| POST | `/trek/<trek_id>/update` | Update trek details (admin) |
| POST | `/trek/<trek_id>/assign_staff` | Assign or reassign staff (admin) |
| DELETE | `/trek/<trek_id>` | Delete a trek (admin) |
| POST | `/trek/<trek_id>/status` | Update status (staff changes need approval) |
| POST | `/trek/<trek_id>/slots` | Update slots (staff changes need approval) |
| POST | `/trek/<trek_id>/stage` | Update stage (staff changes need approval) |
| POST | `/trek/<trek_id>/difficulty` | Update difficulty (staff changes need approval) |
| GET | `/trek/change_requests` | List pending change requests (admin) |
| POST | `/trek/change_requests/<request_id>/approve` | Approve a change request (admin) |
| POST | `/trek/change_requests/<request_id>/reject` | Reject a change request (admin) |

### Booking
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/trek/<trek_id>/book` | Book a trek (trekker) |
| GET | `/trek/<trek_id>/bookings` | View a trek's participants (staff / admin) |
| POST | `/booking/<booking_id>/cancel` | Cancel own booking (trekker) |
| POST | `/booking/<booking_id>/remove` | Remove a participant (staff / admin) |
| GET | `/booking/all` | View all bookings (admin) |
| POST | `/booking/export` | Start a CSV export job (trekker) |
| GET | `/booking/export/<task_id>/status` | Check export job status |
| GET | `/booking/export/<task_id>/download` | Download the finished export |

### Staff
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/staff/add` | Create a staff account (admin) |
| GET | `/staff/all` | List staff (admin) |
| POST | `/staff/<staff_id>/status` | Blacklist or reactivate staff (admin) |
| POST | `/staff/profile` | Create or update own profile (staff) |
| GET | `/staff/<staff_id>/profile` | View own profile (staff) |
| GET | `/staff/<staff_id>/treks` | View assigned treks (staff) |

### User (Trekker)
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/user/all` | List trekkers (admin) |
| POST | `/user/<user_id>/status` | Blacklist or reactivate a trekker (admin) |
| POST | `/user/profile` | Create or update own profile (trekker) |
| GET | `/user/<user_id>/profile` | View own profile (trekker) |
| GET | `/user/<user_id>/bookings` | View own booking history (trekker) |

### Background Jobs & Statistics (Admin)
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/admin/reminders/run` | Run the reminder job now |
| POST | `/admin/reports/generate` | Generate the monthly report now |
| GET | `/admin/reports` | List generated reports |
| GET | `/admin/reports/<filename>` | View a generated report |
| GET | `/stats` | Dashboard summary statistics |

---

## Project Structure

```
Trekking Management Portal/
│
├── backend/
│   ├── app.py                  # Flask app — models, routes, RBAC, validation
│   ├── tasks.py                # Celery jobs — reminders, reports, CSV export
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment variable template
│   ├── instance/trekking.db    # SQLite database (created on first run)
│   ├── reports/                # Generated monthly reports
│   └── exports/                # Generated CSV exports
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── api.js              # Fetch helper — adds the JWT, sets the API URL
│       ├── router/routes.js    # Routes with role guards
│       ├── components/
│       │   └── Navbar.vue
│       └── views/              # Login, Register, Admin, Staff, User,
│                               # TrekManagement, StaffManagement, UserManagement,
│                               # AddTrek, AddStaff, AllBookings, UserBookings,
│                               # TrekBookings, Statistics, Reports, Home
│
├── ER Diagram.png
└── Project Report.pdf
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Redis server running on port 6379
- A Gmail address with an app password (only needed for emails)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/trekking-management-portal.git
cd trekking-management-portal

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate         # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env             # On Windows: copy .env.example .env
# then open .env and fill in the values (see below)

# 4. Start the backend (creates the database and admin account on first run)
python app.py

# 5. In a new terminal, start the frontend
cd frontend
npm install
npm run dev
```

The API runs at `http://127.0.0.1:5000/` and the app at `http://localhost:5173/`

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `JWT_SECRET_KEY` | Secret used to sign login tokens (use a long random string) |
| `ADMIN_EMAIL` | Email of the default admin (default `admin@gmail.com`) |
| `ADMIN_PASSWORD` | Password of the default admin (a random one is printed if blank) |
| `MAIL_USERNAME` / `MAIL_PASSWORD` | Gmail address and app password for sending emails |
| `MAIL_DEFAULT_SENDER` | From address (defaults to `MAIL_USERNAME`) |
| `REDIS_HOST` / `REDIS_PORT` | Redis location (default `localhost:6379`) |
| `CELERY_BROKER_URL` | Celery broker URL (default `redis://localhost:6379/1`) |
| `FLASK_DEBUG` | Set to `1` to enable debug mode |

> The admin account is only created when no admin exists yet. Never commit your `.env` file.

### Background Jobs (optional)

Run these from `backend/`, each in its own terminal, to enable reminder emails, monthly reports, and CSV export:

```bash
celery -A tasks.celery_app worker --loglevel=info      # add --pool=solo on Windows
celery -A tasks.celery_app beat --loglevel=info
```

---

## Limitations & Future Enhancements

### Current Limitations
- Email delivery needs SMTP credentials set in `.env`
- No automated schema migration tool (changes to existing tables need a fresh database)
- No payment integration (`payment_status` is a placeholder)
- The API address in `frontend/src/api.js` is hard-coded for local use

### Planned Enhancements
- [ ] Schema migrations with Flask-Migrate
- [ ] Payment gateway integration
- [ ] PDF report generation alongside the HTML reports
- [ ] Push / SMS notification channels alongside email

---

## Author

**Pratosh Lathia**  
📧 [pratoshsl25@gmail.com](mailto:pratoshsl25@gmail.com) 
📧 [23f3003255@ds.study.iitm.ac.in](mailto:23f3003255@ds.study.iitm.ac.in)  
🎓 IIT Madras — BS in Data Science and Applications
