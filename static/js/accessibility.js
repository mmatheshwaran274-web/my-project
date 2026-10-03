/**
 * BLIND ASSIST - Accessibility & Assistive Engine
 * Provides Text-to-Speech (SpeechSynthesis), Tamil translation,
 * Font scaling, High contrast toggling, and Global Keyboard Navigation.
 */

const BlindAssistA11y = (function () {
    // Translation dictionary for Tamil / English
    const translations = {
        en: {
            brand: "Blind Assist",
            tagline: "Smart Assistance for Independent Living",
            home: "Home",
            dashboard: "Dashboard",
            profile: "Profile",
            settings: "Settings",
            logout: "Logout",
            login: "Login",
            register: "Register",
            voice_assistant: "Voice Assistant",
            voice_subtitle: "Speak a command",
            object_detection: "Object Detection",
            object_subtitle: "Identify objects around you",
            read_text: "Read Text",
            read_subtitle: "Read text from an image",
            my_location: "My Location",
            location_subtitle: "Get your current location",
            emergency: "Emergency",
            emergency_subtitle: "Get emergency assistance",
            activity_history: "Activity History",
            history_subtitle: "View recent activities",
            welcome: "Welcome",
            get_started: "GET STARTED",
            start_camera: "Start Camera",
            stop_camera: "Stop Camera",
            capture_image: "Capture & Process",
            upload_image: "Upload Image",
            read_aloud: "Read Aloud",
            pause_speech: "Pause Speech",
            resume_speech: "Resume Speech",
            stop_speech: "Stop Speech",
            confirm: "CONFIRM EMERGENCY",
            cancel: "CANCEL",
            listening: "Listening... Speak now",
            press_to_speak: "Press to Speak",
            emergency_prompt: "Are you sure you want to activate emergency assistance?"
        },
        ta: {
            brand: "பிளைண்ட் அசிஸ்ட்",
            tagline: "சுயாதீன வாழ்விற்கான ஸ்மார்ட் உதவி",
            home: "முகப்பு",
            dashboard: "டாஷ்போர்டு",
            profile: "சுயவிவரம்",
            settings: "அமைப்புகள்",
            logout: "வெளியேறு",
            login: "உள்நுழை",
            register: "பதிவு செய்க",
            voice_assistant: "குரல் உதவியாளர்",
            voice_subtitle: "கட்டளையை பேசவும்",
            object_detection: "பொருள் கண்டறிதல்",
            object_subtitle: "சுற்றியுள்ள பொருட்களை அறியுங்கள்",
            read_text: "உரையை படிக்க",
            read_subtitle: "படத்திலிருந்து உரையைப் படியுங்கள்",
            my_location: "என் இருப்பிடம்",
            location_subtitle: "தற்போதைய இருப்பிடத்தைப் பெறுங்கள்",
            emergency: "அவசர உதவி",
            emergency_subtitle: "அவசர உதவியைப் பெறுங்கள்",
            activity_history: "செயல்பாட்டு வரலாறு",
            history_subtitle: "சமீபத்திய செயல்பாடுகளைப் பாருங்கள்",
            welcome: "வரவேற்கிறோம்",
            get_started: "தொடங்குங்கள்",
            start_camera: "கேமராவைத் தொடங்கு",
            stop_camera: "கேமராவை நிறுத்து",
            capture_image: "படம் எடுத்து செயல்முறை செய்",
            upload_image: "படத்தை பதிவேற்று",
            read_aloud: "சத்தமாக படிக்கவும்",
            pause_speech: "பேச்சை இடைநிறுத்து",
            resume_speech: "மீண்டும் பேசவும்",
            stop_speech: "பேச்சை நிறுத்து",
            confirm: "அவசர உதவியை உறுதி செய்",
            cancel: "ரத்து செய்",
            listening: "கேட்கிறது... இப்போது பேசவும்",
            press_to_speak: "பேச அழுத்தவும்",
            emergency_prompt: "அவசர உதவியை இயக்க விரும்புகிறீர்களா?"
        }
    };

    // State management
    const state = {
        voiceEnabled: true,
        speechSpeed: 1.0,
        highContrast: false,
        fontSize: 'medium',
        language: 'en'
    };

    // SpeechSynthesis instance
    const synth = window.speechSynthesis;
    let currentUtterance = null;

    function init() {
        loadPreferences();
        applyPreferences();
        bindGlobalKeyboardShortcuts();
        setupAnnouncer();
    }

    function loadPreferences() {
        const saved = localStorage.getItem('blind_assist_settings');
        if (saved) {
            try {
                Object.assign(state, JSON.parse(saved));
            } catch (e) {
                console.error("Error loading local settings:", e);
            }
        }
    }

    function savePreferences() {
        localStorage.setItem('blind_assist_settings', JSON.stringify(state));
    }

    function applyPreferences() {
        // High Contrast
        if (state.highContrast) {
            document.body.classList.add('high-contrast');
        } else {
            document.body.classList.remove('high-contrast');
        }

        // Font Size
        document.body.classList.remove('font-small', 'font-medium', 'font-large', 'font-xlarge');
        document.body.classList.add(`font-${state.fontSize}`);

        // Language Translations
        applyLanguage(state.language);
    }

    function setHighContrast(enabled) {
        state.highContrast = !!enabled;
        applyPreferences();
        savePreferences();
        announce(state.highContrast ? "High contrast mode enabled." : "High contrast mode disabled.");
    }

    function toggleHighContrast() {
        setHighContrast(!state.highContrast);
    }

    function setFontSize(size) {
        if (['small', 'medium', 'large', 'xlarge', 'x-large'].includes(size)) {
            state.fontSize = size.replace('x-large', 'xlarge');
            applyPreferences();
            savePreferences();
            announce(`Font size changed to ${size}.`);
        }
    }

    function setSpeechSpeed(speed) {
        const val = parseFloat(speed);
        if (!isNaN(val) && val >= 0.5 && val <= 2.5) {
            state.speechSpeed = val;
            savePreferences();
            speak(`Speech speed set to ${val} times.`);
        }
    }

    function setLanguage(lang) {
        if (lang === 'en' || lang === 'ta') {
            state.language = lang;
            applyPreferences();
            savePreferences();
            const msg = lang === 'ta' ? "தமிழ் மொழி தேர்ந்தெடுக்கப்பட்டது." : "English language selected.";
            speak(msg);
        }
    }

    function applyLanguage(lang) {
        const dict = translations[lang] || translations.en;
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (dict[key]) {
                if (el.tagName === 'INPUT' && (el.type === 'button' || el.type === 'submit')) {
                    el.value = dict[key];
                } else {
                    el.textContent = dict[key];
                }
            }
        });
    }

    // Text to Speech Controls
    function speak(text, interrupt = true) {
        if (!state.voiceEnabled || !synth || !text) return;

        if (interrupt) {
            synth.cancel();
        }

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = state.speechSpeed || 1.0;
        utterance.lang = state.language === 'ta' ? 'ta-IN' : 'en-US';

        // Select voice if available
        const voices = synth.getVoices();
        const preferredVoice = voices.find(v => v.lang.startsWith(state.language));
        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }

        currentUtterance = utterance;
        synth.speak(utterance);
    }

    function pauseSpeech() {
        if (synth && synth.speaking) {
            synth.pause();
            announce("Speech paused.");
        }
    }

    function resumeSpeech() {
        if (synth && synth.paused) {
            synth.resume();
            announce("Speech resumed.");
        }
    }

    function stopSpeech() {
        if (synth) {
            synth.cancel();
            announce("Speech stopped.");
        }
    }

    // ARIA Live Announcer
    function setupAnnouncer() {
        let announcer = document.getElementById('a11y-announcer');
        if (!announcer) {
            announcer = document.createElement('div');
            announcer.id = 'a11y-announcer';
            announcer.className = 'visually-hidden';
            announcer.setAttribute('aria-live', 'assertive');
            announcer.setAttribute('aria-atomic', 'true');
            document.body.appendChild(announcer);
        }
    }

    function announce(message) {
        const announcer = document.getElementById('a11y-announcer');
        if (announcer) {
            announcer.textContent = '';
            setTimeout(() => {
                announcer.textContent = message;
            }, 50);
        }
    }

    // Keyboard Shortcuts
    function bindGlobalKeyboardShortcuts() {
        document.addEventListener('keydown', function (e) {
            // Alt + H: Toggle High Contrast
            if (e.altKey && (e.key === 'h' || e.key === 'H')) {
                e.preventDefault();
                toggleHighContrast();
            }
            // Alt + M: Mic / Voice Assistant
            if (e.altKey && (e.key === 'm' || e.key === 'M')) {
                e.preventDefault();
                window.location.href = '/voice';
            }
            // Alt + E: Emergency
            if (e.altKey && (e.key === 'e' || e.key === 'E')) {
                e.preventDefault();
                window.location.href = '/emergency';
            }
            // Alt + D: Dashboard
            if (e.altKey && (e.key === 'd' || e.key === 'D')) {
                e.preventDefault();
                window.location.href = '/dashboard';
            }
            // Alt + S: Stop speech
            if (e.altKey && (e.key === 's' || e.key === 'S')) {
                e.preventDefault();
                stopSpeech();
            }
        });
    }

    return {
        init,
        state,
        speak,
        pauseSpeech,
        resumeSpeech,
        stopSpeech,
        announce,
        setHighContrast,
        toggleHighContrast,
        setFontSize,
        setSpeechSpeed,
        setLanguage,
        translations
    };
})();

document.addEventListener('DOMContentLoaded', BlindAssistA11y.init);
