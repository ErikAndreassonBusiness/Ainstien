// app/static/js/run_models.js

const FEATURE_LABEL_MAP = {
  // Fundamentals
  revenue: "Revenue",
  depreciation: "Depreciation",
  ebitda: "EBITDA",
  ebit: "EBIT",
  net_income: "Net Income",
  total_assets: "Total Assets",
  total_equity: "Total Equity",
  short_term_debt: "Short Term Debt",
  long_term_debt: "Long Term Debt",
  total_debt: "Total Debt",
  current_assets: "Current Assets",
  fixed_assets: "Fixed Assets",
  cash: "Cash",
  inventory: "Inventory",
  account_receiveables: "Account Receivables",

  // Metrics
  revenue_growth_percent: "Revenue Growth (%)",
  profit_growth_percent: "Profit Growth (%)",
  quick_ratio_percent: "Quick Ratio (%)",
  net_debt_ebitda_ratio: "Net Debt / EBITDA",
  equity_ratio_percent: "Equity Ratio (%)",
  assets_turnover_ratio: "Assets Turnover Ratio",
  inventory_turnover_ratio: "Inventory Turnover Ratio",
  roa: "ROA",
  roe: "ROE",
  roi: "ROI",
  ebit_margin_percent: "EBIT Margin (%)",
  profit_margin_percent: "Profit Margin (%)",

  // Targets
  future_price: "Future Price Target",
  future_growth: "Future Growth Target",
};

// Fallback function
function formatFeatureLabel(featureKey) {
  if (FEATURE_LABEL_MAP[featureKey]) {
    return FEATURE_LABEL_MAP[featureKey];
  }

  return featureKey
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

/**
 * Main function: Runs the page setup
 */
async function initRunModelsPage() {
  try {
    const [featuresData, targetsData] = await Promise.all([
      fetchFeatureNames(),
      fetchTargetNames(),
    ]);

    if (featuresData) {
      renderCheckboxes(
        featuresData.fundamental_features,
        "fundamentals-container",
        "features",
      );
      renderCheckboxes(
        featuresData.metric_features,
        "metrics-container",
        "features",
      );
    }
    if (targetsData && targetsData.targets) {
      renderTargets(targetsData.targets, "targets-container");
    }
  } catch (error) {
    console.error(
      "Initialization failure during runtime layout creation:",
      error,
    );
  }

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
 * Helper function to inject checkboxes into scrolling features viewport panels
 */
function renderCheckboxes(featureArray, containerId, inputName) {
  const container = document.getElementById(containerId);
  if (!container || !featureArray) return;
  container.innerHTML = "";

  featureArray.forEach((feature) => {
    const cleanLabel = formatFeatureLabel(feature);
    const div = document.createElement("div");
    div.className = "form-check mb-2";
    div.innerHTML = `
      <input class="form-check-input" type="checkbox" name="${inputName}" value="${feature}" id="feat_${feature}" checked />
      <label class="form-check-label fw-semibold text-sm" for="feat_${feature}">${cleanLabel}</label>
    `;
    container.appendChild(div);
  });
}

/**
 * Helper function to inject targets radio options
 */
function renderTargets(targetArray, containerId) {
  const container = document.getElementById(containerId);
  if (!container || !targetArray) return;
  container.innerHTML = "";

  targetArray.forEach((target, index) => {
    const cleanLabel = FEATURE_LABEL_MAP[target.value] || target.label_fallback;
    const isChecked = index === 0 ? "checked" : "";

    const div = document.createElement("div");
    div.className = "form-check mb-2";
    div.innerHTML = `
      <input type="radio" class="form-check-input" name="target_variable" id="target_${target.value}" value="${target.value}" ${isChecked} />
      <label class="form-check-label fw-semibold text-sm" for="target_${target.value}">${cleanLabel}</label>
    `;
    container.appendChild(div);
  });
}

/**
 * Get Multicollinearity Correlation Matrix
 */
async function getCorrelationMatrix() {
  const fundamentalFeatures = Array.from(
    document.querySelectorAll(
      '#fundamentals-container input[type="checkbox"]:checked',
    ),
  ).map((cb) => cb.value);

  const metricFeatures = Array.from(
    document.querySelectorAll(
      '#metrics-container input[type="checkbox"]:checked',
    ),
  ).map((cb) => cb.value);

  // Combine
  const selectedFeatures = [...fundamentalFeatures, ...metricFeatures];
  if (selectedFeatures.length === 0) return;

  const data = {
    fundamental_features: fundamentalFeatures,
    metric_features: metricFeatures,
  };

  try {
    const correlationData = await fetchCorrelationMatrix(data);
    if (correlationData) {
      renderCorrelationMatrix(correlationData, selectedFeatures);
    }
  } catch (error) {
    console.error("Correlation dataset engine failure:", error);
  }
}

/**
 * Get the models results with robust feature type separation
 */
async function getModelResults(event) {
  event.preventDefault();

  const form = event.target;
  const formData = new FormData(form);
  const modelSettings = Object.fromEntries(formData.entries());

  const allCheckedElements = Array.from(
    document.querySelectorAll('input[name="features"]:checked'),
  );

  const masterFeatures = await fetchFeatureNames();

  if (masterFeatures) {
    const fundamentalSet = new Set(masterFeatures.fundamental_features);
    const metricSet = new Set(masterFeatures.metric_features);

    // 3. Map values precisely by validating their existence in the master lists
    modelSettings.fundamental_features = allCheckedElements
      .map((cb) => cb.value)
      .filter((val) => fundamentalSet.has(val));

    modelSettings.metric_features = allCheckedElements
      .map((cb) => cb.value)
      .filter((val) => metricSet.has(val));
  } else {
    // Fallback if the network request fails: default to an empty array setup
    modelSettings.fundamental_features = [];
    modelSettings.metric_features = [];
  }

  // 4. Set the combined features list that scikit-learn expects
  modelSettings.features = allCheckedElements.map((cb) => cb.value);
  modelSettings.models = getCheckedValues('input[name="models"]');

  // Guard Clause: Prevent submission if nothing is checked to stop sklearn crashes
  if (modelSettings.features.length === 0) {
    alert(
      "Please select at least one feature before running the modeling engine.",
    );
    return;
  }

  const submitBtn = form.querySelector('button[type="submit"]');
  const originalText = submitBtn.textContent;
  submitBtn.textContent = "Running Engine...";
  submitBtn.disabled = true;

  try {
    console.log("Payload sent to backend:", modelSettings);
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
    // Translate technical name into title string
    thead.innerHTML += `<th>${formatFeatureLabel(feature)}</th>`;
  });

  data.matrix.forEach((row, i) => {
    const tr = document.createElement("tr");
    // Translate row title technical name into clean text
    tr.innerHTML = `<td class="fw-bold text-start">${formatFeatureLabel(selectedFeatures[i])}</td>`;

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

  console.log("Performance rendering initialized", performanceData);

  performanceData.forEach((model) => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td class="fw-bold text-dark">
        ${model.model_name}
      </td>
      <td class="text-end ${model.r2 > 0 ? "quant-up" : "quant-down"}">${model.r2.toFixed(4)}</td>
      <td class="text-end">${model.mape}%</td>
      <td class="text-end">${model.mae.toFixed(2)}</td>
      <td class="text-end">${model.rmse.toFixed(2)}</td>
    `;
    tbody.appendChild(tr);
  });
}

/**
 * Helper: Maps selected feature values to their corresponding UI text labels
 */
function getFeatureLabels(selector) {
  return Array.from(document.querySelectorAll(`${selector}:checked`)).map(
    (cb) => {
      const label = document.querySelector(`label[for="${cb.id}"]`);
      return {
        value: cb.value,
        label: label ? label.textContent.trim() : cb.value,
      };
    },
  );
}

/**
 * Renders the coefficient tabs and internal tables
 */
function renderCoefficientsMatrix(coefficientsData) {
  const tabsList = document.getElementById("coefficientTabs");
  const tabContent = document.getElementById("coefficientTabsContent");

  if (!tabsList || !tabContent) return;

  // Clear previous states cleanly
  tabsList.innerHTML = "";
  tabContent.innerHTML = "";

  // Pull both the technical names and clean UI text labels using our helper
  const featureMeta = getFeatureLabels('input[name="features"]');

  Object.entries(coefficientsData).forEach(
    ([modelName, coefficients], index) => {
      const safeId = `tab-${modelName.replace(/[^a-zA-Z0-9]/g, "-").toLowerCase()}`;
      const isActive = index === 0;

      // 1. Render and append Navigation Tab
      const navItem = document.createElement("li");
      navItem.className = "nav-item";
      navItem.role = "presentation";
      navItem.innerHTML = `
      <button 
        class="nav-link fw-semibold text-xs text-uppercase ${isActive ? "active" : ""}" 
        id="${safeId}-nav" 
        data-bs-toggle="tab" 
        data-bs-target="#${safeId}-pane" 
        type="button" 
        role="tab" 
        aria-controls="${safeId}-pane" 
        aria-selected="${isActive}">
        ${modelName}
      </button>
    `;
      tabsList.appendChild(navItem);

      // 2. Normalize 2D output vectors from sklearn shapes (e.g. [[c1, c2]] vs [c1, c2])
      const flatCoeffs = Array.isArray(coefficients[0])
        ? coefficients[0]
        : coefficients;

      // 3. Render Content Pane Container
      const pane = document.createElement("div");
      pane.className = `tab-pane fade ${isActive ? "show active" : ""}`;
      pane.id = `${safeId}-pane`;
      pane.role = "tabpanel";
      pane.setAttribute("aria-labelledby", `${safeId}-nav`);

      // 4. Map coefficients directly into HTML table rows array
      const rowsHTML = flatCoeffs
        .map((coef, i) => {
          const featureName = featureMeta[i]
            ? featureMeta[i].label
            : `Feature Ref [${i + 1}]`;

          // Dynamic scaling for small floating-point quant signals
          const formattedCoef =
            Math.abs(coef) < 0.0001 && coef !== 0
              ? coef.toExponential(4)
              : coef.toFixed(5);

          // Quant signal styling matched to your design tokens
          let colorClass = "text-muted";
          if (coef > 0) colorClass = "quant-up fw-semibold"; // Reused your project token
          if (coef < 0) colorClass = "quant-down fw-semibold"; // Reused your project token

          return `
        <tr>
          <td class="text-dark fw-medium">${featureName}</td>
          <td class="text-end font-monospace ${colorClass}">${formattedCoef}</td>
        </tr>
      `;
        })
        .join("");

      // 5. Construct final markup structure and mount to DOM
      pane.innerHTML = `
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0 text-sm">
          <thead class="table-light">
            <tr>
              <th scope="col" style="width: 60%">Feature Attribute</th>
              <th scope="col" class="text-end" style="width: 40%">Coefficient Weight</th>
            </tr>
          </thead>
          <tbody class="financial-data">
            ${rowsHTML}
          </tbody>
        </table>
      </div>
    `;

      tabContent.appendChild(pane);
    },
  );
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
