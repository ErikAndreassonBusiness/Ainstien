// app/static/js/run_models.js

const FEATURE_LABEL_MAP = {
  // Fundamentals
  revenue: "Revenue",
  depreciation: "Depreciation",
  EBITDA: "EBITDA",
  EBIT: "EBIT",
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
  account_receiveables: "Account Receivables", //fix misspelling when back-end misspelling is fixed

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
 * Main function: Runs the page setup cleanly
 */
async function initRunModelsPage() {
  try {
    const featuresNames = await fetchFeatureNames();
    const targetsNames = await fetchTargetNames();

    // --- Render Features and Targets
    if (featuresNames) {
      renderCheckboxes(
        featuresNames.fundamental_features,
        "fundamentals-container",
        "features",
      );
      renderCheckboxes(
        featuresNames.metric_features,
        "metrics-container",
        "features",
      );
    }

    if (targetsNames && targetsNames.targets) {
      renderTargets(targetsNames.targets, "targets-container");
    }

    // --- Render Select ALL Buttons ---
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
  } catch (error) {
    console.error(
      "Initialization failure during runtime layout creation:",
      error,
    );
  }

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
 * Interface Utility: High-performance select/deselect all mass toggling
 */
function setupCheckboxToggle(btnId, selector, label) {
  const btn = document.getElementById(btnId);
  if (!btn) return;

  let stateToggle = true;

  btn.addEventListener("click", function () {
    const checkboxes = document.querySelectorAll(selector);
    if (checkboxes.length === 0) return;

    checkboxes.forEach((cb) => {
      cb.checked = stateToggle;
    });

    this.textContent = stateToggle
      ? `Deselect All ${label}`
      : `Select All ${label}`;
    stateToggle = !stateToggle;
  });
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
  const allCheckedElements = Array.from(
    document.querySelectorAll('input[name="features"]:checked'),
  ).map((cb) => cb.value);

  if (allCheckedElements.length === 0) {
    alert(
      "Please select at least one feature to compute the correlation matrix.",
    );
    return;
  }

  const btn = document.getElementById("btn-load-correlation");
  if (btn) {
    btn.disabled = true;
    btn.textContent = "Computing Matrix...";
  }
  // Check how the names features are gathared
  try {
    const masterFeatures = await fetchFeatureNames();
    let fundamentalFeatures = [];
    let metricFeatures = [];

    if (masterFeatures) {
      const fundamentalSet = new Set(masterFeatures.fundamental_features);
      const metricSet = new Set(masterFeatures.metric_features);

      fundamentalFeatures = allCheckedElements.filter((val) =>
        fundamentalSet.has(val),
      );
      metricFeatures = allCheckedElements.filter((val) => metricSet.has(val));
    } else {
      fundamentalFeatures = allCheckedElements;
    }

    const features = {
      fundamental_features: fundamentalFeatures,
      metric_features: metricFeatures,
    };

    const correlationData = await fetchCorrelationMatrix(features);

    if (correlationData && correlationData.matrix) {
      renderCorrelationMatrix(correlationData, allCheckedElements);
    } else {
      console.warn("Backend returned an empty correlation payload.");
    }
  } catch (error) {
    console.error("Correlation dataset engine failure:", error);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "Compute Correlation Matrix";
    }
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
    thead.innerHTML += `<th>${formatFeatureLabel(feature)}</th>`;
  });

  data.matrix.forEach((row, i) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td class="fw-bold text-start text-xs">${formatFeatureLabel(selectedFeatures[i])}</td>`;

    row.forEach((value) => {
      let bgColor = "transparent";
      let textColor = "inherit";
      if (value > 0.6) {
        bgColor = "rgba(0, 100, 0, 0.15)"; // Soft positive green tint matching legendary custom CSS style
        textColor = "#006400";
      } else if (value < -0.6) {
        bgColor = "rgba(0, 86, 179, 0.15)"; // Soft inverse blue tint
        textColor = "var(--ainstien-blue)";
      }

      tr.innerHTML += `<td class="font-monospace text-xs" style="background-color: ${bgColor}; color: ${textColor}">${value.toFixed(2)}</td>`;
    });

    tbody.appendChild(tr);
  });

  container.classList.remove("d-none");
}

/**
 * Model engine compilation execution orchestrator
 */
async function getModelResults(e) {
  e.preventDefault();

  const selectedFeatures = getCheckedValues('input[name="features"]');
  const selectedModels = getCheckedValues('input[name="models"]');

  if (selectedFeatures.length === 0 || selectedModels.length === 0) {
    alert(
      "Please select at least one tracking feature and one mathematical model algorithm.",
    );
    return;
  }

  const submitBtn = e.target.querySelector('button[type="submit"]');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = "Processing Regression Tasks...";
  }

  const payload = {
    features: selectedFeatures,
    models: selectedModels,
    target_variable:
      e.target.querySelector('input[name="target_variable"]:checked')?.value ||
      "future_price",
    log_transform: e.target.querySelector('input[name="log_transform"]')
      ?.checked
      ? "on"
      : "off",
    cv_folds: e.target.querySelector('input[name="cv_folds"]')?.value || "5",
    positive_coefficients: e.target.querySelector(
      'input[name="positive_coefficients"]',
    )?.checked
      ? "on"
      : "off",
    test_split:
      e.target.querySelector('input[name="test_split"]')?.value || "0.8",
  };

  try {
    const response = await runModels(payload);
    if (response && response.performance && response.coefficients) {
      renderPerformanceMatrix(response.performance);
      renderCoefficientsMatrix(response.coefficients);
    } else {
      alert(
        "The machine learning calculation engine returned an unreadable layout mapping.",
      );
    }
  } catch (error) {
    console.error("Model performance execution failure:", error);
    alert("An error occurred during machine learning model processing.");
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = "Run Analysis Engine";
    }
  }
}

/**
 * Renders the primary performance metric tables (R2, MAPE, etc.)
 */
function renderPerformanceMatrix(performanceData) {
  const tbody = document.getElementById("performanceTableBody");
  if (!tbody) return;

  tbody.innerHTML = "";

  performanceData.forEach((model) => {
    const tr = document.createElement("tr");
    tr.className = "stock-row text-sm";

    tr.innerHTML = `
      <td class="fw-bold text-dark text-uppercase">
        ${model.model_name}
      </td>
      <td class="text-end font-monospace ${model.r2 > 0 ? "quant-up text-success" : "quant-down text-danger"}">${model.r2.toFixed(2)}</td>
      <td class="text-end font-monospace">${(model.mape * 100).toFixed(1)}%</td>
      <td class="text-end font-monospace">${model.mae.toFixed(2)}</td>
      <td class="text-end font-monospace">${model.rmse.toFixed(2)}</td>
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

  tabsList.innerHTML = "";
  tabContent.innerHTML = "";

  const selectedFeatures = getFeatureLabels('input[name="features"]');

  Object.entries(coefficientsData).forEach(
    ([modelName, coefficients], index) => {
      const safeId = `tab-${modelName.replace(/[^a-zA-Z0-9]/g, "-").toLowerCase()}`;
      const isActive = index === 0;

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

      const flatCoeffs = Array.isArray(coefficients[0])
        ? coefficients[0]
        : coefficients;

      const pane = document.createElement("div");
      pane.className = `tab-pane fade ${isActive ? "show active" : ""}`;
      pane.id = `${safeId}-pane`;
      pane.role = "tabpanel";
      pane.setAttribute("aria-labelledby", `${safeId}-nav`);

      const rowsHTML = flatCoeffs
        .map((coef, i) => {
          const featureName = selectedFeatures[i]
            ? selectedFeatures[i].label
            : `Feature Ref [${i + 1}]`;
          const formattedCoef =
            Math.abs(coef) < 0.0001 && coef !== 0
              ? coef.toExponential(4)
              : coef.toFixed(5);

          let colorClass = "text-muted";
          if (coef > 0) colorClass = "quant-up text-success fw-semibold";
          if (coef < 0) colorClass = "quant-down text-danger fw-semibold";

          return `
        <tr>
          <td class="text-dark fw-medium text-sm">${featureName}</td>
          <td class="text-end font-monospace text-sm ${colorClass}">${coef > 0 ? "+" : ""}${formattedCoef}</td>
        </tr>
      `;
        })
        .join("");

      pane.innerHTML = `
      <div class="table-responsive border rounded mt-3 bg-white">
        <table class="table table-hover align-middle mb-0 text-sm">
          <thead class="table-light">
            <tr>
              <th scope="col" class="text-xs text-uppercase tracking-wider py-2" style="width: 60%">Feature Attribute</th>
              <th scope="col" class="text-end text-xs text-uppercase tracking-wider py-2" style="width: 40%">Coefficient Weight</th>
            </tr>
          </thead>
          <tbody class="financial-data">
            ${rowsHTML || '<tr><td colspan="2" class="text-center text-muted">No variable factors reported.</td></tr>'}
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

// Bootstrap execution
document.addEventListener("DOMContentLoaded", initRunModelsPage);
