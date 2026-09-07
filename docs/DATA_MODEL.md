# Data Model

This document describes the logical data model of **HomeLab Hub**.

The goal is to keep the core database simple, lightweight and extensible while allowing optional modules to expand the system without modifying the core architecture.

The data model is designed around long-term infrastructure management rather than temporary monitoring.

> **Implementation status:** The core Device, Device Session and Tag models
> are implemented and in production use. Device Notes, Device Photos and
> Agent Status remain planned extensions. This document describes both the
> implemented core and the intended direction of the remaining data model.

---

# Design Principles

The following principles define how the data model should evolve.

* Devices are never automatically deleted.
* Every discovered device remains in the inventory until manually removed.
* User-entered information always has priority over automatically discovered information.
* Optional modules must not require changes to the core data model.
* Historical information should be preserved whenever practical.
* The backend should remain lightweight enough to run on a Raspberry Pi 3 Model B+.

---

# Core Entities

The first version of HomeLab Hub is built around the following core entities.

* Device — implemented
* Device Session — implemented
* Tag — implemented
* Device Note — planned
* Device Photo — planned
* Agent Status — planned

Additional entities may be added later as the project evolves.

---

# Device

Represents one physical or virtual device known by HomeLab Hub.

A device is created automatically when first discovered on the network or manually by the user.

Once created, it remains in the inventory until explicitly deleted.

## Fields

* id
* hostname
* friendly_name
* manufacturer
* model
* device_type
* mac_address
* current_ip
* known
* pinned
* active
* first_seen
* last_seen
* created_at
* updated_at

## Notes

User documentation should never be overwritten by automatic discovery.

Changing IP addresses should not create duplicate devices.

The MAC address should normally be treated as the primary identifier.

Devices are never removed automatically. A device can be permanently deleted
only through an explicit user-requested deletion.

Deleting a device also removes its associated device sessions and tag
associations. Tags themselves remain available for use by other devices.

---

# Device Session

Represents one continuous online period.

A session begins when a new or previously offline device is detected.

A session remains active while the device is considered online. When the
configured missed-scan threshold is reached, the device is marked offline and
the active session is closed.

## Fields

* id
* device_id
* session_start
* session_end
* duration

## Purpose

Sessions allow HomeLab Hub to display:

* Last online duration
* Last seen
* First seen
* Historical availability
* Future uptime statistics

---

# Tag

Tags allow devices to be grouped independently of their type.

Examples:

* Docker
* Linux
* Raspberry Pi
* Production
* Storage
* Media
* Testing

## Fields

* id
* name
* color

Tags use a many-to-many relationship with devices. A tag can be assigned to
multiple devices and a device can have multiple tags.

---

# Device Tag

A many-to-many relationship between devices and tags.

## Fields

* device_id
* tag_id

---

# Device Note

**Status: Planned**

Stores documentation written by the user.

Examples include:

* Maintenance history
* Configuration notes
* Upgrade history
* Known issues
* Future plans

## Fields

* id
* device_id
* title
* content
* created_at
* updated_at

---

# Device Photo

**Status: Planned**

Stores references to device photographs.

The image itself should be stored on disk rather than inside the database.

## Fields

* id
* device_id
* filename
* caption
* uploaded_at

---

# Agent Status

**Status: Planned**

Stores the most recent information received from a monitoring agent.

This table represents the current state only.

Historical performance metrics will be stored separately in future versions.

## Fields

* device_id
* cpu_usage
* memory_usage
* disk_usage
* temperature
* uptime
* last_report

---

# Unknown Devices

Unknown devices are not stored separately.

A device is considered unknown when:

* it has been discovered
* known = false

Once the user marks the device as known, it becomes part of the normal inventory.

---

# Future Extensions

The following modules are planned but intentionally excluded from the core data model.

* Docker
* Service monitoring
* Benchmark history
* Kindle Dashboard integration
* Telegram notifications
* Android application
* Flask application launcher
* Watchdog integration

These modules should integrate through APIs or extension tables whenever possible.

---

# Future Considerations

The current data model is intentionally conservative.

As the project grows, additional entities may be introduced for:

* Historical metrics
* Security events
* Service status
* Notifications
* Plugin configuration
* Android synchronization

The goal is to keep the core stable while allowing continuous expansion through modular components.

