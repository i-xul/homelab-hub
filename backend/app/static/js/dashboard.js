/*
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     dashboard.js

 Description:
     Handles interactive actions on the HomeLab Hub inventory
     dashboard.

     The initial implementation starts a manual inventory scan,
     displays its result and refreshes the dashboard after a
     successful synchronization.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
*/

"use strict";


// ---------------------------------------------------------
// Dashboard elements
// ---------------------------------------------------------

const syncButton = document.querySelector("#sync-button");
const syncStatus = document.querySelector("#sync-status");

const deviceEditButtons =
    document.querySelectorAll(".device-edit-button");

const deviceCards =
    document.querySelectorAll(".device-card");

const localDateTimeElements =
    document.querySelectorAll(".local-datetime");

const deviceEditModal =
    document.querySelector("#device-edit-modal");

const deviceEditForm =
    document.querySelector("#device-edit-form");

const deviceEditClose =
    document.querySelector("#device-edit-close");

const deviceEditCancel =
    document.querySelector("#device-edit-cancel");

const deviceEditId =
    document.querySelector("#device-edit-id");

const deviceEditFriendlyName =
    document.querySelector("#device-edit-friendly-name");

const deviceEditTrusted =
    document.querySelector("#device-edit-trusted");

const deviceEditPinned =
    document.querySelector("#device-edit-pinned");

const deviceEditIpAssignment =
    document.querySelector("#device-edit-ip-assignment");

const deviceEditExpectedIp =
    document.querySelector("#device-edit-expected-ip");

const deviceEditStatus =
    document.querySelector("#device-edit-status");

// ---------------------------------------------------------
// Local date and time formatting
// ---------------------------------------------------------

function formatLocalDateTime(element) {
    /*
     * Convert an ISO 8601 timestamp supplied by the backend
     * into the browser user's local time zone.
     */

    const timestamp = element.getAttribute("datetime");

    if (!timestamp) {
        return;
    }

    const date = new Date(timestamp);

    if (Number.isNaN(date.getTime())) {
        return;
    }

    const format = element.dataset.format || "datetime";

    const options = format === "time"
        ? {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            hour12: false,
        }
        : {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            hour12: false,
        };

    element.textContent = new Intl.DateTimeFormat(
        undefined,
        options,
    ).format(date);

    element.title = `UTC: ${timestamp}`;
}


localDateTimeElements.forEach(
    formatLocalDateTime,
);

// ---------------------------------------------------------
// Manual synchronization
// ---------------------------------------------------------

async function runManualScan() {
    /*
     * Start one manual inventory scan through the backend API.
     *
     * The button remains disabled while the request is active,
     * preventing accidental repeated clicks from the browser.
     */

    if (!syncButton || !syncStatus) {
        return;
    }

    syncButton.disabled = true;
    syncButton.textContent = "Scanning…";

    syncStatus.className = "sync-status";
    syncStatus.textContent = "Scanning the configured network…";

    try {
        const response = await fetch("/api/scan", {
            method: "POST",
            headers: {
                "Accept": "application/json",
            },
        });

        const payload = await response.json();

        if (!response.ok) {
            throw new Error(
                payload.message || "Inventory scan failed."
            );
        }

        const result = payload.result;

        syncStatus.className =
            "sync-status sync-status--success";

        syncStatus.textContent = [
            `Detected ${result.detected}`,
            `created ${result.created}`,
            `updated ${result.updated}`,
            `skipped ${result.skipped_without_mac}`,
        ].join(" · ");

        // Reload shortly after completion so the visible device
        // lists and summary cards reflect the latest database state.
        window.setTimeout(() => {
            window.location.reload();
        }, 1500);
    } catch (error) {
        syncStatus.className =
            "sync-status sync-status--error";

        syncStatus.textContent =
            error instanceof Error
                ? error.message
                : "Inventory scan failed.";

        syncButton.disabled = false;
        syncButton.textContent = "Sync now";
    }
}


if (syncButton) {
    syncButton.addEventListener(
        "click",
        runManualScan,
    );
}

// ---------------------------------------------------------
// Device card navigation
// ---------------------------------------------------------

function isInteractiveCardTarget(target) {
    /*
     * Return whether the event originated from an element that
     * already has its own interactive behaviour.
     */

    if (!(target instanceof Element)) {
        return false;
    }

    return target.closest(
        "a, button, input, select, textarea, label"
    ) !== null;
}


function openDeviceCard(card) {
    /*
     * Navigate to the detail page stored on a device card.
     */

    const detailUrl = card.dataset.detailUrl;

    if (!detailUrl) {
        return;
    }

    window.location.assign(detailUrl);
}


deviceCards.forEach((card) => {
    card.addEventListener("click", (event) => {
        if (isInteractiveCardTarget(event.target)) {
            return;
        }

        openDeviceCard(card);
    });

    card.addEventListener("keydown", (event) => {
        if (
            event.key !== "Enter"
            && event.key !== " "
        ) {
            return;
        }

        if (isInteractiveCardTarget(event.target)) {
            return;
        }

        event.preventDefault();
        openDeviceCard(card);
    });
});

// ---------------------------------------------------------
// Device metadata editing
// ---------------------------------------------------------

function openDeviceEditModal(button) {
    /*
     * Populate and open the device edit form using metadata
     * stored in the selected card's data attributes.
     */

    if (
        !deviceEditModal ||
        !deviceEditId ||
        !deviceEditFriendlyName ||
        !deviceEditTrusted ||
        !deviceEditPinned ||
        !deviceEditIpAssignment ||
        !deviceEditExpectedIp ||
        !deviceEditStatus
    ) {
        return;
    }

    deviceEditId.value = button.dataset.deviceId || "";

    deviceEditFriendlyName.value =
        button.dataset.friendlyName || "";

    deviceEditTrusted.checked =
        button.dataset.trusted === "true";

    deviceEditPinned.checked =
        button.dataset.pinned === "true";

    deviceEditIpAssignment.value =
        button.dataset.ipAssignment || "unknown";

    deviceEditExpectedIp.value =
        button.dataset.expectedIp || "";

    deviceEditStatus.textContent = "";
    deviceEditStatus.className = "form-status";

    deviceEditModal.hidden = false;
}


function closeDeviceEditModal() {
    /*
     * Close the device edit modal without saving changes.
     */

    if (deviceEditModal) {
        deviceEditModal.hidden = true;
    }
}


async function saveDeviceMetadata(event) {
    /*
     * Send user-managed device metadata to the PATCH API.
     */

    event.preventDefault();

    if (
        !deviceEditId ||
        !deviceEditFriendlyName ||
        !deviceEditTrusted ||
        !deviceEditPinned ||
        !deviceEditIpAssignment ||
        !deviceEditExpectedIp ||
        !deviceEditStatus
    ) {
        return;
    }

    const deviceId = deviceEditId.value;

    const payload = {
        friendly_name: deviceEditFriendlyName.value,
        trusted: deviceEditTrusted.checked,
        pinned: deviceEditPinned.checked,
        ip_assignment: deviceEditIpAssignment.value,
        expected_ip: deviceEditExpectedIp.value,
    };

    deviceEditStatus.className = "form-status";
    deviceEditStatus.textContent = "Saving changes…";

    try {
        const response = await fetch(
            `/api/devices/${deviceId}`,
            {
                method: "PATCH",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            },
        );

        const responsePayload = await response.json();

        if (!response.ok) {
            throw new Error(
                responsePayload.message ||
                "Device update failed."
            );
        }

        deviceEditStatus.textContent =
            "Changes saved successfully.";

        window.setTimeout(() => {
            window.location.reload();
        }, 700);
    } catch (error) {
        deviceEditStatus.className =
            "form-status form-status--error";

        deviceEditStatus.textContent =
            error instanceof Error
                ? error.message
                : "Device update failed.";
    }
}

deviceEditButtons.forEach((button) => {
    button.addEventListener(
        "click",
        () => openDeviceEditModal(button),
    );
});

if (deviceEditClose) {
    deviceEditClose.addEventListener(
        "click",
        closeDeviceEditModal,
    );
}

if (deviceEditCancel) {
    deviceEditCancel.addEventListener(
        "click",
        closeDeviceEditModal,
    );
}

if (deviceEditForm) {
    deviceEditForm.addEventListener(
        "submit",
        saveDeviceMetadata,
    );
}