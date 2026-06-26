document.addEventListener("DOMContentLoaded", () => {
  renderActiveTrades();
  renderPossibleTrades();
  renderPortfolioChart();
  renderSixSigmaHistogram();
});

function renderActiveTrades() {
  const tableBody = document.getElementById("activeTradesTable");
  const mockActiveTrades = [
    { ticker: "VOLV-B.ST", entry: 215.5, current: 228.1, pl: 5.8 },
    { ticker: "ERIC-B.ST", entry: 54.2, current: 51.1, pl: -5.7 },
    { ticker: "HM-B.ST", entry: 145.0, current: 152.3, pl: 5.0 },
    { ticker: "INVE-B.ST", entry: 250.0, current: 255.0, pl: 2.0 },
    { ticker: "SAND.ST", entry: 190.0, current: 188.5, pl: -0.8 },
  ];

  tableBody.innerHTML = mockActiveTrades
    .map((trade) => {
      const plClass = trade.pl >= 0 ? "quant-up" : "quant-down";
      const plPrefix = trade.pl >= 0 ? "+" : "";
      return `
            <tr>
                <td class="financial-data fw-bold">${trade.ticker}</td>
                <td class="financial-data">${trade.entry.toFixed(2)}</td>
                <td class="financial-data">${trade.current.toFixed(2)}</td>
                <td class="financial-data text-end ${plClass}">${plPrefix}${trade.pl.toFixed(2)}%</td>
            </tr>
        `;
    })
    .join("");
}

function renderPossibleTrades() {
  const tableBody = document.getElementById("possibleTradesTable");
  const mockPossibleTrades = [
    { ticker: "EVO.ST", signal: "SELL", conviction: 74 },
    { ticker: "ATCO-A.ST", signal: "BUY", conviction: 65 },
    { ticker: "SEB-A.ST", signal: "BUY", conviction: 92 },
    { ticker: "ASSA-B.ST", signal: "SELL", conviction: 58 },
  ];

  tableBody.innerHTML = mockPossibleTrades
    .map((trade) => {
      const signalClass = trade.signal === "BUY" ? "quant-up" : "quant-down";
      return `
            <tr>
                <td class="financial-data fw-bold">${trade.ticker}</td>
                <td class="financial-data ${signalClass}">${trade.signal}</td>
                <td class="text-end">
                    <div class="progress" style="height: 15px;">
                        <div class="progress-bar" role="progressbar" style="width: ${trade.conviction}%; background-color: var(--ainstien-blue);">
                            ${trade.conviction}%
                        </div>
                    </div>
                </td>
            </tr>
        `;
    })
    .join("");
}

function renderPortfolioChart() {
  const ctx = document.getElementById("portfolioChart").getContext("2d");
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Industrials", "Tech", "Consumer", "Cash"],
      datasets: [
        {
          data: [45, 20, 15, 20],
          backgroundColor: ["#0056b3", "#1a1d20", "#6c757d", "#28a745"],
          borderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false, // CRITICAL: stops infinite expansion
      plugins: {
        legend: { position: "right" },
      },
    },
  });
}

function renderSixSigmaHistogram() {
  const ctx = document.getElementById("marketCapHistogram").getContext("2d");
  const labels = [
    "0-10",
    "10-20",
    "20-30",
    "30-40",
    "40-50",
    "50-60",
    "60-70",
    "70-80",
    "80+",
  ];
  const distributionData = [5, 12, 25, 30, 18, 8, 3, 1, 1];

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Companies",
          data: distributionData,
          backgroundColor: "rgba(0, 86, 179, 0.6)",
          borderColor: "#0056b3",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false, // CRITICAL: stops infinite expansion
      scales: {
        y: { beginAtZero: true },
        x: {},
      },
      plugins: {
        legend: { display: false },
      },
    },
    plugins: [
      {
        id: "sixSigmaLines",
        afterDraw: (chart) => {
          const {
            ctx,
            chartArea: { top, bottom },
            scales: { x },
          } = chart;

          const drawLine = (xPos, color, text) => {
            ctx.save();
            ctx.beginPath();
            ctx.moveTo(xPos, top);
            ctx.lineTo(xPos, bottom);
            ctx.lineWidth = 2;
            ctx.strokeStyle = color;
            ctx.setLineDash([5, 5]);
            ctx.stroke();
            ctx.fillStyle = color;
            ctx.font = "10px Arial";
            ctx.fillText(text, xPos + 5, top + 15);
            ctx.restore();
          };

          const meanX = x.getPixelForValue(3.5);
          const plus3SigmaX = x.getPixelForValue(7.5);

          drawLine(meanX, "#1a1d20", "Mean (μ)");
          drawLine(plus3SigmaX, "#dc3545", "+3σ");
        },
      },
    ],
  });
}
