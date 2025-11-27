(function () {
  const ttsLangMap = {
    en: 'en-US',
    sw: 'sw-KE',
    sheng: 'en-US',
    ki: 'en-US',
    so: 'so-SO',
  };

  let currentUtterance = null;

  function getUserLanguageCode() {
    if (typeof window !== 'undefined' && window.USER_LANGUAGE_CODE) {
      return String(window.USER_LANGUAGE_CODE || 'en').toLowerCase();
    }
    return 'en';
  }

  function getTtsLang() {
    const code = getUserLanguageCode();
    return ttsLangMap[code] || 'en-US';
  }

  function startReading(selector) {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      alert('Text-to-speech is not supported in this browser.');
      return;
    }

    const el = document.querySelector(selector);
    if (!el) return;

    const text = (el.innerText || el.textContent || '').trim();
    if (!text) return;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = getTtsLang();
    currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
  }

  function stopReading() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      currentUtterance = null;
    }
  }

  // Expose helpers globally for templates to call
  if (typeof window !== 'undefined') {
    window.startReading = startReading;
    window.stopReading = stopReading;
  }
})();
