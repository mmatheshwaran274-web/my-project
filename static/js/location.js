/**
 * BLIND ASSIST - Location Assistance Module
 * High-accuracy browser geolocation, coordinate formatting, and OpenStreetMap linking.
 */

document.addEventListener('DOMContentLoaded', function () {
    const btnGetLocation = document.getElementById('btn-get-location');
    const locStatus = document.getElementById('loc-status');
    const locResults = document.getElementById('loc-results');
    const txtLatitude = document.getElementById('loc-latitude');
    const txtLongitude = document.getElementById('loc-longitude');
    const txtAccuracy = document.getElementById('loc-accuracy');
    const mapLink = document.getElementById('loc-map-link');

    // Welcome speech
    setTimeout(() => {
        BlindAssistA11y.speak("Location Assistance page. Click the Get Location button to determine your current GPS position.");
    }, 500);

    if (btnGetLocation) {
        btnGetLocation.addEventListener('click', requestLocation);
    }

    function requestLocation() {
        if (!navigator.geolocation) {
            const err = "Geolocation is not supported by your browser.";
            updateStatus(err);
            BlindAssistA11y.speak(err);
            return;
        }

        updateStatus("Detecting your GPS location, please wait...");
        BlindAssistA11y.speak("Detecting your current location, please hold on.");
        btnGetLocation.disabled = true;

        navigator.geolocation.getCurrentPosition(
            onLocationSuccess,
            onLocationError,
            {
                enableHighAccuracy: true,
                timeout: 12000,
                maximumAge: 0
            }
        );
    }

    async function onLocationSuccess(position) {
        btnGetLocation.disabled = false;
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        const acc = position.coords.accuracy;

        try {
            const response = await fetch(`/api/location?lat=${lat}&lon=${lon}&acc=${acc}&lang=${BlindAssistA11y.state.language}`);
            const data = await response.json();

            if (data.success) {
                locResults.style.display = 'block';
                txtLatitude.textContent = `${data.latitude}°`;
                txtLongitude.textContent = `${data.longitude}°`;
                txtAccuracy.textContent = `± ${Math.round(data.accuracy || acc)} meters`;

                if (mapLink && data.map_url) {
                    mapLink.href = data.map_url;
                    mapLink.style.display = 'inline-flex';
                }

                updateStatus("Location detected successfully.");
                BlindAssistA11y.speak(data.speech);
            } else {
                updateStatus("Could not verify location coordinates.");
            }
        } catch (err) {
            console.error("Location API fetch error:", err);
            const fallbackSpeech = `Latitude is ${lat.toFixed(4)}, Longitude is ${lon.toFixed(4)}.`;
            txtLatitude.textContent = `${lat.toFixed(4)}°`;
            txtLongitude.textContent = `${lon.toFixed(4)}°`;
            txtAccuracy.textContent = `± ${Math.round(acc)} meters`;
            locResults.style.display = 'block';
            BlindAssistA11y.speak(`Your location coordinates: ${fallbackSpeech}`);
        }
    }

    function onLocationError(error) {
        btnGetLocation.disabled = false;
        let errMsg = "An unknown error occurred while retrieving location.";

        switch (error.code) {
            case error.PERMISSION_DENIED:
                errMsg = "Location permission denied. Please allow GPS location in your browser settings.";
                break;
            case error.POSITION_UNAVAILABLE:
                errMsg = "GPS position is unavailable. Please check your signal.";
                break;
            case error.TIMEOUT:
                errMsg = "Location request timed out. Please try again.";
                break;
        }

        updateStatus(errMsg);
        BlindAssistA11y.speak(errMsg);
    }

    function updateStatus(msg) {
        if (locStatus) {
            locStatus.textContent = msg;
        }
        BlindAssistA11y.announce(msg);
    }
});
