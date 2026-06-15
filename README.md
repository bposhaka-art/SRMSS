# SRMSS - Smart Depot Management System

A comprehensive **fleet management and public transport depot operations platform** designed to streamline vehicle scheduling, GPS tracking, maintenance, fuel management, and driver operations.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [User Roles & Permissions](#user-roles--permissions)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Default Credentials](#default-credentials)
- [Screenshots & Workflows](#screenshots--workflows)

---

## ✨ Features

### Core Functionality

- **🔐 Role-Based Access Control (RBAC)**
  - Administrator: Full system access
  - Supervisor: Operations management & monitoring
  - Operational Staff: Driver-specific dashboard & assignments

- **🚗 Fleet Management**
  - Vehicle inventory with capacity & mileage tracking
  - Vehicle utilization monitoring
  - Maintenance scheduling and cost tracking
  - Fuel log management with approval workflow

- **👨‍💼 Driver Management**
  - Driver database with license & contact information
  - Driver assignment to trips
  - Performance history tracking
  - Daily schedule viewing

- **📍 GPS & Tracking**
  - Live real-time vehicle tracking on interactive map
  - GPS simulation for ongoing trips
  - Speed monitoring
  - Vehicle location history

- **🛣️ Route Management**
  - Interactive map-based route creation
  - Bus stop definition with fare calculation
  - OSRM integration for route optimization
  - Distance & stop management

- **📅 Trip Scheduling**
  - Schedule trips with vehicle, driver, and route assignment
  - Conflict detection (driver/vehicle double-booking prevention)
  - Operation date & time management
  - Status tracking (Scheduled → Ongoing → Completed/Delayed)

- **📊 Dashboard & Reports**
  - Real-time statistics (vehicles, drivers, trips, pending items)
  - Fleet utilization charts
  - Trip status distribution (doughnut charts)
  - Monthly performance summaries
  - Fuel cost & maintenance cost analytics
  - Trip completion rates

- **✅ Approval Workflow**
  - Fuel log approval by administrator
  - Maintenance request approval
  - Automatic entry for admin submissions
  - Status tracking (Pending → Approved/Rejected)

- **🎨 UI/UX Features**
  - Responsive dark/light theme toggle
  - Mobile-friendly design
  - Real-time data updates
  - Interactive modals for CRUD operations
  - Sidebar navigation with role-based menu visibility

---

## 📁 Project Structure

```
SRMSS/
├── app.py                          # Main Flask application (single file)
├── srmss_rbac.db                   # SQLite database (auto-created)
├── README.md                        # Documentation
└── .gitignore                       # Git ignore rules
```

### App.py Breakdown

```python
app.py (2,482 lines)
├── HTML Template (1,063 lines)
│   ├── Login Screen
│   ├── Sidebar Navigation
│   ├── Dashboard
│   ├── Control Center
│   ├── Live GPS Tracking
│   ├── Trip Scheduling
│   ├── Route Planning
│   ├── Vehicle/Driver Management
│   ├── Fuel Logs
│   ├── Maintenance
│   ├── Reports
│   ├── Approvals
│   ├── User Management
│   └── Track & Fares Viewer
├── Frontend JavaScript (1,000+ lines)
│   ├── Authentication
│   ├── Theme Toggle
│   ├── Page Routing
│   ├── Modal Management
│   ├── Map Integration (Leaflet)
│   └── API Communication
└── Backend Python (419 lines)
    ├── Database Initialization
    ├── Authentication Routes
    ├── Operations API
    ├── GPS Simulation
    ├── Maintenance & Fuel Endpoints
    ├── Route Management
    ├── User Management
    ├── Approvals Workflow
    ├── Reports Generation
    └── Database Helper Functions
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.x, Flask |
| **Database** | SQLite3 |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Maps & GPS** | Leaflet.js v1.9.4, OpenStreetMap, OSRM API |
| **Charts** | Chart.js |
| **Styling** | CSS Custom Properties (Dark/Light theme) |
| **Threading** | Python threading for GPS simulation |

---

## 👥 User Roles & Permissions

### Administrator
- ✅ Full access to all features
- ✅ User management (create, edit, delete)
- ✅ Fleet management (vehicles, drivers, routes)
- ✅ Approval workflows (fuel, maintenance)
- ✅ System-wide reports & analytics
- ✅ Direct entry for fuel & maintenance (no approval needed)

### Supervisor
- ✅ Operations management & control center
- ✅ Live GPS tracking
- ✅ Trip scheduling & timetable
- ✅ Fleet monitoring & utilization
- ✅ Vehicle & driver management
- ✅ Fuel log submission (requires admin approval)
- ✅ Reports & analytics
- ✅ Route planning

### Operational Staff (Driver)
- ✅ Personal dashboard with assigned trips
- ✅ Today's schedule viewing
- ✅ Trip history tracking
- ✅ Track & fares viewer
- ✅ Fuel log submission (requires approval)

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.7+
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Step 1: Clone Repository

```bash
git clone https://github.com/bposhaka-art/SRMSS.git
cd SRMSS
```

### Step 2: Install Dependencies

```bash
pip install flask
```

### Step 3: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 4: Login

Use the default credentials (see below) to login

---

## 📖 Usage Guide

### First Login

1. Navigate to `http://localhost:5000`
2. Use default admin credentials
3. Database auto-initializes on first run with seed data

### Admin Setup Workflow

1. **User Management** → Create admin, supervisor, and staff accounts
2. **Vehicle Management** → Add your fleet vehicles
3. **Driver Management** → Register all drivers
4. **Route Planning** → Define routes on interactive map
5. **Trip Scheduling** → Assign vehicles & drivers to routes
6. **Approvals** → Manage fuel & maintenance requests

### Supervisor Operations

1. **Control Center** → Monitor real-time trip status
2. **Live GPS Tracking** → Track active vehicles on map
3. **Trip Scheduling** → Schedule new trips
4. **Reports** → View operational analytics

### Driver Dashboard

1. **View Assignments** → See today's trip schedule
2. **Track & Fares** → Check routes and fare calculations
3. **Submit Fuel Logs** → Log fuel purchases (pending approval)

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT,
    driver_id INTEGER
)
```

### Drivers Table
```sql
CREATE TABLE drivers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    license_no TEXT,
    contact TEXT
)
```

### Vehicles Table
```sql
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY,
    registration_no TEXT,
    type TEXT,
    capacity INTEGER,
    mileage REAL
)
```

### Routes Table
```sql
CREATE TABLE routes (
    id INTEGER PRIMARY KEY,
    route_name TEXT,
    distance_km REAL,
    start_point TEXT,
    end_point TEXT,
    path_geometry TEXT,  -- JSON coordinates
    stops TEXT           -- JSON stops with fares
)
```

### Operations Table
```sql
CREATE TABLE operations (
    id INTEGER PRIMARY KEY,
    route_id INTEGER,
    vehicle_id INTEGER,
    driver_id INTEGER,
    operation_date TEXT,
    departure_time TEXT,
    status TEXT,
    current_lat REAL,
    current_lon REAL,
    speed REAL
)
```

### Maintenance Table
```sql
CREATE TABLE maintenance (
    id INTEGER PRIMARY KEY,
    vehicle_id INTEGER,
    driver_id INTEGER,
    date TEXT,
    description TEXT,
    cost REAL,
    status TEXT
)
```

### Fuel Logs Table
```sql
CREATE TABLE fuel_logs (
    id INTEGER PRIMARY KEY,
    vehicle_id INTEGER,
    date TEXT,
    liters REAL,
    cost REAL,
    status TEXT
)
```

### Approvals Table
```sql
CREATE TABLE approvals (
    id INTEGER PRIMARY KEY,
    type TEXT,
    data TEXT,      -- JSON data
    message TEXT,
    status TEXT
)
```

---

## 🔌 API Endpoints

### Authentication
- `POST /api/login` - User login with credentials

### Statistics & Operations
- `GET /api/stats` - Dashboard statistics
- `POST /api/operations/schedule` - Schedule a trip
- `GET /api/operations/today` - Today's operations
- `GET /api/operations/date/<date>` - Operations by date
- `POST /api/operations/status/<id>` - Update trip status

### GPS & Tracking
- `POST /api/gps/start/<op_id>` - Start GPS simulation
- `GET /api/gps/live` - Get live vehicle locations

### Vehicles
- `GET /api/vehicles` - List all vehicles
- `POST /api/vehicles` - Create vehicle
- `POST /api/vehicles/update/<id>` - Update vehicle

### Drivers
- `GET /api/drivers` - List all drivers
- `POST /api/drivers` - Create driver
- `POST /api/drivers/update/<id>` - Update driver

### Routes
- `GET /api/routes` - List all routes
- `POST /api/routes` - Create route
- `GET /api/routes/<id>` - Get route details

### Fuel Management
- `GET /api/fuel` - List fuel logs
- `POST /api/fuel` - Submit fuel log (requires approval)
- `POST /api/fuel/direct` - Admin direct entry (no approval)

### Maintenance
- `GET /api/maintenance` - List maintenance records
- `POST /api/maintenance` - Add maintenance record (admin direct)

### Approvals
- `GET /api/approvals/pending` - List pending approvals
- `POST /api/approvals` - Create approval request
- `POST /api/approvals/approve/<id>` - Approve item
- `POST /api/approvals/reject/<id>` - Reject item

### User Management
- `GET /api/users` - List all users
- `POST /api/users` - Create user
- `PUT /api/users/<id>` - Update user role
- `DELETE /api/users/<id>` - Delete user

### Reports & Analytics
- `GET /api/reports/summary` - Performance summary
- `GET /api/monitoring/vehicles` - Vehicle utilization
- `GET /api/driver/history/<driver_id>` - Driver trip history
- `GET /api/driver/today/<driver_id>` - Driver today's assignments

---

## 🔑 Default Credentials

After first run, use these credentials to login:

| Role | Username | Password |
|------|----------|----------|
| Administrator | `admin` | `admin` |
| Supervisor | `supervisor` | `super` |
| Operational Staff | `driver` | `driver` |

**⚠️ Security Note**: Change default credentials immediately in production!

---

## 📸 Screenshots & Workflows

### Main Workflows

#### 1. **Admin Workflow**
```
Login (admin) → Dashboard → User Management → 
Vehicle Setup → Driver Setup → Route Planning → 
Trip Scheduling → Approvals → Reports
```

#### 2. **Supervisor Workflow**
```
Login (supervisor) → Dashboard → 
Control Center (Monitor Trips) → 
Live GPS Tracking → Reports → 
Fuel Log Submission (Pending Approval)
```

#### 3. **Driver Workflow**
```
Login (driver) → Dashboard (View Today's Trips) → 
Track & Fares → Fuel Log Submission → 
Trip History
```

### Key Pages

| Page | Access | Purpose |
|------|--------|---------|
| Dashboard | All | Welcome & statistics overview |
| Control Center | Supervisor, Admin | Real-time operation status management |
| Live GPS Tracking | Supervisor, Admin | Map-based vehicle tracking |
| Trip Scheduling | Supervisor, Admin | Schedule vehicle trips |
| Route Planning | Supervisor, Admin | Create routes with interactive map |
| Vehicles | Supervisor, Admin | Fleet inventory management |
| Drivers | Supervisor, Admin | Driver database & assignments |
| Fuel Logs | Supervisor, Admin, Driver | Track fuel consumption |
| Maintenance | Supervisor, Admin | Log & track maintenance |
| Reports | Supervisor, Admin | Analytics & performance reports |
| Approvals | Admin | Workflow management for submissions |
| User Management | Admin | Create & manage system users |
| Track & Fares | All | View routes and calculate fares |

---

## 🚦 Application Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Login Screen                         │
│              (Username & Password Auth)                 │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐    ┌───▼────┐   ┌────▼─────┐
   │   Admin │    │Supervisor│  │Driver    │
   └────┬────┘    └───┬────┘   └────┬─────┘
        │              │              │
        │         Dashboard    Dashboard
        │         (Supervisor)  (Personal)
        │              │              │
   ┌────▼────────────────┴──────────────────┐
   │  Full Fleet Management System          │
   │  - All Features Available              │
   └────────────────────────────────────────┘
```

---

## 🔧 Configuration

### Database
- **Location**: `srmss_rbac.db` (SQLite)
- **Auto-initialization**: Yes (on first run)
- **Seed Data**: Included (2 vehicles, 1 route, 3 users)

### Server
- **Host**: `localhost`
- **Port**: `5000`
- **Debug Mode**: `True` (development)

### Maps
- **Tile Provider**: OpenStreetMap
- **Default Location**: Colombo, Sri Lanka (6.9271, 79.8612)
- **Routing Engine**: OSRM (Open Source Routing Machine)

---

## 🐛 Troubleshooting

### Application won't start
```bash
# Ensure Flask is installed
pip install flask

# Check Python version
python --version  # Should be 3.7+
```

### Database errors
```bash
# Delete existing database to reinitialize
rm srmss_rbac.db

# Restart application
python app.py
```

### Port 5000 already in use
```bash
# Modify app.py last line:
# Change: app.run(debug=True, port=5000)
# To:     app.run(debug=True, port=5001)
```

### GPS simulation not working
- Ensure trip status is "Ongoing"
- Check browser console for JavaScript errors
- Verify threading is enabled in Python

---

## 📝 Future Enhancements

- [ ] Email notifications for approvals
- [ ] SMS alerts for trip updates
- [ ] Advanced geofencing
- [ ] Machine learning for route optimization
- [ ] Mobile app (iOS/Android)
- [ ] Real GPS integration (hardware)
- [ ] Payment gateway integration
- [ ] Multi-language support
- [ ] Data export (Excel, PDF)
- [ ] API authentication (JWT tokens)
- [ ] Dockerized deployment
- [ ] Cloud database migration

---

## 📄 License

This project is provided as-is for educational and commercial use.

---

## 👨‍💻 Developer

**Created by**: bposhaka-art  
**Repository**: [SRMSS on GitHub](https://github.com/bposhaka-art/SRMSS)

---

## 📞 Support

For issues, bugs, or feature requests, please open an issue on the [GitHub repository](https://github.com/bposhaka-art/SRMSS/issues).

---

## 🎓 Learning Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Leaflet Maps**: https://leafletjs.com/
- **SQLite**: https://www.sqlite.org/
- **Chart.js**: https://www.chartjs.org/
- **OSRM Routing**: http://project-osrm.org/

---

**Last Updated**: June 2026  
**Version**: 1.0.0
