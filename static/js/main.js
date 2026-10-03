/**
 * BLIND ASSIST - Main Application Logic
 * Card focus announcements, header toggles, and accessible form handling.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Announce page title on entry
    const pageHeading = document.querySelector('h1');
    if (pageHeading) {
        const titleText = pageHeading.innerText.trim();
        // Give slight delay for page render
        setTimeout(() => {
            BlindAssistA11y.announce(`Loaded page: ${titleText}`);
        }, 300);
    }

    // Attach voice feedback to dashboard cards on keyboard focus or mouse hover
    const dashCards = document.querySelectorAll('.dash-card');
    dashCards.forEach(card => {
        const title = card.querySelector('.dash-card-title')?.innerText || '';
        const subtitle = card.querySelector('.dash-card-subtitle')?.innerText || '';
        const speechText = `${title}. ${subtitle}. Press Enter or click to open.`;

        card.addEventListener('focus', () => {
            BlindAssistA11y.announce(speechText);
        });
    });

    // Quick Contrast Toggle Button in Header
    const contrastBtn = document.getElementById('header-contrast-toggle');
    if (contrastBtn) {
        contrastBtn.addEventListener('click', () => {
            BlindAssistA11y.toggleHighContrast();
        });
    }

    // Quick Language Toggle Button in Header
    const langBtn = document.getElementById('header-lang-toggle');
    if (langBtn) {
        langBtn.addEventListener('click', () => {
            const nextLang = BlindAssistA11y.state.language === 'en' ? 'ta' : 'en';
            BlindAssistA11y.setLanguage(nextLang);
            langBtn.textContent = nextLang === 'en' ? 'தமிழ்' : 'English';
        });
    }
});
