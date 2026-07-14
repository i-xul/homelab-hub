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

🟡 In Progress

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
* Scan scheduling

Expected result:

The application can build a persistent inventory of network devices.

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

Expected result:

Users can manage their complete homelab inventory.

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

---

# Milestone 5 — Monitoring Agents

Goal:

Collect detailed host information.

Tasks:

Linux agent

CPU

RAM

Temperature

Disk usage

Uptime

OS information

Service information

Docker information

Expected result:

Linux hosts report detailed system information.

---

# Milestone 6 — Infrastructure Dashboard

Goal:

Create a central infrastructure overview.

Tasks:

Infrastructure dashboard

Host statistics

Service status

Temperature overview

Storage overview

Historical graphs

Expected result:

A complete infrastructure dashboard.

---

# Milestone 7 — Integrations

Goal:

Integrate existing self-hosted services.

Examples:

Watchdog

Kindle Dashboard

Flask applications

Security dashboards

Docker

Expected result:

HomeLab Hub becomes the central entry point for the homelab.

---

# Milestone 8 — Benchmarking

Goal:

Store long-term performance history.

Tasks:

CPU history

Temperature history

Storage history

Memory history

Benchmark execution

Historical graphs

Expected result:

Long-term infrastructure performance tracking.

---

# Milestone 9 — Android Client

Goal:

Provide mobile access.

Tasks:

Android application

API authentication

Dashboard

Device management

Manual synchronization

Optional notifications

Expected result:

Native Android application.

---

# Milestone 10 — Plugin System

Goal:

Allow third-party extensions.

Tasks:

Plugin loading

Plugin configuration

Plugin API

Optional dashboard widgets

Expected result:

New functionality can be added without modifying the core application.

---

# Long-Term Ideas

Ideas that are intentionally outside the current roadmap.

Possible future additions include:

Multiple users

Role-based permissions

Inventory import/export

Automatic backups

Configuration templates

Asset management

UPS monitoring

Network topology visualization

Historical security events

Multiple network support

Distributed HomeLab Hub instances

Custom dashboards

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

