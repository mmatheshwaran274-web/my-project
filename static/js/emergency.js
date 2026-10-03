/**
 * BLIND ASSIST - Emergency Assistance Module
 * Accessible confirmation modal, GPS coordinate capture, emergency API dispatch,
 * and spoken reassurance.
 */

document.addEventListener('DOMContentLoaded', function () {
    const btnTriggerEmergency = document.getElementById('btn-trigger-emergency');
    const modalConfirm = document.getElementById('emergency-modal');
    const btnCancel = document.getElementById('btn-emergency-cancel');
    const btnConfirm = document.getElementById('btn-emergency-confirm');
    const resultsContainer = document.getElementById('emergency-results');
    const contactDisplay = document.getElementById('emergency-contact-display');
    const instructionsList = document.getElementById('emergency-instructions-list');
    const statusText = document.getElementById('emergency-status');

    // Welcome warning
    setTimeout(() => {
        BlindAssistA11y.speak("Emergency assistance page. If you require emergency help, press the large red Emergency button.");
    }, 500);

    // Open confirmation modal
    if (btnTriggerEmergency) {
        btnTriggerEmergency.addEventListener('click', openConfirmation);
    }

    // Modal controls
    if (btnCancel) {
        btnCancel.addEventListener('click', closeConfirmation);
    }

    if (btnConfirm) {
        btnConfirm.addEventListener('click', executeEmergencyDispatch);
    }

    function openConfirmation() {
        if (modalConfirm) {
            modalConfirm.classList.add('active');
            modalConfirm.setAttribute('aria-hidden', 'false');
            if (btnConfirm) btnConfirm.focus();

            const promptText = BlindAssistA11y.state.language === 'ta'
                ? "அவசர உதவியை இயக்க விரும்புகிறீர்களா? உறுதி செய்ய Enter அழுத்தவும், ரத்து செய்ய Escape அழுத்தவும்."
                : "Are you sure you want to activate emergency assistance? Press Enter to confirm or Escape to cancel.";

            BlindAssistA11y.speak(promptText);
        }
    }

    function closeConfirmation() {
        if (modalConfirm) {
            modalConfirm.classList.remove('active');
            modalConfirm.setAttribute('aria-hidden', 'true');
            if (btnTriggerEmergency) btnTriggerEmergency.focus();
            BlindAssistA11y.speak("Emergency activation cancelled.");
        }
    }

    // Modal key handler
    document.addEventListener('keydown', function (e) {
        if (modalConfirm && modalConfirm.classList.contains('active')) {
            if (e.key === 'Escape') {
                closeConfirmation();
            }
        }
    });

    async function executeEmergencyDispatch() {
        closeConfirmation();
        updateStatus("Activating emergency response and logging GPS location...");
        BlindAssistA11y.speak("Activating emergency response. Please remain calm.");

        let latitude = null;
        let longitude = null;

        // Try getting geolocation with a fast timeout
        if (navigator.geolocation) {
            try {
                const pos = await new Promise((resolve, reject) => {
                    navigator.geolocation.getCurrentPosition(resolve, reject, {
                        enableHighAccuracy: true,
                        timeout: 5000
                    });
                });
                latitude = pos.coords.latitude;
                longitude = pos.coords.longitude;
            } catch (e) {
                console.warn("Could not capture GPS for emergency:", e);
            }
        }

        try {
            const response = await fetch('/api/emergency', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    latitude: latitude,
                    longitude: longitude,
                    language: BlindAssistA11y.state.language
                })
            });

            const data = await response.json();

            if (data.success) {
                resultsContainer.style.display = 'block';
                if (contactDisplay) {
                    contactDisplay.textContent = data.emergency_contact || "No contact registered";
                }

                if (instructionsList && data.instructions) {
                    instructionsList.innerHTML = '';
                    data.instructions.forEach(step => {
                        const li = document.createElement('li');
                        li.style.marginBottom = '0.75rem';
                        li.textContent = step;
                        instructionsList.appendChild(li);
                    });
                }

                updateStatus("Emergency assistance activated successfully.");
                BlindAssistA11y.speak(data.speech);
            } else {
                updateStatus("Failed to activate emergency assistance.");
            }
        } catch (err) {
            console.error("Emergency dispatch error:", err);
            const errMsg = "Unable to connect to emergency service. Please dial 112 directly.";
            updateStatus(errMsg);
            BlindAssistA11y.speak(errMsg);
        }
    }

    function updateStatus(msg) {
        if (statusText) {
            statusText.textContent = msg;
        }
        BlindAssistA11y.announce(msg);
    }
});
