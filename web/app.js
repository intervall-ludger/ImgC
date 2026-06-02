import init, { convert, convert_to_gif } from "./pkg/imgc.js";

const fileInput = document.getElementById("file-input");
const dropzone = document.getElementById("dropzone");
const fileList = document.getElementById("file-list");
const formatSelect = document.getElementById("format");
const convertBtn = document.getElementById("convert");
const statusEl = document.getElementById("status");

let files = [];
let isReady = false;

init().then(() => {
    isReady = true;
    refreshButton();
});

function refreshButton() {
    convertBtn.disabled = !isReady || files.length === 0;
}

function setStatus(message, isError = false) {
    statusEl.textContent = message;
    statusEl.classList.toggle("error", isError);
}

function addFiles(selected) {
    files = files.concat(Array.from(selected));
    // Build the list via textContent so crafted file names can't inject markup.
    fileList.replaceChildren(
        ...files.map((f) => {
            const li = document.createElement("li");
            li.textContent = f.name;
            return li;
        })
    );
    refreshButton();
}

fileInput.addEventListener("change", (e) => addFiles(e.target.files));

["dragenter", "dragover"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    })
);
["dragleave", "drop"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
    })
);
dropzone.addEventListener("drop", (e) => addFiles(e.dataTransfer.files));

// Show only the options that apply to the chosen format.
function updateOptionVisibility() {
    const format = formatSelect.value;
    const groups = {
        size: format !== "gif" && format !== "ico",
        fps: format === "gif",
        icon: format === "ico",
    };
    document.querySelectorAll("[data-group]").forEach((el) => {
        el.hidden = !groups[el.dataset.group];
    });
}
formatSelect.addEventListener("change", updateOptionVisibility);
updateOptionVisibility();

function numberOrUndefined(id) {
    const value = parseFloat(document.getElementById(id).value);
    return Number.isFinite(value) && value > 0 ? value : undefined;
}

function download(bytes, filename) {
    const blob = new Blob([bytes]);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function rename(name, ext) {
    const dot = name.lastIndexOf(".");
    const stem = dot > 0 ? name.slice(0, dot) : name;
    return `${stem}.${ext}`;
}

async function bytesOf(file) {
    return new Uint8Array(await file.arrayBuffer());
}

convertBtn.addEventListener("click", async () => {
    const format = formatSelect.value;
    const fps = parseInt(document.getElementById("fps").value, 10) || 30;
    const iconSize = parseInt(document.getElementById("icon-size").value, 10) || 64;
    const maxMb = numberOrUndefined("max-size");
    const minMb = numberOrUndefined("min-size");

    convertBtn.disabled = true;
    setStatus("Converting...");

    try {
        if (format === "gif" && files.length > 1) {
            const frames = await Promise.all(files.map(bytesOf));
            const out = convert_to_gif(frames, fps);
            download(out, rename(files[0].name, "gif"));
        } else {
            for (const file of files) {
                const out = convert(await bytesOf(file), format, maxMb, minMb, fps, iconSize);
                download(out, rename(file.name, format));
            }
        }
        setStatus(`Done. Converted ${files.length} file(s).`);
    } catch (err) {
        setStatus(err.message || String(err), true);
    } finally {
        refreshButton();
    }
});
