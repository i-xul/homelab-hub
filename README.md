# HomeLab Hub

**HomeLab Hub** is a self-hosted infrastructure management platform designed for Raspberry Pi and homelab environments.

The project combines device discovery, inventory management, infrastructure monitoring, documentation, benchmarking and service integrations into a single lightweight web interface. It is designed to run efficiently on low-power hardware such as the Raspberry Pi 3 Model B+ while remaining modular and extensible.

---

## Features

### Implemented or partially implemented

* Automatic network device discovery
* Device inventory with persistent history
* Known and unknown device detection
* Online and offline device tracking
* Device pinning
* Device tags and categories
* Manual notes and documentation
* Device photo support
* Session history (first seen, last seen, online duration)
* Lightweight web interface
* REST API

### Planned modules

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
              │                     │
              └──────────┬──────────┘
                         │
              Monitoring Agents
                         │
     Raspberry Pi • Linux • Windows
```

The backend is designed using an **API-first** architecture, allowing multiple clients such as the web interface, Android application and optional integrations to use the same backend services.

---

## Roadmap

### Phase 1

* Core backend
* SQLite database
* Device discovery
* Device inventory
* Basic web interface

### Phase 2

* Device sessions
* Offline device history
* Known/unknown device management
* Tags
* Notes
* Photos

### Phase 3

* Monitoring agents
* Hardware statistics
* Temperature monitoring
* Benchmark history

### Phase 4

* Infrastructure integrations
* Docker
* Services
* Security dashboard
* Optional Kindle integration

### Phase 5

* Android application
* Additional plugins
* Advanced reporting

---

## Technology Stack

* Python
* Flask
* SQLite
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
* Plugin-based
* Privacy-first
* Raspberry Pi friendly
* Open source
* Easy to maintain

---

## Language

Project language:

* Source code: English
* Comments: English
* Documentation: English

---

## Project Status

**Active development**

HomeLab Hub is currently under active development.

The core application foundation is operational and currently includes:

* Flask backend with SQLite persistence
* Local network discovery using Nmap and ARP
* MAC-based device identification
* Hostname and manufacturer enrichment
* Persistent device inventory
* Known and unknown device management
* Manual device metadata editing
* IP assignment tracking
* Manual network synchronization
* Online and offline state foundation
* Device detail views
* Device session tracking and session history
* Raspberry Pi 3 compatible architecture

Current development is focused on automatic scheduled network discovery,
reliable online/offline state tracking and continuous device session history.

The project is developed incrementally, with each milestone intended to
leave the application in a usable and testable state.

---

## License

This project will be released under the MIT License.

