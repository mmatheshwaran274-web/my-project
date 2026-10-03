/**
 * BLIND ASSIST - AI Image Analysis & Computer Vision Module
 * Handles file upload, image preview, multipart/form-data transmission to /api/analyze-image,
 * rich structured detail rendering, and browser Text-to-Speech (TTS).
 */

document.addEventListener('DOMContentLoaded', function () {
    const video = document.getElementById('camera-feed');
    const placeholder = document.getElementById('camera-placeholder');
    const previewContainer = document.getElementById('image-preview-container');
    const previewImg = document.getElementById('image-preview');
    const fileInfo = document.getElementById('image-file-info');

    const btnStartCamera = document.getElementById('btn-start-camera');
    const btnStopCamera = document.getElementById('btn-stop-camera');
    const btnCapture = document.getElementById('btn-capture-vision');
    const btnUploadImage = document.getElementById('btn-upload-image');
    const fileInput = document.getElementById('file-upload-vision');
    const btnAnalyze = document.getElementById('btn-analyze-image');
    const btnClear = document.getElementById('btn-clear-image');

    const resultsContainer = document.getElementById('vision-results');
    const resultsText = document.getElementById('vision-output-text');
    const detectedTags = document.getElementById('detected-tags');
    const statusNotice = document.getElementById('vision-status');
    const btnReadAloud = document.getElementById('btn-read-aloud');
    const modelBadge = document.getElementById('ai-model-badge');

    const apiErrorBox = document.getElementById('analysis-api-error');
    const apiErrorText = document.getElementById('analysis-api-error-text');
    const detailScene = document.getElementById('detail-scene');
    const detailPeople = document.getElementById('detail-people');
    const detailColors = document.getElementById('detail-colors');
    const detailText = document.getElementById('detail-text');
    const detailGuidance = document.getElementById('detail-guidance');

    let stream = null;
    let selectedFile = null;
    let lastSpokenText = "";
    const canvas = document.createElement('canvas');

    // Speech helper with SpeechSynthesis fallback
    function speakText(text) {
        if (!text) return;
        if (typeof BlindAssistA11y !== 'undefined' && BlindAssistA11y.speak) {
            BlindAssistA11y.speak(text);
        } else if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            window.speechSynthesis.speak(utterance);
        }
    }

    // Spoken welcome announcement on page load
    setTimeout(() => {
        speakText("Object Detection and Image Analysis page. Upload a photo or start camera to analyze your surroundings.");
    }, 600);

    // 1. Upload Button -> Triggers native system file picker
    if (btnUploadImage && fileInput) {
        btnUploadImage.addEventListener('click', function (e) {
            e.preventDefault();
            fileInput.value = '';
            fileInput.click();
        });
    }

    // 2. File Selection Handler -> Validates, shows immediate preview, shows Analyze button
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelection);
    }

    // 3. Analyze Image Button -> Sends multipart/form-data to /api/analyze-image
    if (btnAnalyze) {
        btnAnalyze.addEventListener('click', function () {
            if (!selectedFile) {
                const msg = "Please select or upload an image first.";
                updateStatus(msg, true);
                speakText(msg);
                return;
            }
            sendMultipartAnalysis(selectedFile);
        });
    }

    // 4. Clear Image Button -> Resets state
    if (btnClear) {
        btnClear.addEventListener('click', clearSelectedImage);
    }

    // 5. Camera Controls
    if (btnStartCamera) {
        btnStartCamera.addEventListener('click', startCamera);
    }

    if (btnStopCamera) {
        btnStopCamera.addEventListener('click', stopCamera);
    }

    if (btnCapture) {
        btnCapture.addEventListener('click', captureAndAnalyze);
    }

    // 6. Read Aloud Button
    if (btnReadAloud) {
        btnReadAloud.addEventListener('click', function () {
            const textToSpeak = lastSpokenText || (resultsText ? resultsText.textContent : "");
            if (textToSpeak) {
                speakText(textToSpeak);
            }
        });
    }

    /**
     * Handles file selection:
     * - Validates JPG/JPEG/PNG
     * - Displays image preview immediately
     * - Reveals Analyze button
     */
    function handleFileSelection(e) {
        const file = e.target.files && e.target.files[0];
        if (!file) return;

        const validMimes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
        const fileName = (file.name || '').toLowerCase();
        const hasValidExt = fileName.endsWith('.jpg') || fileName.endsWith('.jpeg') || fileName.endsWith('.png') || fileName.endsWith('.webp');

        if (!validMimes.includes(file.type) && !hasValidExt) {
            const errMsg = "Invalid file format. Please select a JPG, JPEG, or PNG image.";
            updateStatus(errMsg, true);
            speakText(errMsg);
            fileInput.value = '';
            return;
        }

        selectedFile = file;

        // Stop camera cleanly if running
        if (stream) {
            stopCamera();
        }

        const reader = new FileReader();
        reader.onload = function (event) {
            const dataUrl = event.target.result;

            if (placeholder) placeholder.style.display = 'none';
            if (video) video.style.display = 'none';
            if (previewContainer) previewContainer.style.display = 'block';
            if (previewImg) previewImg.src = dataUrl;

            if (fileInfo) {
                const sizeKb = (file.size / 1024).toFixed(1);
                fileInfo.textContent = 'Selected: ' + file.name + ' (' + sizeKb + ' KB)';
            }

            // Show Analyze and Clear buttons
            if (btnAnalyze) {
                btnAnalyze.style.display = 'inline-flex';
                btnAnalyze.disabled = false;
                btnAnalyze.innerHTML = '&#128269; Analyze Image';
            }
            if (btnClear) {
                btnClear.style.display = 'inline-flex';
            }

            if (resultsContainer) resultsContainer.style.display = 'none';

            const readyMsg = "Image loaded successfully. Click 'Analyze Image' to begin.";
            updateStatus(readyMsg);
            speakText(readyMsg);
        };

        reader.onerror = function () {
            const err = "Failed to read the selected file.";
            updateStatus(err, true);
            speakText(err);
        };

        reader.readAsDataURL(file);
    }

    /**
     * Resets the selected image, hides preview, and restores initial state.
     */
    function clearSelectedImage() {
        selectedFile = null;
        if (fileInput) fileInput.value = '';

        if (previewContainer) previewContainer.style.display = 'none';
        if (previewImg) previewImg.src = '';
        if (fileInfo) fileInfo.textContent = '';

        if (btnAnalyze) btnAnalyze.style.display = 'none';
        if (btnClear) btnClear.style.display = 'none';
        if (resultsContainer) resultsContainer.style.display = 'none';

        if (!stream && placeholder) {
            placeholder.style.display = 'block';
        }

        updateStatus("Image cleared. Ready.");
        speakText("Image cleared.");
    }

    /**
     * Starts live camera feed.
     */
    async function startCamera() {
        clearSelectedImage();

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            const err = "Camera API is not supported in this browser.";
            updateStatus(err, true);
            speakText(err);
            return;
        }

        try {
            updateStatus("Requesting camera access...");
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: { ideal: "environment" },
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            });

            if (video) {
                video.srcObject = stream;
                video.style.display = 'block';
            }
            if (placeholder) placeholder.style.display = 'none';
            if (previewContainer) previewContainer.style.display = 'none';

            if (btnStartCamera) btnStartCamera.style.display = 'none';
            if (btnStopCamera) btnStopCamera.style.display = 'inline-flex';
            if (btnCapture) btnCapture.disabled = false;

            const msg = "Camera active. Frame objects and click 'Capture & Analyze'.";
            updateStatus(msg);
            speakText(msg);

        } catch (err) {
            console.error("Camera access error:", err);
            let errMsg = "Camera access denied. Please allow camera permissions in your browser.";
            if (err.name === 'NotFoundError') {
                errMsg = "No camera hardware was found on your device.";
            }
            updateStatus(errMsg, true);
            speakText(errMsg);
        }
    }

    /**
     * Stops live camera stream.
     */
    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        if (video) {
            video.srcObject = null;
            video.style.display = 'none';
        }
        if (placeholder && (!previewContainer || previewContainer.style.display === 'none')) {
            placeholder.style.display = 'block';
        }

        if (btnStartCamera) btnStartCamera.style.display = 'inline-flex';
        if (btnStopCamera) btnStopCamera.style.display = 'none';
        if (btnCapture) btnCapture.disabled = true;

        updateStatus("Camera stopped.");
        speakText("Camera stopped.");
    }

    /**
     * Captures current frame from video and sends as a multipart File.
     */
    function captureAndAnalyze() {
        if (!stream || !video || !video.videoWidth) {
            const msg = "Please start the camera first.";
            updateStatus(msg, true);
            speakText(msg);
            return;
        }

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(function (blob) {
            if (!blob) {
                updateStatus("Failed to capture image frame.", true);
                return;
            }
            const file = new File([blob], 'camera_capture.jpg', { type: 'image/jpeg' });
            sendMultipartAnalysis(file);
        }, 'image/jpeg', 0.9);
    }

    /**
     * Sends the image file to the backend POST /api/analyze-image endpoint
     * using multipart/form-data.
     */
    async function sendMultipartAnalysis(fileObj) {
        updateStatus("Sending image to Vision AI for analysis...");
        speakText("Analyzing image, please wait.");

        if (btnAnalyze) {
            btnAnalyze.disabled = true;
            btnAnalyze.innerHTML = '&#8987; Analyzing...';
        }
        if (btnCapture) {
            btnCapture.disabled = true;
        }

        try {
            const userLang = (typeof BlindAssistA11y !== 'undefined' && BlindAssistA11y.state && BlindAssistA11y.state.language) 
                ? BlindAssistA11y.state.language 
                : 'en';

            const formData = new FormData();
            formData.append('image', fileObj);
            formData.append('language', userLang);

            // POST /api/analyze-image using multipart/form-data (browser sets boundary automatically)
            const response = await fetch('/api/analyze-image', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                renderFullAnalysisResults(data);
            } else {
                const err = (data && data.error) ? data.error : "Image analysis failed to process the image.";
                updateStatus(err, true);
                speakText(err);
                if (apiErrorBox && apiErrorText) {
                    apiErrorText.textContent = err;
                    apiErrorBox.style.display = 'block';
                }
            }
        } catch (error) {
            console.error("Vision AI request failed:", error);
            const err = "Network connection to the vision service failed. Please check your internet connection.";
            updateStatus(err, true);
            speakText(err);
        } finally {
            if (btnAnalyze) {
                btnAnalyze.disabled = false;
                btnAnalyze.innerHTML = '&#128269; Analyze Image';
            }
            if (btnCapture && stream) {
                btnCapture.disabled = false;
            }
        }
    }

    /**
     * Displays the complete returned analysis details clearly on the webpage:
     * - Scene/environment description
     * - Objects present & count
     * - People count
     * - Colors & visual details
     * - Visible text
     * - Assistive guidance
     * - Voice speech output
     */
    function renderFullAnalysisResults(data) {
        if (resultsContainer) resultsContainer.style.display = 'block';

        // 1. Model Badge
        if (modelBadge) {
            modelBadge.textContent = data.model || "Vision AI";
        }

        // 2. API Error Notice (Requirement 10: Show actual error if API failed)
        if (apiErrorBox && apiErrorText) {
            if (data.api_error) {
                apiErrorText.textContent = data.api_error;
                apiErrorBox.style.display = 'block';
            } else {
                apiErrorBox.style.display = 'none';
            }
        }

        // 3. Scene & Environment
        if (detailScene) {
            detailScene.textContent = data.scene_description || "Scene analysis unavailable.";
        }

        // 4. Objects & People Tags
        if (detectedTags) {
            detectedTags.innerHTML = '';
            const objects = data.objects || [];
            if (objects.length === 0 && (!data.objects_present || data.objects_present.length === 0)) {
                const tag = document.createElement('span');
                tag.className = 'btn btn-outline';
                tag.style.fontSize = '0.9rem';
                tag.textContent = "No specific objects identified";
                detectedTags.appendChild(tag);
            } else {
                const list = (data.objects_present && data.objects_present.length > 0) 
                    ? data.objects_present 
                    : objects.map(o => o.label);

                list.forEach(item => {
                    const labelText = (typeof item === 'string') ? item : (item.label || 'Object');
                    const tag = document.createElement('span');
                    tag.className = 'btn btn-outline';
                    tag.style.margin = '2px';
                    tag.style.fontSize = '0.95rem';
                    tag.style.fontWeight = '700';
                    tag.style.cursor = 'default';
                    tag.textContent = labelText;
                    detectedTags.appendChild(tag);
                });
            }
        }

        if (detailPeople) {
            detailPeople.textContent = 'People Count: ' + (data.people_count !== undefined ? data.people_count : 'None');
        }

        // 5. Colors & Visual Characteristics
        if (detailColors) {
            detailColors.textContent = data.colors_description || "Visual color profile analyzed.";
        }

        // 6. Visible Text
        if (detailText) {
            detailText.textContent = data.text_visible || "None detected";
        }

        // 7. Assistive Guidance
        if (detailGuidance) {
            detailGuidance.textContent = data.assistive_guidance || "No immediate navigational hazards detected.";
        }

        // 8. Spoken Speech Output
        const speech = data.speech || "Image analysis completed.";
        lastSpokenText = speech;
        if (resultsText) {
            resultsText.textContent = speech;
        }

        updateStatus("Analysis complete. Details displayed below.");

        // Automatic voice readout for blind/visually impaired user
        speakText(speech);
    }

    /**
     * Updates status notice and announces to screen reader.
     */
    function updateStatus(msg, isError = false) {
        if (statusNotice) {
            statusNotice.textContent = msg;
            statusNotice.style.color = isError ? 'var(--accent-red, #dc2626)' : 'var(--primary)';
        }
        if (typeof BlindAssistA11y !== 'undefined' && BlindAssistA11y.announce) {
            BlindAssistA11y.announce(msg);
        }
    }
});
