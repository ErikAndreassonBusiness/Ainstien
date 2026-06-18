// app/static/js/run_models.js

/**
 * Main function: Runs the page setup
 */
function initRunModelsPage() {
  // Setup interface toggles
  setupCheckboxToggle(
    "btn-select-all-models",
    'input[name="models"]',
    "Models",
  );
  setupCheckboxToggle(
    "btn-select-all-features",
    'input[name="features"]',
    "Features",
  );

  // --- Multicollinearity Button ---
  const btnLoadCorrelation = document.getElementById("btn-load-correlation");
  if (btnLoadCorrelation) {
    btnLoadCorrelation.addEventListener("click", getCorrelationMatrix);
  }

  // --- Modeling Button ---
  const form = document.getElementById("model-config-form");
  if (form) {
    form.addEventListener("submit", getModelResults);
  }
}

/**
 * Get Multicollinearity Correlation Matrix
 */
async function getCorrelationMatrix() {
  const selectedFeatures = getCheckedValues('input[name="features"]');
  if (selectedFeatures.length === 0) return;

  try {
    const correlationData = await fetchCorrelationMatrix(selectedFeatures);
    if (correlationData) {
      renderCorrelationMatrix(correlationData, selectedFeatures);
    }
  } catch (error) {
    console.error("Correlation dataset engine failure:", error);
  }
}

/**
 * Get the models results
 */
async function getModelResults(event) {
  event.preventDefault(); // Prevent standard form postback

  const form = event.target;

  // --- Collect data via form and present in in JSON format for backend ---
  const formData = new FormData(form);
  const modelSettings = Object.fromEntries(formData.entries());
  modelSettings.features = getCheckedValues('input[name="features"]');
  modelSettings.models = getCheckedValues('input[name="models"]');

  // Change button state to show loading
  const submitBtn = form.querySelector('button[type="submit"]');
  const originalText = submitBtn.textContent;
  submitBtn.textContent = "Running Engine...";
  submitBtn.disabled = true;

  try {
    const results = await runModels(modelSettings);
    if (results) {
      renderPerformanceMatrix(results.performance);
      renderCoefficientsMatrix(results.coefficients);
    }
  } catch (error) {
    console.error("Model engine execution failure:", error);
  } finally {
    submitBtn.textContent = originalText;
    submitBtn.disabled = false;
  }
}

/**
 * Renders the multidimensional correlation grid
 */
function renderCorrelationMatrix(data, selectedFeatures) {
  const container = document.getElementById("correlationMatrixContainer");
  const thead = document.getElementById("correlationHeaderRow");
  const tbody = document.getElementById("correlationTableBody");

  if (!container || !thead || !tbody) return;

  thead.innerHTML = "<th>Feature</th>";
  tbody.innerHTML = "";

  selectedFeatures.forEach((feature) => {
    thead.innerHTML += `<th>${feature}</th>`;
  });

  data.matrix.forEach((row, i) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td class="fw-bold text-start">${selectedFeatures[i]}</td>`;

    row.forEach((value) => {
      // Color coding logic based on correlation value
      let bgColor = "transparent";
      let textColor = "inherit";
      if (value > 0.7) {
        bgColor = "#006400";
        textColor = "white";
      } else if (value < -0.7) {
        bgColor = "var(--ainstien-blue)";
        textColor = "white";
      }

      tr.innerHTML += `<td style="background-color: ${bgColor}; color: ${textColor}">${value.toFixed(2)}</td>`;
    });

    tbody.appendChild(tr);
  });

  container.classList.remove("d-none");
}

/**
 * Renders the primary performance metric tables (R2, MAPE, etc.)
 */
function renderPerformanceMatrix(performanceData) {
  const tbody = document.getElementById("performanceTableBody");
  if (!tbody) return;

  tbody.innerHTML = "";

  performanceData.model_name.forEach(() => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td class="fw-bold text-dark">
        ${model_name}
        <span class="badge bg-light text-dark text-xs p-1">Metrics</span>
      </td>
      <td class="text-end ${performanceData.r2 > 0 ? "quant-up" : "quant-down"}">${performanceData.r2.toFixed(4)}</td>
      <td class="text-end">${performanceData.mape}%</td>
      <td class="text-end">${performanceData.mae.toFixed(2)}</td>
      <td class="text-end">${performanceData.rmse.toFixed(2)}</td>
    `;
    tbody.appendChild(tr);
  });
}

/**
 * Renders the coefficient tabs and internal tables
 */
function renderCoefficientsMatrix(coefficientsData) {
  // Dynamic generation logic for tabs and tables goes here
  // based on your exact JSON response format from the backend.
  console.log("Coefficients rendering initialized", coefficientsData);
}

/**
 * Interface Utility: Collects values of all checked checkboxes matching a selector
 */
function getCheckedValues(selector) {
  return Array.from(document.querySelectorAll(`${selector}:checked`)).map(
    (cb) => cb.value,
  );
}

/**
 * Interface Utility: Attaches select/deselect all mass toggling
 */
function setupCheckboxToggle(btnId, selector, label) {
  const btn = document.getElementById(btnId);
  if (!btn) return;

  btn.addEventListener("click", function () {
    const checkboxes = document.querySelectorAll(selector);
    const allChecked = Array.from(checkboxes).every((cb) => cb.checked);
    checkboxes.forEach((cb) => (cb.checked = !allChecked));
    this.textContent = allChecked
      ? `Select All ${label}`
      : `Deselect All ${label}`;
  });
}

// Bootstrap execution
document.addEventListener("DOMContentLoaded", initRunModelsPage);
