# Roadmap

This document describes the planned development path of **HomeLab Hub**.

The roadmap is organized into milestones rather than software versions.

Each milestone should produce a usable and testable application.

Future milestones may change as the project evolves.

---

# Milestone 1 — Foundation

Goal:

Create a working project foundation.

Tasks:

* Project structure
* Documentation
* Flask backend
* SQLite database
* Configuration handling
* Logging
* Basic web interface
* Basic REST API

Status:

🟢 Completed

---

# Milestone 2 — Device Discovery

Goal:

Automatically discover devices on the local network.

Tasks:

* Network scanning
* Hostname detection
* MAC address detection
* Manufacturer lookup
* Device creation
* Device updates
* Manual synchronization
* Automatic scan scheduling
* Scan overlap protection

Expected result:

The application can continuously maintain a persistent inventory of network devices.

Status:

🟢 Completed

Implemented:

* Network scanning with Nmap and ARP discovery
* MAC address detection
* Hostname enrichment
* Manufacturer detection
* Automatic device creation and updates
* Manual synchronization
* Automatic scheduled scanning
* Shared scan coordination
* Scan overlap protection
* Scheduler status reporting
* Configurable scan interval

---

# Milestone 3 — Device Inventory

Goal:

Manage discovered devices.

Tasks:

* Known devices
* Unknown devices
* Online devices
* Offline devices
* Pinned devices
* Device details
* Tags
* Notes
* Photos
* Explicit device deletion

Expected result:

Users can manage their complete homelab inventory.

Status:

🟡 In Progress

Implemented:

* Known and unknown device management
* Online and offline device state
* Reliable automatic offline tracking
* Configurable missed-scan threshold
* Pinned-device behavior
* Device metadata editing
* IP assignment tracking
* Device detail view
* Device tags
* Tag management through the web interface and REST API
* Explicit user-requested device deletion

Remaining:

* Notes
* Photos

---

# Milestone 4 — Device Sessions

Goal:

Track device availability over time.

Tasks:

* Session start
* Session end
* Session duration
* Historical sessions
* Last online duration
* Future uptime calculations

Expected result:

The application keeps historical online/offline information.

Status:

🟡 In Progress

Implemented:

* Session creation
* Active session tracking
* Automatic session closure
* Configurable offline threshold handling
* Session history storage
* Session history display
* Current session duration
* Completed session duration
* First-seen and last-seen information

Remaining:

* Cumulative uptime statistics
* Additional availability statistics and reporting

---

# Milestone 5 — Production Deployment

Goal:

Run HomeLab Hub continuously on its intended low-power hardware.

Tasks:

* Raspberry Pi 3 deployment
* Python virtual environment
* Production WSGI server
* systemd service
* Automatic service startup
* Persistent SQLite database
* Production configuration
* Continuous scheduled discovery

Expected result:

HomeLab Hub operates as a persistent service on a Raspberry Pi 3 Model B+.

Status:

🟢 Completed

Implemented:

* Raspberry Pi 3 Model B+ production deployment
* Python virtual environment
* Gunicorn production server
* Single-worker deployment compatible with the in-process scheduler
* systemd service
* Automatic startup after reboot
* Persistent SQLite database
* Environment-based production configuration
* Continuous scheduled network discovery

---

# Milestone 6 — Monitoring Agents

Goal:

Collect detailed host information.

Tasks:

* Linux agent
* CPU usage
* RAM usage
* Temperature
* Disk usage
* Uptime
* OS information
* Service information
* Docker information

Expected result:

Linux hosts report detailed system information.

---

# Milestone 7 — Infrastructure Dashboard

Goal:

Create a central infrastructure overview.

Tasks:

* Infrastructure dashboard
* Host statistics
* Service status
* Temperature overview
* Storage overview
* Historical graphs

Expected result:

A complete infrastructure dashboard.

---

# Milestone 8 — Integrations

Goal:

Integrate existing self-hosted services.

Examples:

* Watchdog
* Kindle Dashboard
* Flask applications
* Security dashboards
* Docker

Expected result:

HomeLab Hub becomes the central entry point for the homelab.

---

# Milestone 9 — Benchmarking

Goal:

Store long-term performance history.

Tasks:

* CPU history
* Temperature history
* Storage history
* Memory history
* Benchmark execution
* Historical graphs

Expected result:

Long-term infrastructure performance tracking.

---

# Milestone 10 — Android Client

Goal:

Provide mobile access.

Tasks:

* Android application
* API authentication
* Dashboard
* Device management
* Manual synchronization
* Optional notifications

Expected result:

Native Android application.

---

# Milestone 11 — Plugin System

Goal:

Allow third-party extensions.

Tasks:

* Plugin loading
* Plugin configuration
* Plugin API
* Optional dashboard widgets

Expected result:

New functionality can be added without modifying the core application.

---

# Long-Term Ideas

Ideas that are intentionally outside the current roadmap.

Possible future additions include:

* Multiple users
* Role-based permissions
* Inventory import/export
* Automatic backups
* Configuration templates
* Asset management
* UPS monitoring
* Network topology visualization
* Historical security events
* Multiple network support
* Distributed HomeLab Hub instances
* Custom dashboards

---

# Development Philosophy

The project follows a few important principles.

Every milestone should produce a working application.

The application should remain usable throughout development.

Large features should be divided into small independent tasks.

The core application should remain lightweight.

Optional integrations should never become mandatory.

Backward compatibility should be preserved whenever practical.

Code readability is preferred over clever implementations.

Maintainability is considered more important than feature count.

Documentation should evolve together with the code.

The project is expected to grow continuously over several years.
