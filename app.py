from flask import Flask, render_template_string, request, jsonify
import sqlite3
import json
from datetime import datetime
import random
import threading
import time

app = Flask(__name__)
DB_NAME = 'srmss_rbac.db'

# --- HTML TEMPLATE ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SRMSS - Smart Depot Management</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary: #2563eb; --sidebar-bg: #1e293b; --bg: #f1f5f9; --card-bg: #ffffff; 
            --text: #334155; --danger: #ef4444; --success: #16a34a; --warning: #eab308; --purple: #7c3aed;
            --input-bg: #ffffff; --input-border: #e2e8f0; --hover-bg: rgba(255,255,255,0.1);
        }
        [data-theme="dark"] {
            --bg: #0f172a; --card-bg: #1e293b; --text: #cbd5e1; --input-bg: #334155; --input-border: #475569;
            --sidebar-bg: #020617;
        }
        body { margin: 0; font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); height: 100vh; overflow: hidden; transition: 0.3s; }
        .hidden { display: none !important; }

        /* Layout */
        .app-container { display: flex; height: 100vh; width: 100%; }
        .sidebar { width: 260px; background: var(--sidebar-bg); color: white; display: flex; flex-direction: column; }
        .sidebar-header { padding: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; }
        .sidebar-header h2 { margin: 0; color: var(--primary); font-size: 20px; }
        .theme-switch { cursor: pointer; font-size: 20px; background: none; border: none; color: white; }
        .sidebar ul { list-style: none; padding: 0; margin: 0; overflow-y: auto; flex: 1; }
        .sidebar ul li { padding: 15px 20px; cursor: pointer; font-size: 14px; border-left: 4px solid transparent; }
        .sidebar ul li:hover { background: var(--hover-bg); }
        .sidebar ul li.active { background: var(--hover-bg); border-left-color: var(--primary); font-weight: 600; }
        .sidebar-footer { padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); }
        .logout-btn { width: 100%; padding: 12px; background: rgba(239, 68, 68, 0.2); color: #f87171; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }

        .main-content { flex: 1; padding: 30px; overflow-y: auto; height: 100%; box-sizing: border-box; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 1px solid var(--input-border); padding-bottom: 15px; }
        header h1 { margin: 0; font-size: 24px; }

        /* Components */
        .panel { background: var(--card-bg); padding: 25px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px; }
        .panel h3 { margin-top: 0; margin-bottom: 15px; font-size: 16px; display: flex; justify-content: space-between; align-items: center; }
        
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
        @media (max-width: 1000px) { .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; } }

        .form-row { display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap; }
        .form-row > * { flex: 1; min-width: 150px; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid var(--input-border); background: var(--input-bg); color: var(--text); border-radius: 6px; box-sizing: border-box; font-family: 'Inter'; }
        
        .btn { padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; border: none; color: white; font-size: 13px; display: inline-block; text-decoration: none; text-align: center; }
        .btn-primary { background: var(--primary); }
        .btn-danger { background: var(--danger); }
        .btn-success { background: var(--success); }
        .btn-secondary { background: #64748b; }
        .btn-sm { padding: 6px 12px; font-size: 12px; }
        
        #map { height: 400px; width: 100%; border-radius: 8px; margin-bottom: 15px; border: 1px solid var(--input-border); z-index: 1; }

        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid var(--input-border); font-size: 13px; }
        th { background: rgba(0,0,0,0.03); color: var(--text); font-weight: 600; }
        
        .badge { padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
        .badge-red { background: #fee2e2; color: #991b1b; }
        .badge-green { background: #dcfce7; color: #166534; }
        .badge-yellow { background: #fef9c3; color: #854d0e; }
        .badge-blue { background: #e0f2fe; color: #075985; }
        .badge-purple { background: #f3e8ff; color: #7c3aed; }

        .action-link { color: var(--primary); cursor: pointer; margin-right: 10px; font-size: 12px; font-weight: 600; }
        
        /* Modal Styles */
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; align-items: center; justify-content: center; }
        .modal-content { background: var(--card-bg); padding: 30px; border-radius: 12px; width: 90%; max-width: 500px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        .modal-header { display: flex; justify-content: space-between; margin-bottom: 20px; }
        .modal-header h2 { margin: 0; font-size: 20px; }
        .close-btn { background: none; border: none; font-size: 24px; cursor: pointer; color: var(--text); }

        /* Login Art */
        .login-bg-art { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; overflow: hidden; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); }
        .road-line { position: absolute; height: 4px; background: rgba(255,255,255,0.1); transform: rotate(-45deg); }
        .bus-stop-circle { position: absolute; width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.2); border-radius: 50%; }
        .art-bus { position: absolute; font-size: 40px; opacity: 0.1; animation: drive 20s infinite linear; }
        @keyframes drive { from { transform: translateX(-100px) translateY(100vh); } to { transform: translateX(100vw) translateY(-100px); } }

        /* Dashboard */
        .welcome-banner { background: linear-gradient(135deg, #2563eb, #1e40af); color: white; padding: 30px; border-radius: 12px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; }
        .stat-card { padding: 20px; border-radius: 8px; background: var(--card-bg); box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: center; }
        .stat-card h4 { margin: 0 0 10px 0; font-size: 12px; text-transform: uppercase; opacity: 0.7; letter-spacing: 1px; }
        .stat-card .value { font-size: 28px; font-weight: 700; color: var(--primary); }
        
        .chart-container { position: relative; height: 300px; width: 100%; }
        
        /* GPS Sidebar */
        .tracking-sidebar { width: 300px; background: var(--card-bg); border-right: 1px solid var(--input-border); overflow-y: auto; }
        .vehicle-list-item { padding: 15px; border-bottom: 1px solid var(--input-border); cursor: pointer; }
        .vehicle-list-item:hover { background: rgba(0,0,0,0.03); }

        /* Schedule Timeline */
        .schedule-timeline { border-left: 3px solid var(--primary); margin-left: 20px; padding-left: 20px; }
        .schedule-item { position: relative; margin-bottom: 20px; padding: 15px; background: var(--card-bg); border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .schedule-item::before { content: ''; position: absolute; left: -29px; top: 20px; width: 12px; height: 12px; background: var(--primary); border-radius: 50%; border: 2px solid white; }
    </style>
</head>
<body>

    <!-- LOGIN SCREEN -->
    <div id="login-screen" style="height:100vh; display:flex; align-items:center; justify-content:center; position:relative;">
        <div class="login-bg-art">
            <div class="road-line" style="top: 20%; left: -10%; width: 200%;"></div>
            <div class="road-line" style="top: 50%; left: -10%; width: 200%;"></div>
            <div class="bus-stop-circle" style="top: 20%; left: 20%;"></div>
            <div class="art-bus" style="top: 60%; left: 30%;">🚌</div>
        </div>
        <div style="background:rgba(255,255,255,0.95); padding:40px; border-radius:10px; width:100%; max-width:320px; box-shadow:0 10px 25px rgba(0,0,0,0.3); z-index:10;">
            <h2 style="text-align:center; color:var(--primary); margin-bottom:20px;">🚌 SRMSS Login</h2>
            <input type="text" id="login_user" placeholder="Username" style="width:100%; padding:12px; margin-bottom:15px; border:1px solid #ddd; border-radius:5px; box-sizing:border-box;">
            <input type="password" id="login_pass" placeholder="Password" style="width:100%; padding:12px; margin-bottom:20px; border:1px solid #ddd; border-radius:5px; box-sizing:border-box;">
            <button onclick="attemptLogin()" style="width:100%; padding:12px; background:var(--primary); color:white; border:none; border-radius:5px; cursor:pointer; font-weight:600;">Sign In</button>
        </div>
    </div>

    <!-- APP CONTAINER -->
    <div id="app-container" class="app-container hidden">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>SRMSS</h2>
                <button class="theme-switch" onclick="toggleTheme()">🌙</button>
            </div>
            <div style="padding: 10px 20px; font-size: 12px; opacity: 0.7; border-bottom: 1px solid rgba(255,255,255,0.1);">
                Role: <span id="user-role-display">Role</span>
            </div>
            <ul id="nav-menu">
                <li onclick="loadPage('dashboard')" id="nav-dashboard">Dashboard</li>
                <li onclick="loadPage('control')" id="nav-control" style="display:none;">Control Center</li>
                <li onclick="loadPage('tracking')" id="nav-tracking" style="display:none;">Live GPS Tracking</li>
                <li onclick="loadPage('timetable')" id="nav-timetable" style="display:none;">Trip Scheduling</li>
                <li onclick="loadPage('monitoring')" id="nav-monitoring" style="display:none;">Fleet Monitoring</li>
                <li onclick="loadPage('viewer')" id="nav-viewer" style="display:none;">Track & Fares</li>
                <li onclick="loadPage('routes')" id="nav-routes" style="display:none;">Route Planning</li>
                <li onclick="loadPage('vehicles')" id="nav-vehicles" style="display:none;">Vehicles</li>
                <li onclick="loadPage('drivers')" id="nav-drivers" style="display:none;">Drivers</li>
                <li onclick="loadPage('fuel')" id="nav-fuel" style="display:none;">Fuel Logs</li>
                <li onclick="loadPage('maintenance')" id="nav-maintenance" style="display:none;">Maintenance</li>
                <li onclick="loadPage('reports')" id="nav-reports" style="display:none;">Reports & Analytics</li>
                <li onclick="loadPage('approvals')" id="nav-approvals" style="display:none;">Approvals</li>
                <li onclick="loadPage('users')" id="nav-users" style="display:none;">User Management</li>
            </ul>
            <div class="sidebar-footer">
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
        </nav>

        <main class="main-content">
            <header>
                <h1 id="page-title">Dashboard</h1>
                <div id="header-actions"></div>
            </header>
            <div id="content-area">Loading...</div>
        </main>
    </div>

    <!-- Modal -->
    <div id="edit-modal" class="modal-overlay hidden">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modal-title">Edit</h2>
                <button class="close-btn" onclick="closeModal()">&times;</button>
            </div>
            <div id="modal-body"></div>
            <div style="margin-top: 20px; text-align: right;">
                <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                <button class="btn btn-primary" id="modal-save-btn">Save</button>
            </div>
        </div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        const API = '/api';
        let currentUser = null;
        let map = null;
        let liveTrackingInterval = null;
        let tempRouteData = {};
        let drawnRouteLayer = null;
        let stopMarkersLayer = null;

        // Core
        function toggleTheme() {
            const c = document.documentElement.getAttribute('data-theme');
            document.documentElement.setAttribute('data-theme', c === 'dark' ? 'light' : 'dark');
        }
        async function attemptLogin() {
            const res = await fetch(`${API}/login`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: document.getElementById('login_user').value, password: document.getElementById('login_pass').value })
            });
            const data = await res.json();
            if (data.success) {
                currentUser = data.user;
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('app-container').classList.remove('hidden');
                document.getElementById('user-role-display').innerText = currentUser.role;
                updateMenuVisibility();
                loadPage('dashboard');
            } else { alert("Login Failed"); }
        }
        function logout() {
            if(map) map.remove();
            if(liveTrackingInterval) clearInterval(liveTrackingInterval);
            currentUser = null;
            document.getElementById('app-container').classList.add('hidden');
            document.getElementById('login-screen').style.display = 'flex';
        }
        function updateMenuVisibility() {
            const items = ['dashboard', 'control', 'tracking', 'timetable', 'monitoring', 'viewer', 'routes', 'vehicles', 'drivers', 'fuel', 'maintenance', 'reports', 'approvals', 'users'];
            items.forEach(id => document.getElementById(`nav-${id}`).style.display = 'none');
            
            document.getElementById('nav-dashboard').style.display = 'block';
            document.getElementById('nav-viewer').style.display = 'block';
            
            if(currentUser.role === 'Operational Staff') {
                document.getElementById('nav-reports').style.display = 'block'; 
                document.getElementById('nav-fuel').style.display = 'block'; 
                document.getElementById('nav-maintenance').style.display = 'block';
                document.getElementById('nav-vehicles').style.display = 'block'; 
            }
            if(currentUser.role === 'Administrator') {
                items.forEach(id => document.getElementById(`nav-${id}`).style.display = 'block');
            }
            if(currentUser.role === 'Supervisor') {
                document.getElementById('nav-tracking').style.display = 'block';
                document.getElementById('nav-routes').style.display = 'block';
                document.getElementById('nav-timetable').style.display = 'block';
                document.getElementById('nav-control').style.display = 'block';
                document.getElementById('nav-vehicles').style.display = 'block';
                document.getElementById('nav-drivers').style.display = 'block';
                document.getElementById('nav-fuel').style.display = 'block';
                document.getElementById('nav-maintenance').style.display = 'block';
                document.getElementById('nav-reports').style.display = 'block';
            }
        }
        function loadPage(page) {
            if (map) { map.remove(); map = null; }
            if(liveTrackingInterval) clearInterval(liveTrackingInterval);
            
            document.querySelectorAll('#nav-menu li').forEach(el => el.classList.remove('active'));
            document.getElementById(`nav-${page}`).classList.add('active');

            const content = document.getElementById('content-area');
            const title = document.getElementById('page-title');
            const isAdmin = (currentUser && currentUser.role === 'Administrator');
            const isSupervisor = (currentUser && currentUser.role === 'Supervisor');
            const canEdit = (isAdmin || isSupervisor);

            switch(page) {
                case 'dashboard': renderDashboard(title, content); break;
                case 'control': renderControlCenter(title, content); break;
                case 'tracking': renderLiveTracking(title, content); break;
                case 'timetable': renderTimetable(title, content, canEdit); break;
                case 'monitoring': renderMonitoring(title, content); break;
                case 'routes': renderRoutes(title, content, canEdit); break;
                case 'viewer': renderViewer(title, content); break;
                case 'vehicles': renderVehicles(title, content, true); break;
                case 'drivers': renderDrivers(title, content, true); break;
                case 'fuel': renderFuel(title, content, true, isAdmin); break;
                case 'maintenance': renderMaintenance(title, content, true); break;
                case 'users': renderUsers(title, content, isAdmin); break;
                case 'approvals': renderApprovals(title, content, isAdmin); break;
                case 'reports': renderReports(title, content); break;
            }
        }

        async function apiGet(endpoint) { return await (await fetch(endpoint)).json(); }
        async function apiPost(endpoint, data) { return await fetch(endpoint, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) }); }
        async function apiPut(endpoint, data) { return await fetch(endpoint, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) }); }
        async function apiDel(endpoint) { return await fetch(endpoint, { method: 'DELETE' }); }
        
        function openModal(title, html, onSave) {
            document.getElementById('modal-title').innerText = title;
            document.getElementById('modal-body').innerHTML = html;
            document.getElementById('edit-modal').classList.remove('hidden');
            document.getElementById('modal-save-btn').onclick = onSave;
        }
        function closeModal() { document.getElementById('edit-modal').classList.add('hidden'); }

        // --- 1. DASHBOARD ---
        async function renderDashboard(title, container) {
            title.innerText = "Home";
            const stats = await apiGet(`${API}/stats`);
            const operations = await apiGet(`${API}/operations/today`);
            
            const banner = `<div class="welcome-banner"><div><h1>Welcome, ${currentUser.username}!</h1><p>Role: ${currentUser.role}</p></div></div>`;

            if(currentUser.role === 'Operational Staff') {
                 container.innerHTML = banner + `<div class="panel"><p>Loading schedule...</p></div>`;
                 const did = currentUser.driver_id;
                 if(!did) { container.innerHTML += `<div class="panel">No driver profile linked.</div>`; return; }
                 const history = await apiGet(`${API}/driver/history/${did}`);
                 const todayOps = await apiGet(`${API}/driver/today/${did}`);
                 let timelineHtml = (todayOps || []).map(op => `
                    <div class="schedule-item">
                        <h4>${op.departure_time} - ${op.route_name}</h4>
                        <p>Bus: ${op.registration_no} (${op.type})</p>
                        <p>Status: <span class="badge ${op.status === 'Completed' ? 'badge-green' : 'badge-blue'}">${op.status}</span></p>
                    </div>
                 `).join('');
                 
                 let html = `
                    <div class="grid-3" style="margin-bottom:20px;">
                        <div class="stat-card"><h4>Assigned Today</h4><div class="value">${todayOps.length}</div></div>
                        <div class="stat-card"><h4>Total History</h4><div class="value">${history.total_trips}</div></div>
                        <div class="stat-card"><h4>Completed</h4><div class="value">${history.completed_trips}</div></div>
                    </div>
                    <div class="panel"><h3>Today's Assignments</h3><div class="schedule-timeline">${timelineHtml || '<p>No assignments.</p>'}</div></div>`;
                 container.innerHTML = banner + html;
                 return;
            }

            let adminCharts = '';
            if(currentUser.role === 'Administrator') {
                adminCharts = `
                    <div class="grid-2">
                        <div class="panel"><h3>Fleet Utilization</h3><div class="chart-container"><canvas id="chart-fleet"></canvas></div></div>
                        <div class="panel"><h3>Trip Status Distribution</h3><div class="chart-container"><canvas id="chart-trips"></canvas></div></div>
                    </div>`;
            }

            const tripList = (operations || []).slice(0, 5).map(op => {
                const badge = op.status === 'Ongoing' ? 'badge-green' : 'badge-blue';
                return `<div style="padding:8px; border-bottom:1px solid var(--input-border);">${op.route_name} <span class="badge ${badge}" style="float:right">${op.status}</span></div>`;
            }).join('');

            container.innerHTML = banner + 
            `<div class="grid-4">
                <div class="stat-card"><h4>Vehicles</h4><div class="value">${stats.vehicles}</div></div>
                <div class="stat-card"><h4>Drivers</h4><div class="value">${stats.drivers}</div></div>
                <div class="stat-card"><h4>Trips Today</h4><div class="value">${stats.trips}</div></div>
                <div class="stat-card"><h4>Pending</h4><div class="value">${stats.pending_items}</div></div>
            </div>
            <div class="grid-2">
                <div class="panel"><h3>Today's Schedule</h3>${tripList || 'None'}</div>
                <div class="panel"><h3>Quick Actions</h3>
                    <button class="btn btn-primary" onclick="loadPage('control')">Control Center</button>
                    <button class="btn btn-secondary" onclick="loadPage('tracking')">Live Map</button>
                </div>
            </div>
            ${adminCharts}`;

            if(currentUser.role === 'Administrator') {
                setTimeout(() => {
                    new Chart(document.getElementById('chart-fleet'), {
                        type: 'bar', data: { labels: ['Total', 'Active', 'Maintenance'], datasets: [{ label: 'Vehicles', data: [stats.vehicles, stats.active_now, stats.maintenance_count || 2], backgroundColor: ['#64748b', '#2563eb', '#ef4444'] }] }, options: { responsive: true, maintainAspectRatio: false }
                    });
                    new Chart(document.getElementById('chart-trips'), {
                        type: 'doughnut', data: { labels: ['Completed', 'Delayed', 'Scheduled'], datasets: [{ data: [stats.completed_trips || 0, stats.delayed_trips || 0, (stats.trips - (stats.completed_trips || 0) - (stats.delayed_trips || 0))], backgroundColor: ['#16a34a', '#ef4444', '#eab308'] }] }, options: { responsive: true, maintainAspectRatio: false }
                    });
                }, 100);
            }
        }

        // --- 2. TIMETABLE ---
        async function renderTimetable(title, container, canEdit) {
            title.innerText = "Trip Scheduling";
            const routes = await apiGet(`${API}/routes`);
            const vehicles = await apiGet(`${API}/vehicles`);
            const drivers = await apiGet(`${API}/drivers`);
            
            const rOpts = routes.map(r => `<option value="${r.id}">${r.route_name}</option>`).join('');
            const vOpts = vehicles.map(v => `<option value="${v.id}">${v.registration_no}</option>`).join('');
            const dOpts = drivers.map(d => `<option value="${d.id}">${d.name}</option>`).join('');

            container.innerHTML = `
                <div class="panel">
                    <h3>Schedule New Trip</h3>
                    <div class="form-row">
                        <select id="tt_route"><option value="">Select Route</option>${rOpts}</select>
                        <select id="tt_vehicle"><option value="">Select Vehicle</option>${vOpts}</select>
                        <select id="tt_driver"><option value="">Select Driver</option>${dOpts}</select>
                    </div>
                    <div class="form-row">
                        <input type="date" id="tt_date">
                        <input type="time" id="tt_time">
                        ${canEdit ? `<button class="btn btn-primary" onclick="scheduleTrip()">Assign Trip</button>` : ''}
                    </div>
                    <div id="sched-msg" style="margin-top:10px; font-weight:600;"></div>
                </div>
                <div class="panel">
                    <h3>Upcoming Schedules</h3>
                    <div id="sched-list"></div>
                </div>`;
            
            document.getElementById('tt_date').value = new Date().toISOString().split('T')[0];
            loadSchedules();
        }

        async function scheduleTrip() {
            const payload = {
                route_id: document.getElementById('tt_route').value,
                vehicle_id: document.getElementById('tt_vehicle').value,
                driver_id: document.getElementById('tt_driver').value,
                date: document.getElementById('tt_date').value,
                time: document.getElementById('tt_time').value
            };

            const res = await apiPost(`${API}/operations/schedule`, payload);
            const data = await res.json();
            
            const msgDiv = document.getElementById('sched-msg');
            if(data.success) {
                msgDiv.innerHTML = `<span style="color:var(--success);">Trip Scheduled Successfully!</span>`;
                loadSchedules();
            } else {
                msgDiv.innerHTML = `<span style="color:var(--danger);">Error: ${data.message}</span>`;
            }
        }

        async function loadSchedules() {
            const today = new Date().toISOString().split('T')[0];
            const ops = await apiGet(`${API}/operations/date/${today}`);
            const container = document.getElementById('sched-list');
            if(!ops || ops.length === 0) {
                container.innerHTML = '<p>No trips scheduled for today.</p>';
                return;
            }
            let html = '<table><thead><tr><th>Time</th><th>Route</th><th>Bus</th><th>Driver</th><th>Status</th></tr></thead><tbody>';
            ops.forEach(o => {
                html += `<tr>
                    <td>${o.departure_time}</td>
                    <td>${o.route_name}</td>
                    <td>${o.registration_no}</td>
                    <td>${o.driver_name}</td>
                    <td><span class="badge badge-blue">${o.status}</span></td>
                </tr>`;
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        }

        // --- 3. MAINTENANCE (FIXED APPROVAL) ---
        async function renderMaintenance(title, container, canEdit) {
            title.innerText = "Maintenance";
            const vehicles = await apiGet(`${API}/vehicles`);
            const drivers = await apiGet(`${API}/drivers`);
            const items = await apiGet(`${API}/maintenance`);
            
            const vOpts = vehicles.map(v => `<option value="${v.id}">${v.registration_no}</option>`).join('');
            const dOpts = drivers.map(d => `<option value="${d.id}">${d.name}</option>`).join('');

            const rows = items.map(i => `<tr>
                <td>${i.date}</td>
                <td>${i.registration_no || 'N/A'}</td>
                <td>${i.driver_name || 'N/A'}</td>
                <td>${i.description}</td>
                <td>Rs. ${i.cost || 0}</td>
                <td><span class="badge ${i.status === 'Completed' ? 'badge-green' : 'badge-yellow'}">${i.status}</span></td>
            </tr>`).join('');

            container.innerHTML = `
                <div class="panel">
                    <h3>Add Maintenance Record</h3>
                    <div class="form-row">
                        <select id="m_vehicle"><option value="">Vehicle</option>${vOpts}</select>
                        <select id="m_driver"><option value="">Driver (Optional)</option>${dOpts}</select>
                        <input type="date" id="m_date" value="${new Date().toISOString().split('T')[0]}">
                    </div>
                    <div class="form-row">
                        <input type="text" id="m_desc" placeholder="Description / Issue">
                        <input type="number" id="m_cost" placeholder="Cost (Rs.)">
                        <button class="btn btn-primary" onclick="saveMaintenance()">Submit</button>
                    </div>
                </div>
                <div class="panel">
                    <h3>History</h3>
                    <table><thead><tr><th>Date</th><th>Vehicle</th><th>Driver</th><th>Details</th><th>Cost</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table>
                </div>`;
        }

        async function saveMaintenance() {
            const payload = {
                vehicle_id: document.getElementById('m_vehicle').value,
                driver_id: document.getElementById('m_driver').value,
                date: document.getElementById('m_date').value,
                description: document.getElementById('m_desc').value,
                cost: document.getElementById('m_cost').value
            };
            
            // Logic: If Admin, direct entry. Else, send to approval.
            if(currentUser.role === 'Administrator') {
                await apiPost(`${API}/maintenance`, payload);
                alert("Record Added Directly.");
            } else {
                await apiPost(`${API}/approvals`, { type: 'maintenance', message: `Maintenance: ${payload.description}`, data: payload });
                alert("Request sent for Approval.");
            }
            loadPage('maintenance');
        }

        // --- 4. FUEL LOGS ---
        async function renderFuel(title, container, canEdit, isAdmin) {
            title.innerText = "Fuel Logs";
            const items = await apiGet(`${API}/fuel`);
            const vehicles = await apiGet(`${API}/vehicles`);
            
            const rows = items.map(i => `<tr>
                <td>${i.date}</td>
                <td>${i.registration_no}</td>
                <td>${i.liters}L</td>
                <td>Rs. ${i.cost}</td>
                <td><span class="badge ${i.status === 'Approved' ? 'badge-green' : 'badge-yellow'}">${i.status}</span></td>
            </tr>`).join('');

            const vOpts = vehicles.map(v => `<option value="${v.id}">${v.registration_no}</option>`).join('');

            container.innerHTML = `
                <div class="panel">
                    <h3>Log Fuel</h3>
                    <div class="form-row">
                        <select id="f_vehicle" style="flex:2"><option value="">Select Vehicle</option>${vOpts}</select>
                        <input type="number" id="f_liters" placeholder="Liters" style="flex:1">
                        <input type="number" id="f_cost" placeholder="Cost" style="flex:1">
                        <button class="btn btn-primary" onclick="saveFuel()">Submit</button>
                    </div>
                </div>
                <div class="panel">
                    <h3>Fuel History</h3>
                    <table><thead><tr><th>Date</th><th>Vehicle</th><th>Liters</th><th>Cost</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table>
                </div>`;
        }

        async function saveFuel() {
            const payload = {
                vehicle_id: document.getElementById('f_vehicle').value,
                liters: document.getElementById('f_liters').value,
                cost: document.getElementById('f_cost').value
            };
            if(currentUser.role === 'Administrator') {
                await apiPost(`${API}/fuel/direct`, payload);
            } else {
                await apiPost(`${API}/fuel`, payload);
            }
            alert("Fuel Log Submitted");
            loadPage('fuel');
        }

        // --- 5. LIVE GPS TRACKING ---
        async function renderLiveTracking(title, container) {
            title.innerText = "Live Fleet Tracking";
            container.innerHTML = `
                <div style="display:flex; height: calc(100vh - 130px);">
                    <div class="tracking-sidebar" style="flex:0 0 300px;">
                        <div style="padding:15px; border-bottom:1px solid var(--input-border);"><h3>Active Vehicles</h3></div>
                        <div id="vehicle-list-sidebar"></div>
                    </div>
                    <div style="flex:1; position:relative;">
                        <div id="map" style="height:100%; width:100%;"></div>
                    </div>
                </div>`;
            
            map = L.map('map').setView([6.9271, 79.8612], 13);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
            
            updateLiveMap();
            liveTrackingInterval = setInterval(updateLiveMap, 3000);
        }

        async function updateLiveMap() {
            if(!map) return;
            const locations = await apiGet(`${API}/gps/live`);
            const sidebar = document.getElementById('vehicle-list-sidebar');
            
            if(!locations) return;

            let sidebarHtml = '';
            locations.forEach(l => {
                sidebarHtml += `
                    <div class="vehicle-list-item" onclick="focusVehicle(${l.lat}, ${l.lon})">
                        <strong>${l.registration_no}</strong><br>
                        <span style="font-size:11px; opacity:0.8;">Route: ${l.route_name}</span><br>
                        <span style="font-size:11px; color:var(--success);">Live • ${l.speed} km/h</span>
                    </div>`;
            });
            if(sidebar) sidebar.innerHTML = sidebarHtml || '<div style="padding:15px; opacity:0.6;">No active trips.</div>';

            map.eachLayer((layer) => {
                if(layer instanceof L.Marker) map.removeLayer(layer);
            });

            locations.forEach(loc => {
                if(loc.lat && loc.lon) {
                    L.marker([loc.lat, loc.lon]).addTo(map).bindPopup(`<b>${loc.registration_no}</b><br>Speed: ${loc.speed} km/h`);
                }
            });
        }

        function focusVehicle(lat, lon) {
            if(map) map.setView([lat, lon], 15);
        }

        // --- 6. CONTROL CENTER ---
        async function renderControlCenter(title, container) {
            title.innerText = "Control Center";
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('header-actions').innerHTML = `<input type="date" id="cc-date" value="${today}" onchange="loadControlData()">`;
            container.innerHTML = `<div id="cc-stats" class="grid-4" style="margin-bottom:20px;"></div><div id="cc-list"></div>`;
            loadControlData();
        }

        async function loadControlData() {
            const dateVal = document.getElementById('cc-date').value;
            const operations = await apiGet(`${API}/operations/date/${dateVal}`);
            
            let stats = { completed: 0, delayed: 0, ongoing: 0, scheduled: 0 };
            (operations || []).forEach(op => {
                if(op.status === 'Completed') stats.completed++;
                else if(op.status === 'Delayed') stats.delayed++;
                else if(op.status === 'Ongoing') stats.ongoing++;
                else stats.scheduled++;
            });

            document.getElementById('cc-stats').innerHTML = `
                <div class="stat-card"><h4>Completed</h4><div class="value" style="color:var(--success);">${stats.completed}</div></div>
                <div class="stat-card"><h4>Delayed</h4><div class="value" style="color:var(--danger);">${stats.delayed}</div></div>
                <div class="stat-card"><h4>Ongoing</h4><div class="value" style="color:var(--primary);">${stats.ongoing}</div></div>
                <div class="stat-card"><h4>Scheduled</h4><div class="value" style="color:var(--warning);">${stats.scheduled}</div></div>
            `;

            const tripCards = (operations || []).map(op => `
                <div class="panel" style="margin-bottom: 10px;">
                    <div style="display:flex; justify-content:space-between;">
                        <div><h3 style="margin:0;">${op.route_name}</h3><p style="opacity:0.8">${op.registration_no} • ${op.driver_name} • ${op.departure_time}</p></div>
                        <span class="badge badge-blue">${op.status}</span>
                    </div>
                    <div style="margin-top:15px; display:flex; gap:10px;">
                        <button class="btn btn-sm btn-success" onclick="updateTripStatus(${op.id}, 'Completed')">Complete</button>
                        <button class="btn btn-sm btn-primary" onclick="updateTripStatus(${op.id}, 'Ongoing')">Start Trip</button>
                        <button class="btn btn-sm btn-danger" onclick="updateTripStatus(${op.id}, 'Delayed')">Delay</button>
                    </div>
                </div>
            `).join('');

            document.getElementById('cc-list').innerHTML = tripCards || '<div class="panel">No operations.</div>';
        }

        async function updateTripStatus(id, status) {
            await apiPost(`${API}/operations/status/${id}`, { status: status });
            if(status === 'Ongoing') {
                await apiPost(`${API}/gps/start/${id}`, {});
                alert("Trip Started. GPS Simulation Active.");
            }
            loadControlData();
        }

        // --- 7. VEHICLES ---
        async function renderVehicles(title, container, canEdit) {
            title.innerText = "Vehicles";
            const items = await apiGet(`${API}/vehicles`);
            const rows = items.map(i => `<tr>
                <td>${i.registration_no}</td>
                <td>${i.type}</td>
                <td>${i.capacity}</td>
                <td>${i.mileage || 0}</td>
                <td><span class="action-link" onclick="openVehicleEditor(${i.id}, '${i.registration_no}', '${i.type}', ${i.capacity}, ${i.mileage || 0})">Edit</span></td>
            </tr>`).join('');
            
            container.innerHTML = `
                <div class="panel">
                    <h3>Add Vehicle</h3>
                    <div class="form-row">
                        <input type="text" id="v_reg" placeholder="Reg"><input type="text" id="v_type" placeholder="Type"><input type="number" id="v_cap" placeholder="Cap"><button class="btn btn-primary" onclick="saveVehicle()">Add</button>
                    </div>
                </div>
                <div class="panel">
                    <table><thead><tr><th>Reg</th><th>Type</th><th>Cap</th><th>Mile</th><th>Actions</th></tr></thead><tbody>${rows}</tbody></table>
                </div>`;
        }
        
        function openVehicleEditor(id, reg, type, cap, mile) {
            const html = `<input type="hidden" id="edit_v_id" value="${id}">
                <div class="form-row"><label>Reg No</label><input type="text" id="edit_v_reg" value="${reg}"></div>
                <div class="form-row"><label>Type</label><input type="text" id="edit_v_type" value="${type}"></div>
                <div class="form-row"><label>Capacity</label><input type="number" id="edit_v_cap" value="${cap}"></div>
                <div class="form-row"><label>Mileage</label><input type="number" id="edit_v_mile" value="${mile}"></div>`;
            openModal("Edit Vehicle", html, async () => {
                const payload = { 
                    id: document.getElementById('edit_v_id').value, 
                    registration_no: document.getElementById('edit_v_reg').value, 
                    type: document.getElementById('edit_v_type').value, 
                    capacity: document.getElementById('edit_v_cap').value, 
                    mileage: document.getElementById('edit_v_mile').value 
                };
                await apiPost(`${API}/vehicles/update/${payload.id}`, payload);
                closeModal();
                loadPage('vehicles');
            });
        }

        async function saveVehicle() { 
            await apiPost(`${API}/vehicles`, { registration_no: document.getElementById('v_reg').value, type: document.getElementById('v_type').value, capacity: document.getElementById('v_cap').value }); 
            loadPage('vehicles'); 
        }

        // --- 8. DRIVERS ---
        async function renderDrivers(title, container, canEdit) {
            title.innerText = "Drivers";
            const items = await apiGet(`${API}/drivers`);
            const rows = items.map(i => `<tr>
                <td>${i.name}</td><td>${i.license_no}</td><td>${i.contact}</td>
                <td><span class="action-link" onclick="openDriverEditor(${i.id}, '${i.name}', '${i.license_no}', '${i.contact}')">Edit</span></td>
            </tr>`).join('');
            container.innerHTML = `
                <div class="panel"><h3>Add Driver</h3><div class="form-row"><input type="text" id="d_name" placeholder="Name"><input type="text" id="d_lic" placeholder="License"><input type="text" id="d_con" placeholder="Contact"><button class="btn btn-primary" onclick="saveDriver()">Add</button></div></div>
                <div class="panel"><table><thead><tr><th>Name</th><th>License</th><th>Contact</th><th>Actions</th></tr></thead><tbody>${rows}</tbody></table></div>`;
        }

        function openDriverEditor(id, name, lic, contact) {
            const html = `<input type="hidden" id="edit_d_id" value="${id}">
                <div class="form-row"><label>Name</label><input type="text" id="edit_d_name" value="${name}"></div>
                <div class="form-row"><label>License</label><input type="text" id="edit_d_lic" value="${lic}"></div>
                <div class="form-row"><label>Contact</label><input type="text" id="edit_d_contact" value="${contact}"></div>`;
            openModal("Edit Driver", html, async () => {
                const payload = {
                    id: document.getElementById('edit_d_id').value,
                    name: document.getElementById('edit_d_name').value,
                    license_no: document.getElementById('edit_d_lic').value,
                    contact: document.getElementById('edit_d_contact').value
                };
                await apiPost(`${API}/drivers/update/${payload.id}`, payload);
                closeModal();
                loadPage('drivers');
            });
        }

        async function saveDriver() { await apiPost(`${API}/drivers`, { name: document.getElementById('d_name').value, license_no: document.getElementById('d_lic').value, contact: document.getElementById('d_con').value }); loadPage('drivers'); }

        // --- 9. ROUTE PLANNING ---
        async function renderRoutes(title, container, canEdit) {
            title.innerText = "Route Planning";
            const items = await apiGet(`${API}/routes`);
            const rows = items.map(i => `<tr><td>${i.route_name}</td><td>${i.distance_km} km</td><td>${(JSON.parse(i.stops || '[]').length)}</td></tr>`).join('');
            
            container.innerHTML = `
                <div class="panel">
                    <h3>Define Route</h3>
                    <div style="font-size:12px; color:var(--danger); margin-bottom:10px;">1. Click Start. 2. Click End. 3. Click Blue Line to add Stops.</div>
                    <div id="map"></div>
                    <div class="form-row">
                        <input type="text" id="r_name" placeholder="Route Name">
                        <input type="text" id="r_dist" placeholder="Distance" readonly style="background:var(--input-bg);">
                    </div>
                    <div id="stops-list" style="margin-bottom:15px;">Click map to start.</div>
                    ${canEdit ? `<button class="btn btn-primary" onclick="saveRoute()">Save Route</button>` : ''}
                </div>
                <div class="panel"><h3>Saved Routes</h3><table><thead><tr><th>Name</th><th>Dist</th><th>Stops</th></tr></thead><tbody>${rows}</tbody></table></div>`;
            initRouteMap();
        }

        function initRouteMap() {
            map = L.map('map').setView([6.9271, 79.8612], 12);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
            drawnRouteLayer = L.layerGroup().addTo(map);
            stopMarkersLayer = L.layerGroup().addTo(map);
            tempRouteData = { start: null, end: null, geometry: [], stops: [] };

            map.on('click', function(e) {
                if(!tempRouteData.start) {
                    tempRouteData.start = e.latlng;
                    L.marker(e.latlng).addTo(drawnRouteLayer).bindPopup("Start").openPopup();
                } else if(!tempRouteData.end) {
                    tempRouteData.end = e.latlng;
                    L.marker(e.latlng).addTo(drawnRouteLayer).bindPopup("End").openPopup();
                    calculateRoute();
                }
            });
        }

        async function calculateRoute() {
            const start = tempRouteData.start; const end = tempRouteData.end;
            const url = `https://router.project-osrm.org/route/v1/driving/${start.lng},${start.lat};${end.lng},${end.lat}?overview=full&geometries=geojson`;
            try {
                const res = await fetch(url); const data = await res.json();
                if(data.routes && data.routes.length > 0) {
                    const route = data.routes[0];
                    document.getElementById('r_dist').value = (route.distance / 1000).toFixed(2);
                    const coords = route.geometry.coordinates.map(c => [c[1], c[0]]); 
                    tempRouteData.geometry = coords;
                    
                    drawnRouteLayer.clearLayers(); L.marker(start).addTo(drawnRouteLayer); L.marker(end).addTo(drawnRouteLayer);
                    const polyline = L.polyline(coords, {color: '#2563eb', weight: 5}).addTo(drawnRouteLayer);
                    map.fitBounds(polyline.getBounds());

                    polyline.on('click', function(e) {
                        L.DomEvent.stopPropagation(e); 
                        const stopName = prompt("Enter Bus Stop Name:"); if(!stopName) return;
                        const fareVal = parseFloat(prompt("Enter Fare (Rs.):")) || 0;
                        L.marker(e.latlng).addTo(stopMarkersLayer);
                        tempRouteData.stops.push({ name: stopName, lat: e.latlng.lat, lon: e.latlng.lng, fare: fareVal });
                        renderStopList();
                    });
                }
            } catch(err) { alert("Route error"); }
        }

        function renderStopList() {
            const container = document.getElementById('stops-list');
            container.innerHTML = '';
            tempRouteData.stops.forEach((s, i) => { 
                container.innerHTML += `<div style="margin-bottom:5px; padding:5px; background:var(--input-bg); border-radius:4px;"><strong>${i+1}. ${s.name}</strong> - Fare: Rs.${s.fare.toFixed(2)}</div>`; 
            });
        }

        async function saveRoute() {
            const payload = {
                route_name: document.getElementById('r_name').value, distance_km: document.getElementById('r_dist').value,
                start_point: "Start", end_point: "End", path_geometry: JSON.stringify(tempRouteData.geometry || []), stops: JSON.stringify(tempRouteData.stops || [])
            };
            await apiPost(`${API}/routes`, payload); alert("Route Saved"); loadPage('routes');
        }

        // --- 10. REPORTS ---
        async function renderReports(title, container) {
            title.innerText = "Reports";
            if(currentUser.role === 'Operational Staff') {
                 container.innerHTML = `<div class="panel"><h3>My History</h3><p>Fetching...</p></div>`; return;
            }
            const data = await apiGet(`${API}/reports/summary`);
            if (!data) { container.innerHTML = `<div class="panel">Error</div>`; return; }

            container.innerHTML = `
                <div id="printArea">
                    <div class="grid-3">
                        <div class="panel"><h3>Total Fuel Cost</h3><div style="font-size:24px; font-weight:700;">Rs. ${data.total_fuel_cost || 0}</div></div>
                        <div class="panel"><h3>Total Maintenance</h3><div style="font-size:24px; font-weight:700;">Rs. ${data.total_maint_cost || 0}</div></div>
                        <div class="panel"><h3>Trip Completion Rate</h3><div style="font-size:24px; font-weight:700;">${data.completion_rate || 0}%</div></div>
                    </div>
                    <div class="panel">
                        <h3>Monthly Performance Summary</h3>
                        <table><thead><tr><th>Metric</th><th>Value</th></tr></thead>
                        <tbody>
                            <tr><td>Total Scheduled Trips</td><td>${data.total_trips || 0}</td></tr>
                            <tr><td>Completed Trips</td><td>${data.completed_trips || 0}</td></tr>
                            <tr><td>Fuel Consumed (L)</td><td>${data.total_liters || 0}</td></tr>
                        </tbody></table>
                    </div>
                </div>
                <button class="btn btn-primary no-print" onclick="window.print()">Export PDF / Print</button>`;
        }

        // --- 11. MONITORING ---
        async function renderMonitoring(title, container) {
            title.innerText = "Fleet Monitoring";
            const data = await apiGet(`${API}/monitoring/vehicles`);
            if(!data) { container.innerHTML = "<div class='panel'>Error loading data.</div>"; return; }
            const rows = data.map(v => {
                let statusBadge = v.trip_count == 0 ? '<span class="badge badge-red">Unassigned</span>' : '<span class="badge badge-green">Active</span>';
                return `<tr><td>${v.registration_no}</td><td>${v.type}</td><td>${v.capacity}</td><td>${v.mileage || 0} km</td><td>${v.trip_count}</td><td>${statusBadge}</td></tr>`;
            }).join('');
            container.innerHTML = `<div class="panel"><h3>Vehicle Utilization</h3><table><thead><tr><th>Reg No</th><th>Type</th><th>Cap</th><th>Mileage</th><th>Trips</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table></div>`;
        }

        // --- 12. APPROVALS (UPDATED) ---
        async function renderApprovals(title, container, isAdmin) {
            if(!isAdmin) return;
            title.innerText = "Approvals";
            const pending = await apiGet(`${API}/approvals/pending`);
            
            const rows = pending.map(p => {
                let details = '';
                try { if(p.data) details = JSON.parse(p.data).description || JSON.parse(p.data).liters + 'L'; } catch(e) {}
                
                return `<tr>
                    <td><span class="badge badge-purple">${p.type}</span></td>
                    <td>${p.message}</td>
                    <td>${details}</td>
                    <td>
                        <button class="btn btn-sm btn-success" onclick="approveItem(${p.id})">Approve</button>
                        <button class="btn btn-sm btn-danger" onclick="rejectItem(${p.id})">Reject</button>
                    </td>
                </tr>`;
            }).join('');

            container.innerHTML = `
                <div class="panel">
                    <table><thead><tr><th>Type</th><th>Info</th><th>Details</th><th>Action</th></tr></thead>
                    <tbody>${rows || '<tr><td colspan="4">No pending items</td></tr>'}</tbody>
                </div>`;
        }
        
        async function approveItem(id) { 
            await apiPost(`${API}/approvals/approve/${id}`, {}); 
            loadPage('approvals'); 
        }
        
        async function rejectItem(id) { 
            await apiPost(`${API}/approvals/reject/${id}`, {}); 
            loadPage('approvals'); 
        }

        // --- 13. USER MANAGEMENT ---
        async function renderUsers(title, container, isAdmin) {
            if(!isAdmin) return;
            title.innerText = "User Management";
            const users = await apiGet(`${API}/users`);
            
            const rows = users.map(u => `
                <tr>
                    <td>${u.username}</td>
                    <td>
                        <select id="role-${u.id}" onchange="updateUserRole(${u.id})">
                            <option ${u.role==='Operational Staff'?'selected':''}>Operational Staff</option>
                            <option ${u.role==='Supervisor'?'selected':''}>Supervisor</option>
                            <option ${u.role==='Administrator'?'selected':''}>Administrator</option>
                        </select>
                    </td>
                    <td><span class="action-link" style="color:var(--danger);" onclick="deleteUser(${u.id})">Delete</span></td>
                </tr>
            `).join('');
            
            container.innerHTML = `
                <div class="panel">
                    <h3>Create User</h3>
                    <div class="form-row">
                        <input type="text" id="u_name" placeholder="Username">
                        <input type="password" id="u_pass" placeholder="Password">
                        <select id="u_role">
                            <option>Operational Staff</option>
                            <option>Supervisor</option>
                            <option>Administrator</option>
                        </select>
                        <button class="btn btn-primary" onclick="createUser()">Add</button>
                    </div>
                </div>
                <div class="panel">
                    <h3>Manage Users</h3>
                    <table><thead><tr><th>User</th><th>Role</th><th>Action</th></tr></thead><tbody>${rows}</tbody></table>
                </div>`;
        }

        async function createUser() {
            const payload = { username: document.getElementById('u_name').value, password: document.getElementById('u_pass').value, role: document.getElementById('u_role').value };
            const res = await apiPost(`${API}/users`, payload);
            if(res.ok) loadPage('users');
            else alert("Error creating user (might already exist)");
        }

        async function updateUserRole(id) {
            const newRole = document.getElementById(`role-${id}`).value;
            await apiPut(`${API}/users/${id}`, { role: newRole });
            alert("Role Updated");
        }

        async function deleteUser(id) {
            if(confirm("Are you sure you want to delete this user?")) {
                await apiDel(`${API}/users/${id}`);
                loadPage('users');
            }
        }
        
        // --- 14. TRACK & FARES (FIXED) ---
        let viewerRouteLayer = null;
        async function renderViewer(title, container) {
            title.innerText = "Track & Fares";
            const routes = await apiGet(`${API}/routes`);
            const rOpts = routes.map(r => `<option value="${r.id}">${r.route_name}</option>`).join('');
            
            container.innerHTML = `
                <div class="panel">
                    <h3>Select Route</h3>
                    <select id="v_route_select" onchange="loadRouteViewer()"><option value="">-- Select --</option>${rOpts}</select>
                    <div id="map" style="height:300px; margin-top:15px;"></div>
                </div>
                <div class="panel" id="fare-panel" style="display:none;">
                    <h3>Fare Calculation</h3>
                    <div class="form-row">
                        <select id="v_start_stop"><option value="">Start</option></select>
                        <select id="v_end_stop"><option value="">End</option></select>
                        <button class="btn btn-primary" onclick="calculateViewerFare()">Calculate</button>
                    </div>
                    <div id="fare-result" style="margin-top:15px; font-size:18px; font-weight:bold; color:var(--primary);"></div>
                </div>`;
            
            map = L.map('map').setView([6.9271, 79.8612], 12);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
            viewerRouteLayer = L.layerGroup().addTo(map);
        }

        async function loadRouteViewer() {
            const routeId = document.getElementById('v_route_select').value;
            if(!routeId) return;
            
            const route = await (await fetch(`${API}/routes/${routeId}`)).json();
            
            viewerRouteLayer.clearLayers();
            document.getElementById('fare-panel').style.display = 'none';
            
            if(route.path_geometry) {
                try {
                    const coords = JSON.parse(route.path_geometry);
                    L.polyline(coords, {color: 'blue', weight: 5}).addTo(viewerRouteLayer);
                    map.fitBounds(coords);
                } catch(e) { console.error("Map geometry error", e); }
            }
            
            const stops = JSON.parse(route.stops || '[]');
            const startSelect = document.getElementById('v_start_stop');
            const endSelect = document.getElementById('v_end_stop');
            startSelect.innerHTML = `<option value="start">Start (${route.start_point})</option>`;
            endSelect.innerHTML = '';

            stops.forEach((s, idx) => {
                if(s.lat && s.lon) L.marker([s.lat, s.lon]).addTo(viewerRouteLayer).bindPopup(s.name);
                startSelect.innerHTML += `<option value="${idx}">${s.name}</option>`;
                endSelect.innerHTML += `<option value="${idx}">${s.name}</option>`;
            });

            document.getElementById('fare-panel').style.display = 'block';
        }

        function calculateViewerFare() {
            const startVal = document.getElementById('v_start_stop').value;
            const endVal = document.getElementById('v_end_stop').value;
            const routeId = document.getElementById('v_route_select').value;
            
            fetch(`${API}/routes/${routeId}`).then(r=>r.json()).then(route => {
                const stops = JSON.parse(route.stops || '[]');
                let totalFare = 0;
                
                let startIdx = (startVal === 'start') ? -1 : parseInt(startVal);
                let endIdx = parseInt(endVal);

                if(startIdx >= endIdx) {
                    document.getElementById('fare-result').innerHTML = `<span style="color:var(--danger);">Invalid selection</span>`;
                    return;
                }
                
                for(let i = startIdx + 1; i <= endIdx; i++) {
                    if(stops[i]) totalFare += (stops[i].fare || 0);
                }

                document.getElementById('fare-result').innerHTML = `Total Fare: Rs. ${totalFare.toFixed(2)}`;
            });
        }

    </script>
</body>
</html>
'''

# --- BACKEND ---

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Drop tables if they exist to apply new schema
    c.execute('DROP TABLE IF EXISTS operations')
    c.execute('DROP TABLE IF EXISTS maintenance')
    c.execute('DROP TABLE IF EXISTS fuel_logs')
    
    # Schema
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, driver_id INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS drivers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, license_no TEXT, contact TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS vehicles (id INTEGER PRIMARY KEY AUTOINCREMENT, registration_no TEXT, type TEXT, capacity INTEGER, mileage REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS routes (id INTEGER PRIMARY KEY AUTOINCREMENT, route_name TEXT, distance_km REAL, start_point TEXT, end_point TEXT, path_geometry TEXT, stops TEXT)''')
    
    # Operations Table
    c.execute('''CREATE TABLE operations (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        route_id INTEGER, vehicle_id INTEGER, driver_id INTEGER, 
        operation_date TEXT, departure_time TEXT, status TEXT DEFAULT 'Scheduled',
        current_lat REAL, current_lon REAL, speed REAL
    )''')
    
    # Maintenance Table
    c.execute('''CREATE TABLE maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        vehicle_id INTEGER, driver_id INTEGER,
        date TEXT, description TEXT, cost REAL, status TEXT DEFAULT 'Pending'
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS fuel_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle_id INTEGER, date TEXT, liters REAL, cost REAL, status TEXT DEFAULT 'Pending')''')
    c.execute('''CREATE TABLE IF NOT EXISTS approvals (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, data TEXT, message TEXT, status TEXT DEFAULT 'Pending')''')

    # Seed
    try:
        c.execute("INSERT INTO users (username, password, role, driver_id) VALUES ('admin', 'admin', 'Administrator', NULL)")
        c.execute("INSERT INTO users (username, password, role, driver_id) VALUES ('supervisor', 'super', 'Supervisor', NULL)")
        c.execute("INSERT INTO drivers (name, license_no, contact) VALUES ('John Doe', 'DL123', '0771234567')")
        driver_id = c.lastrowid
        c.execute("INSERT INTO users (username, password, role, driver_id) VALUES ('driver', 'driver', 'Operational Staff', ?)", (driver_id,))
        
        c.execute("INSERT INTO vehicles (registration_no, type, capacity, mileage) VALUES ('WP-CAR-1234', 'Bus', 50, 12000)")
        c.execute("INSERT INTO vehicles (registration_no, type, capacity, mileage) VALUES ('WP-CAR-5678', 'Mini-Bus', 20, 5000)")
        
        seed_geom = '[[6.9271, 79.8612], [6.92, 79.87], [6.91, 79.88]]'
        seed_stops = '[{"name":"Stop A", "lat":6.92, "lon":79.87, "fare":10}, {"name":"Stop B", "lat":6.91, "lon":79.88, "fare":20}]'
        c.execute("INSERT INTO routes (route_name, distance_km, start_point, end_point, path_geometry, stops) VALUES (?, ?, ?, ?, ?, ?)",
                  ('Route 101', 15.5, 'Central', 'Airport', seed_geom, seed_stops))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

# GPS Simulation
def simulate_gps(op_id):
    steps = 30
    start_lat, start_lon = 6.9271, 79.8612
    end_lat, end_lon = 6.95, 79.90
    
    lat_step = (end_lat - start_lat) / steps
    lon_step = (end_lon - start_lon) / steps
    
    conn = get_db()
    for i in range(steps):
        time.sleep(2)
        curr_lat = start_lat + (lat_step * (i+1))
        curr_lon = start_lon + (lon_step * (i+1))
        
        conn.execute("UPDATE operations SET current_lat=?, current_lon=?, speed=? WHERE id=?", 
                     (curr_lat, curr_lon, random.randint(20, 40), op_id))
        conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/login', methods=['POST'])
def login():
    d = request.json
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (d['username'], d['password'])).fetchone()
    conn.close()
    if user:
        return jsonify(success=True, user={'username': user['username'], 'role': user['role'], 'driver_id': user['driver_id']})
    return jsonify(success=False)

@app.route('/api/stats')
def stats():
    conn = get_db()
    v = conn.execute('SELECT COUNT(*) FROM vehicles').fetchone()[0]
    d = conn.execute('SELECT COUNT(*) FROM drivers').fetchone()[0]
    t = conn.execute("SELECT COUNT(*) FROM operations WHERE operation_date=date('now')").fetchone()[0]
    p = conn.execute("SELECT COUNT(*) FROM approvals WHERE status='Pending'").fetchone()[0]
    active = conn.execute("SELECT COUNT(*) FROM operations WHERE status='Ongoing'").fetchone()[0]
    maint = conn.execute("SELECT COUNT(*) FROM maintenance WHERE status='Pending'").fetchone()[0]
    completed = conn.execute("SELECT COUNT(*) FROM operations WHERE status='Completed'").fetchone()[0]
    delayed = conn.execute("SELECT COUNT(*) FROM operations WHERE status='Delayed'").fetchone()[0]
    conn.close()
    return jsonify(vehicles=v, drivers=d, trips=t, pending_items=p, active_now=active, maintenance_count=maint, completed_trips=completed, delayed_trips=delayed)

# --- SCHEDULING & OPERATIONS ---

@app.route('/api/operations/schedule', methods=['POST'])
def schedule_op():
    d = request.json
    conn = get_db()
    
    # Conflict Check
    conflict = conn.execute('''
        SELECT * FROM operations 
        WHERE operation_date=? AND departure_time=? AND (driver_id=? OR vehicle_id=?) AND status != 'Cancelled'
    ''', (d['date'], d['time'], d['driver_id'], d['vehicle_id'])).fetchone()
    
    if conflict:
        conn.close()
        return jsonify(success=False, message="Conflict: Driver or Vehicle already assigned at this time.")
    
    conn.execute('''
        INSERT INTO operations (route_id, vehicle_id, driver_id, operation_date, departure_time, status)
        VALUES (?, ?, ?, ?, ?, 'Scheduled')
    ''', (d['route_id'], d['vehicle_id'], d['driver_id'], d['date'], d['time']))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route('/api/operations/today')
def ops_today():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    rows = conn.execute('''
        SELECT o.id, o.status, o.departure_time, o.operation_date,
               r.route_name, v.registration_no, d.name as driver_name, v.type
        FROM operations o
        JOIN routes r ON o.route_id = r.id
        JOIN vehicles v ON o.vehicle_id = v.id
        JOIN drivers d ON o.driver_id = d.id
        WHERE o.operation_date = ?
    ''', (today,)).fetchall()
    return jsonify([dict(ix) for ix in rows])

@app.route('/api/operations/date/<date_val>')
def ops_date(date_val):
    conn = get_db()
    rows = conn.execute('''
        SELECT o.id, o.status, o.departure_time, o.operation_date,
               r.route_name, v.registration_no, d.name as driver_name
        FROM operations o
        JOIN routes r ON o.route_id = r.id
        JOIN vehicles v ON o.vehicle_id = v.id
        JOIN drivers d ON o.driver_id = d.id
        WHERE o.operation_date = ?
    ''', (date_val,)).fetchall()
    return jsonify([dict(ix) for ix in rows])

@app.route('/api/operations/status/<int:id>', methods=['POST'])
def op_status(id):
    status = request.json.get('status')
    conn = get_db()
    conn.execute("UPDATE operations SET status=? WHERE id=?", (status, id))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route('/api/gps/start/<int:op_id>', methods=['POST'])
def start_gps(op_id):
    t = threading.Thread(target=simulate_gps, args=(op_id,))
    t.start()
    return jsonify(success=True)

@app.route('/api/gps/live')
def gps_live():
    conn = get_db()
    rows = conn.execute('''
        SELECT o.id, o.current_lat, o.current_lon, o.speed, v.registration_no, r.route_name
        FROM operations o
        JOIN vehicles v ON o.vehicle_id = v.id
        JOIN routes r ON o.route_id = r.id
        WHERE o.status = 'Ongoing' AND o.current_lat IS NOT NULL
    ''').fetchall()
    return jsonify([dict(ix) for ix in rows])

# --- MAINTENANCE (Direct Admin Save) ---
@app.route('/api/maintenance', methods=['GET', 'POST'])
def maintenance():
    conn = get_db()
    if request.method == 'POST':
        d = request.json
        conn.execute('''
            INSERT INTO maintenance (vehicle_id, driver_id, date, description, cost, status)
            VALUES (?, ?, ?, ?, ?, 'Completed')
        ''', (d.get('vehicle_id'), d.get('driver_id'), d.get('date'), d.get('description'), d.get('cost')))
        conn.commit()
        conn.close()
        return jsonify(success=True)
    
    rows = conn.execute('''
        SELECT m.*, v.registration_no, d.name as driver_name
        FROM maintenance m
        LEFT JOIN vehicles v ON m.vehicle_id = v.id
        LEFT JOIN drivers d ON m.driver_id = d.id
        ORDER BY m.date DESC
    ''').fetchall()
    return jsonify([dict(ix) for ix in rows])

# --- FUEL ---

@app.route('/api/fuel', methods=['GET', 'POST'])
def fuel():
    conn = get_db()
    if request.method == 'POST':
        d = request.json
        conn.execute('INSERT INTO approvals (type, message, data) VALUES (?,?,?)', 
                     ('fuel', f"Fuel Log: {d['liters']}L", json.dumps(d)))
        conn.commit()
        conn.close()
        return jsonify(success=True)
    
    rows = conn.execute('''
        SELECT f.*, v.registration_no FROM fuel_logs f
        JOIN vehicles v ON f.vehicle_id = v.id
        ORDER BY f.date DESC
    ''').fetchall()
    return jsonify([dict(ix) for ix in rows])

@app.route('/api/fuel/direct', methods=['POST'])
def fuel_direct():
    d = request.json
    conn = get_db()
    today = datetime.now().strftime('%Y-%m-%d')
    conn.execute('INSERT INTO fuel_logs (vehicle_id, date, liters, cost, status) VALUES (?, ?, ?, ?, "Approved")',
                 (d['vehicle_id'], today, d['liters'], d['cost']))
    conn.commit()
    conn.close()
    return jsonify(success=True)

# --- APPROVALS (UPDATED BACKEND) ---

@app.route('/api/approvals/pending')
def pending_approvals():
    conn = get_db()
    rows = conn.execute("SELECT * FROM approvals WHERE status='Pending'").fetchall()
    return jsonify([dict(ix) for ix in rows])

@app.route('/api/approvals', methods=['POST'])
def create_approval():
    d = request.json
    conn = get_db()
    conn.execute('INSERT INTO approvals (type, message, data) VALUES (?,?,?)', 
                 (d['type'], d['message'], json.dumps(d['data'])))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route('/api/approvals/approve/<int:id>', methods=['POST'])
def approve_item(id):
    conn = get_db()
    item = conn.execute("SELECT * FROM approvals WHERE id=?", (id,)).fetchone()
    if item:
        data = json.loads(item['data'])
        today = datetime.now().strftime('%Y-%m-%d')
        
        if item['type'] == 'fuel':
            conn.execute('INSERT INTO fuel_logs (vehicle_id, date, liters, cost, status) VALUES (?, ?, ?, ?, "Approved")',
                         (data['vehicle_id'], today, data['liters'], data['cost']))
                         
        elif item['type'] == 'maintenance':
            conn.execute('''
                INSERT INTO maintenance (vehicle_id, driver_id, date, description, cost, status)
                VALUES (?, ?, ?, ?, ?, 'Completed')
            ''', (data.get('vehicle_id'), data.get('driver_id'), data.get('date'), data.get('description'), data.get('cost')))
            
    conn.execute("UPDATE approvals SET status='Approved' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route('/api/approvals/reject/<int:id>', methods=['POST'])
def reject_item(id):
    conn = get_db()
    conn.execute("UPDATE approvals SET status='Rejected' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify(success=True)

# --- DICTIONARIES ---

@app.route('/api/vehicles', methods=['GET', 'POST'])
def vehicles():
    conn = get_db()
    if request.method == 'POST':
        d = request.json
        conn.execute("INSERT INTO vehicles (registration_no, type, capacity) VALUES (?,?,?)", (d['registration_no'], d['type'], d.get('capacity',0)))
        conn.commit()
        return jsonify(success=True)
    return jsonify([dict(ix) for ix in conn.execute("SELECT * FROM vehicles").fetchall()])

@app.route('/api/vehicles/update/<int:id>', methods=['POST'])
def update_vehicle(id):
    d = request.json
    conn = get_db()
    conn.execute("UPDATE vehicles SET registration_no=?, type=?, capacity=?, mileage=? WHERE id=?", 
                 (d['registration_no'], d['type'], d['capacity'], d['mileage'], id))
    conn.commit()
    return jsonify(success=True)

@app.route('/api/drivers', methods=['GET', 'POST'])
def drivers():
    conn = get_db()
    if request.method == 'POST':
        d = request.json
        conn.execute("INSERT INTO drivers (name, license_no, contact) VALUES (?,?,?)", (d['name'], d['license_no'], d['contact']))
        conn.commit()
        return jsonify(success=True)
    return jsonify([dict(ix) for ix in conn.execute("SELECT * FROM drivers").fetchall()])

@app.route('/api/drivers/update/<int:id>', methods=['POST'])
def update_driver(id):
    d = request.json
    conn = get_db()
    conn.execute("UPDATE drivers SET name=?, license_no=?, contact=? WHERE id=?", 
                 (d['name'], d['license_no'], d['contact'], id))
    conn.commit()
    return jsonify(success=True)

@app.route('/api/routes', methods=['GET', 'POST'])
def routes():
    conn = get_db()
    if request.method == 'POST':
        d = request.json
        conn.execute("INSERT INTO routes (route_name, distance_km, start_point, end_point, path_geometry, stops) VALUES (?,?,?,?,?,?)",
                     (d['route_name'], d['distance_km'], d.get('start_point',''), d.get('end_point',''), d.get('path_geometry',''), d.get('stops','')))
        conn.commit()
        return jsonify(success=True)
    return jsonify([dict(ix) for ix in conn.execute("SELECT * FROM routes").fetchall()])

@app.route('/api/routes/<int:id>')
def route_detail(id):
    conn = get_db()
    row = conn.execute("SELECT * FROM routes WHERE id=?", (id,)).fetchone()
    return jsonify(dict(row))

@app.route('/api/monitoring/vehicles')
def mon_vehi():
    conn = get_db()
    rows = conn.execute('SELECT v.*, COUNT(o.id) as trip_count FROM vehicles v LEFT JOIN operations o ON v.id = o.vehicle_id GROUP BY v.id').fetchall()
    return jsonify([dict(ix) for ix in rows])

# --- USER MANAGEMENT ---

@app.route('/api/users', methods=['GET', 'POST'])
def handle_users():
    conn = get_db()
    if request.method == 'POST':
        d = request.json
        try:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)", 
                         (d['username'], d['password'], d['role']))
            conn.commit()
            return jsonify(success=True)
        except sqlite3.IntegrityError:
            return jsonify(success=False, message="User exists"), 400
    rows = conn.execute("SELECT id, username, role FROM users").fetchall()
    return jsonify([dict(ix) for ix in rows])

@app.route('/api/users/<int:id>', methods=['PUT', 'DELETE'])
def modify_user(id):
    conn = get_db()
    if request.method == 'PUT':
        d = request.json
        conn.execute("UPDATE users SET role=? WHERE id=?", (d['role'], id))
        conn.commit()
        return jsonify(success=True)
    else:
        conn.execute("DELETE FROM users WHERE id=?", (id,))
        conn.commit()
        return jsonify(success=True)

@app.route('/api/reports/summary')
def reports():
    conn = get_db()
    t = conn.execute("SELECT COUNT(*) FROM operations").fetchone()[0]
    c = conn.execute("SELECT COUNT(*) FROM operations WHERE status='Completed'").fetchone()[0]
    fc = conn.execute("SELECT SUM(cost) FROM fuel_logs WHERE status='Approved'").fetchone()[0] or 0
    mc = conn.execute("SELECT SUM(cost) FROM maintenance").fetchone()[0] or 0
    l = conn.execute("SELECT SUM(liters) FROM fuel_logs WHERE status='Approved'").fetchone()[0] or 0
    rate = (c / t * 100) if t > 0 else 0
    return jsonify(total_trips=t, completed_trips=c, total_fuel_cost=fc, total_maint_cost=mc, total_liters=l, completion_rate=round(rate,1))

@app.route('/api/driver/history/<int:did>')
def d_hist(did):
    conn = get_db()
    t = conn.execute("SELECT COUNT(*) FROM operations WHERE driver_id=?", (did,)).fetchone()[0]
    c = conn.execute("SELECT COUNT(*) FROM operations WHERE driver_id=? AND status='Completed'", (did,)).fetchone()[0]
    return jsonify(total_trips=t, completed_trips=c)

@app.route('/api/driver/today/<int:did>')
def d_today(did):
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    rows = conn.execute('''
        SELECT o.id, o.departure_time, o.status, r.route_name, v.registration_no, v.type
        FROM operations o JOIN routes r ON o.route_id = r.id JOIN vehicles v ON o.vehicle_id = v.id
        WHERE o.driver_id = ? AND o.operation_date = ?
    ''', (did, today)).fetchall()
    return jsonify([dict(ix) for ix in rows])

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
