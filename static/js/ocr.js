/**
 * BLIND ASSIST - OCR Text Reader Module
 * Upload, camera capture, text extraction, and complete speech playback controls.
 */

document.addEventListener('DOMContentLoaded', function () {
    const video = document.getElementById('camera-feed-ocr');
    const placeholder = document.getElementById('camera-placeholder-ocr');
    const btnStartCamera = document.getElementById('btn-start-camera-ocr');
    const btnStopCamera = document.getElementById('btn-stop-camera-ocr');
    const btnCapture = document.getElementById('btn-capture-ocr');
    const fileInput = document.getElementById('file-upload-ocr');
    const resultsContainer = document.getElementById('ocr-results');
    const resultsText = document.getElementById('ocr-output-text');
    const statusNotice = document.getElementById('ocr-status');

    // Speech control buttons
    const btnRead = document.getElementById('btn-read-aloud');
    const btnPause = document.getElementById('btn-pause-speech');
    const btnResume = document.getElementById('btn-resume-speech');
    const btnStop = document.getElementById('btn-stop-speech');

    let stream = null;
    const canvas = document.createElement('canvas');
    let latestExtractedText = "";

    // Welcome announcement
    setTimeout(() => {
        BlindAssistA11y.speak("Text Reader page. You can capture text using your camera or upload a photo to have it read aloud.");
    }, 500);

    // Camera buttons
    if (btnStartCamera) btnStartCamera.addEventListener('click', startCamera);
    if (btnStopCamera) btnStopCamera.addEventListener('click', stopCamera);
    if (btnCapture) btnCapture.addEventListener('click', captureAndExtract);
    if (fileInput) fileInput.addEventListener('change', handleFileUpload);

    // Audio controls
    if (btnRead) {
        btnRead.addEventListener('click', () => {
            if (latestExtractedText) {
                BlindAssistA11y.speak(latestExtractedText);
            } else {
                BlindAssistA11y.speak("No text has been extracted yet.");
            }
        });
    }

    if (btnPause) {
        btnPause.addEventListener('click', () => BlindAssistA11y.pauseSpeech());
    }

    if (btnResume) {
        btnResume.addEventListener('click', () => BlindAssistA11y.resumeSpeech());
    }

    if (btnStop) {
        btnStop.addEventListener('click', () => BlindAssistA11y.stopSpeech());
    }

    async function startCamera() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            const err = "Camera is not supported in this browser.";
            updateStatus(err);
            BlindAssistA11y.speak(err);
            return;
        }

        try {
            updateStatus("Starting camera for text scanning...");
            stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: { ideal: "environment" }, width: { ideal: 1280 } }
            });

            video.srcObject = stream;
            video.style.display = 'block';
            if (placeholder) placeholder.style.display = 'none';

            btnStartCamera.style.display = 'none';
            btnStopCamera.style.display = 'inline-flex';
            btnCapture.disabled = false;

            updateStatus("Camera is ready. Position the text and press Capture.");
            BlindAssistA11y.speak("Camera ready. Position document in view and click Capture to read text.");

        } catch (err) {
            console.error("Camera access error:", err);
            const errMsg = "Camera access denied. Please allow camera permissions.";
            updateStatus(errMsg);
            BlindAssistA11y.speak(errMsg);
        }
    }

    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        video.srcObject = null;
        video.style.display = 'none';
        if (placeholder) placeholder.style.display = 'block';

        btnStartCamera.style.display = 'inline-flex';
        btnStopCamera.style.display = 'none';
        btnCapture.disabled = true;

        updateStatus("Camera stopped.");
        BlindAssistA11y.speak("Camera stopped.");
    }

    async function captureAndExtract() {
        if (!stream || !video.videoWidth) {
            updateStatus("Please start the camera first.");
            return;
        }

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
        sendToOCR(dataUrl);
    }

    function handleFileUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        if (!file.type.startsWith('image/')) {
            updateStatus("Please select an image file.");
            BlindAssistA11y.speak("Please select a valid image file.");
            return;
        }

        const reader = new FileReader();
        reader.onload = function (event) {
            sendToOCR(event.target.result);
        };
        reader.readAsDataURL(file);
    }

    async function sendToOCR(base64Image) {
        updateStatus("Processing document and extracting text...");
        BlindAssistA11y.speak("Processing document, extracting text now.");

        try {
            const response = await fetch('/api/ocr', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ image: base64Image })
            });

            const data = await response.json();

            if (data.success) {
                latestExtractedText = data.text.trim();
                resultsContainer.style.display = 'block';
                resultsText.textContent = latestExtractedText || "[No readable text detected]";

                const notice = `Text extraction complete. Found ${latestExtractedText.length} characters.`;
                updateStatus(notice);

                // Auto-read extracted text
                if (latestExtractedText) {
                    BlindAssistA11y.speak(`Extracted text: ${latestExtractedText}`);
                } else {
                    BlindAssistA11y.speak("No readable text found in the image. Please try taking a closer shot with good lighting.");
                }
            } else {
                const err = data.error || "Failed to extract text.";
                updateStatus(err);
                BlindAssistA11y.speak(err);
            }
        } catch (error) {
            console.error("OCR request error:", error);
            const err = "Failed to communicate with OCR server.";
            updateStatus(err);
            BlindAssistA11y.speak(err);
        }
    }

    function updateStatus(msg) {
        if (statusNotice) {
            statusNotice.textContent = msg;
        }
        BlindAssistA11y.announce(msg);
    }
});
