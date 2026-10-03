/**
 * BLIND ASSIST - Voice Assistant Module
 * Uses Web Speech API (webkitSpeechRecognition) and connects to /api/voice.
 */

document.addEventListener('DOMContentLoaded', function () {
    const micButton = document.getElementById('mic-button');
    const micStatus = document.getElementById('mic-status');
    const transcriptBox = document.getElementById('voice-transcript');
    const fallbackContainer = document.getElementById('voice-fallback-container');
    const fallbackInput = document.getElementById('voice-fallback-input');
    const fallbackSubmit = document.getElementById('voice-fallback-submit');

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isListening = false;

    // Initial Spoken Instructions
    setTimeout(() => {
        BlindAssistA11y.speak("Voice Assistant ready. Click the microphone or press Space to speak a command.");
    }, 500);

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = function () {
            isListening = true;
            micButton.classList.add('listening');
            micButton.setAttribute('aria-pressed', 'true');
            const statusMsg = BlindAssistA11y.state.language === 'ta' ? "கேட்கிறது... இப்போது பேசவும்" : "Listening... Speak now";
            micStatus.textContent = statusMsg;
            BlindAssistA11y.announce(statusMsg);
        };

        recognition.onresult = function (event) {
            const transcript = event.results[0][0].transcript;
            if (transcriptBox) {
                transcriptBox.textContent = `"${transcript}"`;
            }
            handleVoiceCommand(transcript);
        };

        recognition.onerror = function (event) {
            isListening = false;
            micButton.classList.remove('listening');
            micButton.setAttribute('aria-pressed', 'false');
            let errorMsg = `Speech recognition error: ${event.error}`;
            if (event.error === 'no-speech') {
                errorMsg = "No speech was detected. Please try speaking again.";
            } else if (event.error === 'not-allowed') {
                errorMsg = "Microphone access was denied. Please allow microphone permissions.";
            }
            micStatus.textContent = errorMsg;
            BlindAssistA11y.speak(errorMsg);
        };

        recognition.onend = function () {
            isListening = false;
            micButton.classList.remove('listening');
            micButton.setAttribute('aria-pressed', 'false');
            if (micStatus.textContent.includes("Listening")) {
                micStatus.textContent = "Processing command...";
            }
        };

        micButton.addEventListener('click', toggleListening);
        micButton.addEventListener('keydown', function (e) {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                toggleListening();
            }
        });
    } else {
        // Fallback for browsers without Web Speech Recognition (e.g. Firefox)
        if (micStatus) {
            micStatus.textContent = "Speech recognition is not supported in this browser. Please type your command below.";
        }
        if (fallbackContainer) {
            fallbackContainer.style.display = 'block';
        }
        BlindAssistA11y.speak("Speech recognition is not supported in this browser. You can type your command.");
    }

    function toggleListening() {
        if (!recognition) return;
        if (isListening) {
            recognition.stop();
        } else {
            recognition.lang = BlindAssistA11y.state.language === 'ta' ? 'ta-IN' : 'en-US';
            try {
                recognition.start();
            } catch (err) {
                console.warn("Recognition already started:", err);
            }
        }
    }

    async function handleVoiceCommand(commandText) {
        micStatus.textContent = `Analyzing: "${commandText}"`;
        BlindAssistA11y.announce(`Command recognized: ${commandText}`);

        try {
            const response = await fetch('/api/voice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    command: commandText,
                    language: BlindAssistA11y.state.language
                })
            });

            const data = await response.json();

            if (data.speech) {
                BlindAssistA11y.speak(data.speech);
            }

            if (data.action === 'navigate' && data.url) {
                micStatus.textContent = `Navigating to ${data.label || data.url}...`;
                setTimeout(() => {
                    window.location.href = data.url;
                }, 1300);
            } else {
                micStatus.textContent = data.speech || "Command executed.";
            }

        } catch (error) {
            console.error("API error processing voice command:", error);
            const errSpeech = "Sorry, unable to process your voice command right now.";
            micStatus.textContent = errSpeech;
            BlindAssistA11y.speak(errSpeech);
        }
    }

    // Fallback form submission
    if (fallbackSubmit && fallbackInput) {
        fallbackSubmit.addEventListener('click', () => {
            const val = fallbackInput.value.trim();
            if (val) {
                handleVoiceCommand(val);
                fallbackInput.value = '';
            }
        });
        fallbackInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                fallbackSubmit.click();
            }
        });
    }
});
