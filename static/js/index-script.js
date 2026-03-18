// ── Theme ────────────────────────────────────────────────────────────────────
(function initTheme() {
  var saved = localStorage.getItem("theme");
  var prefer = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", saved || prefer);
})();

document.getElementById("theme-toggle").addEventListener("click", function () {
  var current = document.documentElement.getAttribute("data-theme");
  var next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("theme", next);
});

// ── Auto-expanding textarea ──────────────────────────────────────────────────
var qrInput = document.getElementById("qr-input");

function autoResize() {
  qrInput.style.height = "auto";
  qrInput.style.height = qrInput.scrollHeight + "px";
}

qrInput.addEventListener("input", autoResize);
qrInput.addEventListener("change", function () {
  if (!qrInput.value) qrInput.style.height = "";
});

// ── Color label sync ─────────────────────────────────────────────────────────
var colorInputs = [
  ["fill-color", "fill-color-label"],
  ["back-color", "back-color-label"],
  ["gradient1-color", "gradient1-color-label"],
  ["gradient2-color", "gradient2-color-label"],
  ["gradient-back-color", "gradient-back-color-label"],
];

colorInputs.forEach(function (pair) {
  var input = document.getElementById(pair[0]);
  var label = document.getElementById(pair[1]);
  input.addEventListener("input", function () {
    label.textContent = input.value;
  });
});

// ── Type toggle ──────────────────────────────────────────────────────────────
var typeSelect = document.getElementById("qr-type");
var classicColors = document.getElementById("classic-colors");
var gradientColors = document.getElementById("gradient-colors");
var outputSelect = document.getElementById("output-format");

typeSelect.addEventListener("change", function () {
  var isClassic = typeSelect.value === "classic";
  classicColors.style.display = isClassic ? "flex" : "none";
  gradientColors.style.display = isClassic ? "none" : "block";

  var svgOption = outputSelect.querySelector('option[value="svg"]');
  if (!isClassic) {
    svgOption.disabled = true;
    if (outputSelect.value === "svg") outputSelect.value = "png";
  } else {
    svgOption.disabled = false;
  }
});

// ── Helpers ──────────────────────────────────────────────────────────────────
function showError(msg) {
  var banner = document.getElementById("error-banner");
  banner.textContent = msg;
  banner.style.display = "block";
}

function hideError() {
  document.getElementById("error-banner").style.display = "none";
}

function setPreviewState(state) {
  document.getElementById("preview-empty").style.display = state === "empty" ? "flex" : "none";
  document.getElementById("preview-loading").style.display = state === "loading" ? "flex" : "none";
  document.getElementById("preview-result").style.display = state === "result" ? "flex" : "none";
}

// ── Generate ─────────────────────────────────────────────────────────────────
var currentBlobUrl = null;
var currentFileName = "qrcode";

document.getElementById("generate-btn").addEventListener("click", function () {
  hideError();

  var content = qrInput.value.trim();
  if (!content) {
    showError("Please enter text or a URL to encode.");
    return;
  }

  var qrType = typeSelect.value;
  var style = document.getElementById("module-style").value;
  var output = outputSelect.value;
  var sizeInput = document.getElementById("qr-size").value;
  var logoFile = document.getElementById("logo-upload").files[0];

  var params = new URLSearchParams();
  params.set("content", content);
  params.set("style", style);
  params.set("output", output);
  if (sizeInput) params.set("size", sizeInput);

  if (qrType === "classic") {
    params.set("color", document.getElementById("fill-color").value);
    params.set("background", document.getElementById("back-color").value);
  } else {
    params.set("start", document.getElementById("gradient1-color").value);
    params.set("end", document.getElementById("gradient2-color").value);
    params.set("background", document.getElementById("gradient-back-color").value);
    params.set("direction", document.getElementById("gradient-type").value);
  }

  var basePath = "/api/v1/" + qrType;
  var useLogo = logoFile && output === "png";

  setPreviewState("loading");

  if (useLogo) {
    var formData = new FormData();
    formData.append("logo", logoFile);
    fetch(basePath + "?" + params.toString(), { method: "POST", body: formData })
      .then(handleResponse)
      .catch(handleError);
  } else {
    fetch(basePath + "?" + params.toString())
      .then(handleResponse)
      .catch(handleError);
  }

  currentFileName = "qrcode." + output;
});

function handleResponse(resp) {
  if (!resp.ok) {
    resp.json().then(function (data) {
      setPreviewState("empty");
      showError(data.error || "Something went wrong.");
    }).catch(function () {
      setPreviewState("empty");
      showError("Request failed with status " + resp.status);
    });
    return;
  }

  var contentType = resp.headers.get("content-type") || "";

  resp.blob().then(function (blob) {
    if (currentBlobUrl) URL.revokeObjectURL(currentBlobUrl);
    currentBlobUrl = URL.createObjectURL(blob);

    var output = document.getElementById("qr-output");
    output.innerHTML = "";

    if (contentType.includes("svg")) {
      blob.text().then(function (svgText) {
        output.innerHTML = svgText;
        var svg = output.querySelector("svg");
        if (svg) {
          svg.removeAttribute("width");
          svg.removeAttribute("height");
          svg.style.maxWidth = "300px";
          svg.style.width = "100%";
          svg.style.height = "auto";
        }
        setPreviewState("result");
      });
    } else {
      var img = document.createElement("img");
      img.src = currentBlobUrl;
      img.alt = "Generated QR Code";
      img.onload = function () { setPreviewState("result"); };
      output.appendChild(img);
    }
  });
}

function handleError() {
  setPreviewState("empty");
  showError("Network error. Please try again.");
}

// ── Download ─────────────────────────────────────────────────────────────────
document.getElementById("download-btn").addEventListener("click", function () {
  if (!currentBlobUrl) return;
  var a = document.createElement("a");
  a.href = currentBlobUrl;
  a.download = currentFileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
});
