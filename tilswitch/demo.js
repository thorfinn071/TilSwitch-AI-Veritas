const workspace = element.closest("#workspace");

function syncDraft() {
    const source = workspace.querySelector("#source-text textarea");
    const original = element.querySelector(".analysis-original");
    if (!source || !original) {
        return;
    }
    const outdated = source.value !== original.textContent.replace(/\r\n?/g, "\n");
    element.querySelector(".stale-result").hidden = !outdated;
    element.querySelector(".analysis-content").hidden = outdated;
}

workspace.addEventListener("input", (event) => {
    if (event.target.matches("#source-text textarea")) {
        syncDraft();
    }
});
watch("value", syncDraft);

element.addEventListener("click", async (event) => {
    const button = event.target.closest(".copy-phrase");
    if (!button || button.closest(".analysis-content").hidden) {
        return;
    }
    const phrase = button.closest("li").querySelector(".segment-content");
    const feedback = element.querySelector(".copy-status");
    element.querySelectorAll(".copy-phrase").forEach((action) => {
        action.textContent = "Copy";
    });
    try {
        await navigator.clipboard.writeText(phrase.textContent);
        button.textContent = "Copied";
        feedback.textContent = "Phrase copied.";
    } catch {
        const range = document.createRange();
        range.selectNodeContents(phrase);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        feedback.textContent = "Phrase selected. Use your device’s Copy command.";
    }
});
