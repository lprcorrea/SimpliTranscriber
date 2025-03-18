document.addEventListener("DOMContentLoaded", function () {
    const copyBtn = document.getElementById("copy-btn");
    const translateBtn = document.getElementById("translate-btn");
    const transcriptionText = document.getElementById("transcription-text");
    const translatedText = document.getElementById("translated-text");
    const subtitleDiv = document.getElementById("karaoke-subtitles");
    const audioPlayer = document.getElementById("audio-player");

    // Copiar texto para a área de transferência
    copyBtn.addEventListener("click", async function () {
        try {
            await navigator.clipboard.writeText(transcriptionText.value);
            copyBtn.textContent = "COPIADO!";
            setTimeout(() => copyBtn.textContent = "COPIAR", 2000);
        } catch (err) {
            alert("Erro ao copiar o texto.");
            console.error(err);
        }
    });

    // Tradução do texto
    translateBtn.addEventListener("click", async function () {
        const language = document.getElementById("language-select").value;
        const originalText = transcriptionText.value;

        // Mostrar indicador de carregamento
        translateBtn.textContent = "Traduzindo...";
        translateBtn.disabled = true;

        try {
            const response = await fetch('/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: originalText, language })
            });

            const data = await response.json();
            
            // Exibir a tradução
            translatedText.value = data.translated_text;
            translatedText.style.display = "block";
            
        } catch (error) {
            alert("Erro ao traduzir o texto.");
            console.error(error);
        } finally {
            translateBtn.textContent = "Traduzir";
            translateBtn.disabled = false;
        }
    });

    // Sincronização de legendas
    const subtitles = [
        { time: 0, text: "Aqui começa a música..." },
        { time: 3, text: "Palavras sincronizadas..." },
        { time: 6, text: "Outra frase importante..." },
        { time: 10, text: "E assim por diante..." }
    ];

    audioPlayer.addEventListener("timeupdate", () => {
        // Encontrar a legenda correspondente
        let currentSubtitle = subtitles.find((s, index) => {
            const next = subtitles[index + 1];
            return audioPlayer.currentTime >= s.time && (!next || audioPlayer.currentTime < next.time);
        });

        if (currentSubtitle) {
            subtitleDiv.textContent = currentSubtitle.text;
        } else {
            subtitleDiv.textContent = "";
        }
    });
});