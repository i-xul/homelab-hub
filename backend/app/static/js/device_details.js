/*
=============================================================
 HomeLab Hub
-------------------------------------------------------------
 File:
     device_details.js

 Description:
     Handles interactive actions on the HomeLab Hub device
     detail page.

     The initial implementation manages device tag assignment,
     tag creation and tag removal through the REST API.

 Author:
     H A (GitHub: i-xul)

 License:
     MIT License
=============================================================
*/

"use strict";


// ---------------------------------------------------------
// Device tag elements
// ---------------------------------------------------------

const deviceTagsSection =
    document.querySelector("#device-tags");

const assignTagForm =
    document.querySelector("#assign-tag-form");

const availableTagSelect =
    document.querySelector("#available-tag-select");

const createTagForm =
    document.querySelector("#create-tag-form");

const newTagName =
    document.querySelector("#new-tag-name");

const tagStatus =
    document.querySelector("#tag-status");

const tagRemoveButtons =
    document.querySelectorAll(".tag-remove-button");


// ---------------------------------------------------------
// Device deletion elements
// ---------------------------------------------------------

const deviceDeletionSection =
    document.querySelector("#device-deletion");

const deleteDeviceButton =
    document.querySelector("#delete-device-button");

const deleteDeviceStatus =
    document.querySelector("#delete-device-status");


// ---------------------------------------------------------
// Tag helpers
// ---------------------------------------------------------

function getDeviceId() {
    /*
     * Return the device identifier stored on the tag section.
     */

    if (!deviceTagsSection) {
        return null;
    }

    return deviceTagsSection.dataset.deviceId || null;
}


function setTagStatus(
    message,
    isError = false,
) {
    /*
     * Display tag-management feedback to the user.
     */

    if (!tagStatus) {
        return;
    }

    tagStatus.className = isError
        ? "form-status form-status--error"
        : "form-status";

    tagStatus.textContent = message;
}


async function readJsonResponse(response) {
    /*
     * Read a JSON API response and raise a useful error when
     * the backend reports an unsuccessful request.
     */

    const payload = await response.json();

    if (!response.ok) {
        throw new Error(
            payload.message || "Tag operation failed."
        );
    }

    return payload;
}


// ---------------------------------------------------------
// Existing tag assignment
// ---------------------------------------------------------

async function assignExistingTag(event) {
    /*
     * Assign the selected existing tag to the current device.
     */

    event.preventDefault();

    const deviceId = getDeviceId();

    if (
        !deviceId
        || !availableTagSelect
    ) {
        return;
    }

    const tagId = availableTagSelect.value;

    if (!tagId) {
        setTagStatus(
            "Select a tag before adding it.",
            true,
        );
        return;
    }

    setTagStatus("Adding tag…");

    try {
        const response = await fetch(
            `/api/devices/${deviceId}/tags/${tagId}`,
            {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                },
            },
        );

        await readJsonResponse(response);

        setTagStatus("Tag added successfully.");

        window.setTimeout(() => {
            window.location.reload();
        }, 500);
    } catch (error) {
        setTagStatus(
            error instanceof Error
                ? error.message
                : "Tag assignment failed.",
            true,
        );
    }
}


// ---------------------------------------------------------
// Tag creation
// ---------------------------------------------------------

async function createAndAssignTag(event) {
    /*
     * Create a new tag and immediately assign it to the current
     * device.
     */

    event.preventDefault();

    const deviceId = getDeviceId();

    if (
        !deviceId
        || !newTagName
    ) {
        return;
    }

    const name = newTagName.value.trim();

    if (!name) {
        setTagStatus(
            "Tag name must not be empty.",
            true,
        );
        return;
    }

    setTagStatus("Creating tag…");

    try {
        const createResponse = await fetch(
            "/api/tags",
            {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name,
                }),
            },
        );

        const createPayload =
            await readJsonResponse(createResponse);

        const tagId = createPayload.tag.id;

        const assignResponse = await fetch(
            `/api/devices/${deviceId}/tags/${tagId}`,
            {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                },
            },
        );

        await readJsonResponse(assignResponse);

        setTagStatus("Tag created and added successfully.");

        window.setTimeout(() => {
            window.location.reload();
        }, 500);
    } catch (error) {
        setTagStatus(
            error instanceof Error
                ? error.message
                : "Tag creation failed.",
            true,
        );
    }
}


// ---------------------------------------------------------
// Tag removal
// ---------------------------------------------------------

async function removeTag(button) {
    /*
     * Remove one assigned tag from the current device.
     */

    const deviceId = getDeviceId();
    const tagId = button.dataset.tagId;

    if (
        !deviceId
        || !tagId
    ) {
        return;
    }

    button.disabled = true;
    setTagStatus("Removing tag…");

    try {
        const response = await fetch(
            `/api/devices/${deviceId}/tags/${tagId}`,
            {
                method: "DELETE",
                headers: {
                    "Accept": "application/json",
                },
            },
        );

        await readJsonResponse(response);

        setTagStatus("Tag removed successfully.");

        window.setTimeout(() => {
            window.location.reload();
        }, 500);
    } catch (error) {
        button.disabled = false;

        setTagStatus(
            error instanceof Error
                ? error.message
                : "Tag removal failed.",
            true,
        );
    }
}


// ---------------------------------------------------------
// Device deletion
// ---------------------------------------------------------

async function deleteDevice() {
    /*
     * Permanently remove the current device after explicit
     * confirmation from the user.
     */

    if (
        !deviceDeletionSection
        || !deleteDeviceButton
    ) {
        return;
    }

    const deviceId =
        deviceDeletionSection.dataset.deviceId;

    const deviceName =
        deviceDeletionSection.dataset.deviceName
        || "this device";

    if (!deviceId) {
        return;
    }

    const confirmed = window.confirm(
        `Permanently delete "${deviceName}" from the inventory?\n\n`
        + "Its session history and tag associations will also "
        + "be removed. This action cannot be undone."
    );

    if (!confirmed) {
        return;
    }

    deleteDeviceButton.disabled = true;

    if (deleteDeviceStatus) {
        deleteDeviceStatus.className = "form-status";
        deleteDeviceStatus.textContent = "Deleting device…";
    }

    try {
        const response = await fetch(
            `/api/devices/${deviceId}`,
            {
                method: "DELETE",
                headers: {
                    "Accept": "application/json",
                },
            },
        );

        const payload = await response.json();

        if (!response.ok) {
            throw new Error(
                payload.message || "Device deletion failed."
            );
        }

        window.location.href = "/";
    } catch (error) {
        deleteDeviceButton.disabled = false;

        if (deleteDeviceStatus) {
            deleteDeviceStatus.className =
                "form-status form-status--error";

            deleteDeviceStatus.textContent =
                error instanceof Error
                    ? error.message
                    : "Device deletion failed.";
        }
    }
}


// ---------------------------------------------------------
// Event registration
// ---------------------------------------------------------

if (assignTagForm) {
    assignTagForm.addEventListener(
        "submit",
        assignExistingTag,
    );
}


if (createTagForm) {
    createTagForm.addEventListener(
        "submit",
        createAndAssignTag,
    );
}


tagRemoveButtons.forEach((button) => {
    button.addEventListener(
        "click",
        () => removeTag(button),
    );
});

if (deleteDeviceButton) {
    deleteDeviceButton.addEventListener(
        "click",
        deleteDevice,
    );
}
