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
    btnLoadCorrelation.addEventListener("click", handleCorrelationPipeline);
  }

  // --- Modeling Button ---
  const form = document.getElementById("model-config-form");
  if (form) {
    form.addEventListener("submit", handleModelPipeline);
  }
}

/**
 * Get Multicollinearity Correlation Matrix
 */
async function handleCorrelationPipeline() {
  const selectedFeatures = getCheckedValues('input[name="features"]');
  if (selectedFeatures.length === 0) return;

  try {
    const correlationData = await fetchCorrelationMatrix(selectedFeatures);
    if (correlationData) {
      renderCorrelationMatrix(correlationData);
    }
  } catch (error) {
    console.error("Correlation dataset engine failure:", error);
  }
}

/**
 * Get the models results
 */
async function handleModelPipeline(event) {
  event.preventDefault(); // Prevent standard form postback

  const form = event.target;
  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());

  // Manually map array data for checkboxes
  payload.features = getCheckedValues('input[name="features"]');
  payload.models = getCheckedValues('input[name="models"]');

  // Change button state to show loading
  const submitBtn = form.querySelector('button[type="submit"]');
  const originalText = submitBtn.textContent;
  submitBtn.textContent = "Running Engine...";
  submitBtn.disabled = true;

  try {
    const results = await runModelingEngine(payload);
    if (results) {
      renderPerformanceMatrix(results.metrics);
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
function renderCorrelationMatrix(data) {
  const container = document.getElementById("correlationMatrixContainer");
  const thead = document.getElementById("correlationHeaderRow");
  const tbody = document.getElementById("correlationTableBody");

  if (!container || !thead || !tbody) return;

  thead.innerHTML = "<th>Feature</th>";
  tbody.innerHTML = "";

  // Assuming 'data' is an object with { features: [], matrix: [[]] }
  data.features.forEach((feat) => {
    thead.innerHTML += `<th>${feat}</th>`;
  });

  data.matrix.forEach((row, i) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td class="fw-bold text-start">${data.features[i]}</td>`;

    row.forEach((value) => {
      // Color coding logic based on correlation value
      let bgColor = "transparent";
      let textColor = "inherit";
      if (value > 0.7) {
        bgColor = "#006400";
        textColor = "white";
      } else if (value < -0.7) {
        bgColor = "#00008b";
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
function renderPerformanceMatrix(metrics) {
  const tbody = document.getElementById("performanceTableBody");
  if (!tbody) return;

  tbody.innerHTML = "";

  // Assuming 'metrics' is an array of objects: { model_name, r2, mape, mae, rmse }
  metrics.forEach((metric, index) => {
    const tr = document.createElement("tr");
    if (index % 2 !== 0) tr.classList.add("table-light");

    tr.innerHTML = `
      <td class="fw-bold text-dark">
        ${metric.model_name}
        <span class="badge bg-light text-dark text-xs p-1">Metrics</span>
      </td>
      <td class="text-end ${metric.r2 > 0 ? "quant-up" : "quant-down"}">${metric.r2.toFixed(4)}</td>
      <td class="text-end">${metric.mape}%</td>
      <td class="text-end">${metric.mae.toFixed(2)}</td>
      <td class="text-end">${metric.rmse.toFixed(2)}</td>
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
