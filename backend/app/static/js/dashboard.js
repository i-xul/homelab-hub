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