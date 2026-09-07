# HomeLab Hub

**HomeLab Hub** is a self-hosted infrastructure management platform designed for Raspberry Pi and homelab environments.

The project combines device discovery, persistent inventory management, device history, documentation and future infrastructure monitoring into a single lightweight web interface. It is designed to run efficiently on low-power hardware such as the Raspberry Pi 3 Model B+ while remaining modular and extensible.

---

## Features

### Implemented

* Automatic network device discovery
* Manual network synchronization
* Persistent device inventory
* MAC-based device identification
* Hostname and manufacturer enrichment
* Known and unknown device management
* Online and offline device tracking
* Configurable missed-scan threshold
* Device pinning
* Device metadata editing
* IP assignment tracking
* Device detail views
* Device tags
* Tag management through the web interface and REST API
* Device session tracking
* Historical session display
* Automatic session closure
* Explicit user-requested device deletion
* Automatic scheduled network scanning
* Scan overlap protection
* Scheduler status reporting
* Lightweight responsive web interface
* REST API
* Raspberry Pi 3 production deployment
* Gunicorn production server
* systemd service

### Planned

* Device notes and documentation
* Device photo support
* Cumulative uptime statistics
* Linux monitoring agent
* Windows monitoring agent
* Docker integration
* Service monitoring
* Benchmark history
* Infrastructure dashboard
* Kindle Dashboard integration *(optional)*
* Telegram notifications *(optional)*
* Flask application launcher
* Android companion application
* Plugin system

---

## Architecture

```text
                    Web Browser
                         │
                         │
                  REST API / Flask
                         │
                  HomeLab Hub Core
                         │
              ┌──────────┴──────────┐
              │                     │
         SQLite Database      Network Discovery
                                    │
                                    │
                              Scan Scheduler
```

Future monitoring agents and integrations will communicate with the backend through the REST API.

The backend follows an **API-first** architecture, allowing multiple clients such as the web interface, monitoring agents, Android applications and optional integrations to use the same backend services.

---

## Roadmap

### Completed foundation

* Core backend
* SQLite database
* Device discovery
* Persistent device inventory
* Manual synchronization
* Automatic scheduled discovery
* Online and offline tracking
* Device sessions
* Device tags
* Explicit device deletion
* Raspberry Pi 3 production deployment

### Current inventory work

* Device notes
* Device photos
* Additional availability statistics

### Future development

* Monitoring agents
* Infrastructure dashboard
* Service and Docker integrations
* Benchmark history
* Optional integrations
* Android application
* Plugin system

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the detailed milestone roadmap.

---

## Technology Stack

* Python
* Flask
* SQLAlchemy
* Alembic
* SQLite
* Gunicorn
* systemd
* Nmap
* HTML
* CSS
* JavaScript
* REST API

---

## Design Principles

* Lightweight
* Self-hosted
* API-first
* Modular
* Privacy-first
* Raspberry Pi friendly
* Open source
* Easy to maintain
* Persistent historical inventory
* No automatic device deletion

---

## Language

Project language:

* Source code: English
* Comments: English
* Documentation: English

---

## Production Deployment

The primary production deployment runs on a **Raspberry Pi 3 Model B+**.

The current production architecture uses:

* Linux
* Python virtual environment
* Flask
* Gunicorn
* SQLite
* systemd
* Nmap-based network discovery
* Automatic scheduled scanning

Gunicorn currently runs with a single worker because the scan scheduler operates inside the application process.

The application is intended for private-network use and does not require public internet exposure.

---

## Project Status

**Active development**

HomeLab Hub is operational as a persistent Raspberry Pi 3 service.

The current implementation includes:

* Flask backend with SQLAlchemy and SQLite persistence
* Alembic database migrations
* Local network discovery using Nmap and ARP-related system information
* MAC-based device identification
* Hostname and manufacturer enrichment
* Persistent device inventory
* Known and unknown device management
* Manual device metadata editing
* IP assignment tracking
* Manual network synchronization
* Automatic scheduled network discovery
* Scan overlap protection
* Scheduler status reporting
* Reliable automatic online and offline tracking
* Configurable offline threshold handling
* Device detail views
* Device session tracking and history
* Device tags
* Explicit user-requested device deletion
* Gunicorn production serving
* systemd-based service management
* Raspberry Pi 3 production deployment

Current development is focused on completing the remaining inventory features, especially device notes and photographs, before moving into host monitoring and broader infrastructure functionality.

The project is developed incrementally, with each milestone intended to leave the application in a usable and testable state.

---

## Documentation

Additional documentation:

* [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
* [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md)
* [`docs/PROJECT_PRINCIPLES.md`](docs/PROJECT_PRINCIPLES.md)
* [`docs/ROADMAP.md`](docs/ROADMAP.md)

---

## License

This project is released under the MIT License.
