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