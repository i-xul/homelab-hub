# Architecture

This document describes the planned architecture of **HomeLab Hub**.

The system is designed to run on low-power hardware such as a Raspberry Pi 3 Model B+ while remaining modular, extensible and suitable for long-term use.

## Implementation Status

The initial architecture is now partially implemented.

Currently operational components include:

* Flask backend
* SQLite persistence
* REST API foundation
* Web-based device inventory
* Nmap and ARP-based network discovery
* Hostname and manufacturer enrichment
* Persistent device identification by MAC address
* Manual network synchronization
* Device metadata management
* Device detail views
* Device session tracking and history

The next architectural step is background scan scheduling, which will connect
network discovery, online/offline state management and session tracking into
a continuously operating system.

The primary deployment target remains the Raspberry Pi 3 Model B+.

---

## Architecture Goals

The architecture should:

* remain lightweight
* support multiple operating systems
* separate core functionality from optional integrations
* expose a stable API for web and mobile clients
* preserve historical device information
* avoid unnecessary external dependencies
* operate entirely inside the user’s private network
* remain usable without cloud services

---

## High-Level Architecture

```text
                    Web Browser
                         │
                         │ HTTP / HTTPS
                         ▼
                HomeLab Hub Backend
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
       REST API     Web Interface   Background Jobs
          │                              │
          │                              ├── Network discovery
          │                              ├── Session tracking
          │                              ├── Agent processing
          │                              └── Scheduled maintenance
          │
          ▼
      Core Services
          │
          ├── Device inventory
          ├── Known and unknown devices
          ├── Online and offline state
          ├── Tags
          ├── Notes
          ├── Photos
          └── Device sessions
          │
          ▼
      SQLite Database
```

Optional clients and integrations communicate with the backend through the API.

```text
Linux Agents ───────┐
Windows Agents ─────┤
Android App ────────┤
Kindle Integration ─┼── REST API ── HomeLab Hub Backend
Watchdog Integration┤
Telegram Integration┘
```

---

## Core Components

The HomeLab Hub core consists of the following components.

### Backend

The backend is responsible for:

* application logic
* database access
* API endpoints
* authentication
* device state management
* session tracking
* background tasks
* integration management

The initial backend implementation will use Python and Flask.

---

### Web Interface

The web interface provides access to:

* current devices
* offline devices
* unknown devices
* device details
* session history
* tags
* notes
* photographs
* infrastructure data
* application links
* configuration

The web interface should use the same backend API that future clients use.

It should not directly access the database.

---

### REST API

The REST API acts as the primary interface between the backend and all clients.

Planned API consumers include:

* web interface
* Linux agents
* Windows agents
* Android application
* optional integrations
* external automation scripts

The API should use JSON for data exchange.

The backend should be designed API-first so that additional clients can be added without restructuring the core application.

---

### Database

SQLite will be used for the initial implementation.

SQLite was selected because it:

* has low resource requirements
* requires no separate database server
* is easy to back up
* performs well for the expected workload
* is well suited for Raspberry Pi hardware

Database access should be isolated behind an application layer so that migration to another database remains possible later.

---

### Background Jobs

Background jobs perform tasks that should not depend on a user opening the web interface.

Examples include:

* automatic network scans
* device online and offline state updates
* device session creation and closure
* stale agent detection
* scheduled cleanup
* optional integration polling

The default network discovery interval is planned to be approximately five minutes.

The user must also be able to trigger an immediate scan manually through the web interface.

Only one network scan should run at a time.

---

## Network Discovery

Network discovery detects devices visible on the local network.

The first implementation is expected to use tools such as:

* ARP or neighbor table inspection
* ping scanning
* Nmap

The discovery process should collect data such as:

* IP address
* MAC address
* hostname when available
* manufacturer when available
* discovery timestamp

Network discovery should never automatically delete devices.

A device that disappears from the network is marked offline but remains in the inventory until manually removed.

---

## Device Identity

The MAC address is normally used as the primary identifier for automatically discovered network devices.

IP addresses must not be treated as permanent identifiers because they may change.

The design must account for cases where:

* a device has multiple network interfaces
* MAC address randomization is used
* a virtual machine receives a new MAC address
* a device is first created manually
* discovery data is incomplete

User-confirmed identity and manually entered information must take priority over automatically collected values.

---

## Device State

A device can be in one of several logical states.

### Online

The device was detected during the latest completed scan.

### Offline

The device has been detected previously but was not found during the latest completed scan.

### Unknown

The device has been discovered but has not yet been identified or approved by the user.

### Known

The device has been identified and marked as belonging to the environment.

### Pinned

A pinned device remains visible in the main device list even when offline.

Offline pinned devices should be visually distinguished, for example by displaying them in grey.

---

## Device Sessions

A device session represents one continuous period during which a device is considered online.

A session begins when:

* a previously offline device is detected
* a new device is detected for the first time

A session ends when the device is no longer detected according to the configured offline threshold.

The system should preserve:

* session start time
* session end time
* session duration

A short temporary scan failure should not necessarily end a session immediately.

The implementation may require multiple missed scans before a device is marked offline.

---

## Manual Synchronization

The web interface should include a manual synchronization action.

This action should:

* start an immediate network scan
* prevent duplicate simultaneous scans
* show that a scan is running
* update the device list after completion
* display the previous scan time
* display the result of the scan

Automatic scanning must continue independently of manual scans.

---

## Monitoring Agents

Monitoring agents provide detailed host information that cannot be obtained reliably through network discovery alone.

Agents may collect:

* CPU usage
* memory usage
* disk usage
* temperature
* uptime
* operating system
* kernel version
* hardware information
* service status
* Docker information
* Raspberry Pi throttling state

The first agent will target Linux systems.

Windows support may later be implemented using Python or PowerShell.

Agents should:

* remain lightweight
* use authenticated API requests
* send data at configurable intervals
* continue operating without direct database access
* fail safely if the backend is unavailable

---

## Core and Optional Modules

The project must distinguish between required core features and optional modules.

### Core

The core includes:

* device discovery
* device inventory
* online and offline states
* known and unknown device management
* pinned devices
* device sessions
* tags
* notes
* photos
* API
* web interface
* database

### Optional Modules

Optional modules may include:

* Linux monitoring agent
* Windows monitoring agent
* Docker integration
* service monitoring
* benchmark history
* Watchdog integration
* Kindle Dashboard integration
* Telegram notifications
* Flask application launcher
* Android application

The core must remain fully usable without any optional module.

---

## Integration Architecture

Integrations should communicate through documented interfaces rather than modifying core application code whenever possible.

An integration may:

* consume API data
* submit data through the API
* register navigation links
* provide additional device information
* provide optional dashboard sections
* create alerts

Integrations should not:

* directly modify core database tables
* become mandatory dependencies
* prevent the application from starting when unavailable
* overwrite user-entered information

---

## Kindle Dashboard Integration

The Kindle Dashboard integration is specific to certain environments and must remain optional.

It should be implemented as a separate integration or client that consumes HomeLab Hub data through the API.

Users without a Kindle Dashboard setup must be able to install and use HomeLab Hub without Kindle-related configuration or dependencies.

---

## Android Application

A future Android application may provide the same primary data as the web interface.

The Android application should connect to the HomeLab Hub backend through a private network path such as:

* Tailscale
* NordVPN Meshnet
* another trusted VPN connection

The backend should not need to be exposed directly to the public internet.

The Android application remains an optional client and is not required for the core system.

---

## Security

HomeLab Hub is intended for private-network use.

The architecture should support:

* authenticated API access
* securely stored credentials
* HTTPS where practical
* restricted access through firewall rules
* private VPN access for remote connections
* rate limiting for sensitive endpoints
* validation of data received from agents
* protection against unauthorized file uploads

Secrets must not be stored in the Git repository.

The backend should not trust agent-submitted device identifiers without validation.

---

## Photos and Uploaded Files

Uploaded photographs should be stored on disk rather than inside the SQLite database.

The database should store only file metadata and references.

Uploaded files should:

* use generated internal filenames
* be validated by file type
* have configurable size limits
* be stored outside the source-code directory
* be excluded from Git

---

## Application Links

HomeLab Hub may include a launcher for existing internal applications.

Examples include:

* book tracker
* food tracker
* shopping application
* security dashboards

The launcher should primarily store and display links.

External applications should remain independent services and should not be merged into the HomeLab Hub core unless there is a clear architectural reason.

---

## Deployment

The initial deployment target is a Raspberry Pi 3 Model B+.

The planned production environment includes:

* Linux
* Python virtual environment
* Flask application
* SQLite database
* systemd service
* reverse proxy when needed
* local or VPN-only access

Development should remain possible on a separate Linux workstation.

Configuration, runtime data and source code should remain clearly separated.

---

## Project Structure

The initial project structure is:

```text
homelab-hub/
├── agents/
│   └── linux/
├── backend/
│   └── app/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_MODEL.md
│   └── ROADMAP.md
├── integrations/
├── scripts/
├── tests/
├── .gitignore
├── LICENSE
└── README.md
```

This structure may evolve as implementation requirements become clearer.

---

## Architectural Rules

The following rules should guide future development:

1. The core must work without optional integrations.
2. Clients and agents must not access the database directly.
3. User-entered data must not be overwritten by discovery.
4. Devices must never be removed automatically.
5. IP addresses must not be used as permanent device identities.
6. Background scans must not overlap.
7. Optional module failures must not stop the core application.
8. Secrets and runtime data must remain outside version control.
9. Public internet exposure should not be required.
10. New clients should use the documented API.
11. Development decisions should prioritize maintainability over unnecessary complexity.
12. The application must remain suitable for Raspberry Pi 3 class hardware.

---

## Future Architecture Considerations

Possible future changes include:

* plugin registration system
* event-based internal messaging
* WebSocket or server-sent event updates
* PostgreSQL support
* multiple network or subnet support
* role-based user accounts
* backup and restore tools
* remote agent enrollment
* Android push notifications
* distributed HomeLab Hub instances

These possibilities should not increase the complexity of the initial implementation unless they become necessary.

