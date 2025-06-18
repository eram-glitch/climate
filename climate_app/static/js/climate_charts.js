console.log("🔥 climate_charts.js loaded");

let co2Data = {}, mapLayer, map, lineChart, sliderRange;

const colorBins = [
  { limit: 1e10, color: "#4b0000", label: ">10B" },
  { limit: 3e9,  color: "#67000d", label: "3B–10B" },
  { limit: 1e9,  color: "#a50f15", label: "1B–3B" },
  { limit: 3e8,  color: "#cb181d", label: "300M–1B" },
  { limit: 1e8,  color: "#ef3b2c", label: "100M–300M" },
  { limit: 3e7,  color: "#fb6a4a", label: "30M–100M" },
  { limit: 1e7,  color: "#fcae91", label: "10M–30M" },
  { limit: 3e6,  color: "#fdd0c8", label: "3M–10M" },
  { limit: 1,    color: "#fbb4ae", label: "<3M" }
];


// 🔢 Format CO₂ values
function formatCO2(val) {
  if (val >= 1e9) return `${(val / 1e9).toLocaleString(undefined, { minimumFractionDigits: 2 })} billion`;
  if (val >= 1e6) return `${(val / 1e6).toLocaleString(undefined, { minimumFractionDigits: 2 })} million`;
  if (val >= 1e3) return `${(val / 1e3).toLocaleString(undefined, { minimumFractionDigits: 2 })} thousand`;
  return val.toLocaleString(undefined, { minimumFractionDigits: 2 });
}

// 🎨 OWID Color Scale
function getColor(val) {
  for (let bin of colorBins) {
    if (val > bin.limit) return bin.color;
  }
  return "#eee";
}

// 🧭 Choropleth Initialization
function initMap(geoJson, yearRange) {
map = L.map("co2-map", {
  zoomControl: false,
  scrollWheelZoom: false,
  doubleClickZoom: false,
  dragging: false,
  boxZoom: false,
  keyboard: false,
  minZoom: 2,
  maxZoom: 2,
  worldCopyJump: false,
  noWrap: true, // ✅ Prevent tile repetition
  maxBounds: [[-60, -180], [85, 180]], // ✅ Lock bounds
  maxBoundsViscosity: 1.0,
  crs: L.CRS.EPSG3857
}).setView([20, 0], 2);

  map.options.maxBounds = map.getBounds();

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  noWrap: true,
  bounds: [[-60, -180], [85, 180]]
}).addTo(map);

  mapLayer = L.geoJson(geoJson, {
    style: () => ({ fillColor: "#eee", color: "#555", weight: 1, fillOpacity: 0.7 }),
    onEachFeature: (f, l) => l.bindTooltip("", { sticky: true })
  }).addTo(map);

const slider = document.getElementById("co2-year");
const tooltip = document.getElementById("co2-year-tooltip");
const minLabel = document.getElementById("co2-year-min");
const maxLabel = document.getElementById("co2-year-max");

slider.min = yearRange.min_year;
slider.max = yearRange.max_year;
slider.value = yearRange.max_year;

minLabel.textContent = slider.min;
maxLabel.textContent = slider.max;

const defaultVal = slider.value;
const percent = (defaultVal - slider.min) / (slider.max - slider.min);
slider.style.background = `linear-gradient(to right, #f44343 ${percent * 100}%, #e5e7eb ${percent * 100}%)`;
tooltip.textContent = defaultVal;
tooltip.style.left = `calc(${percent * 100}% - 12px)`;
updateMap(defaultVal); // ✅ Show map with latest year data


function updateYearSliderTooltip() {
  const val = slider.value;
  const percent = (val - slider.min) / (slider.max - slider.min);
  tooltip.textContent = val;
  tooltip.style.left = `calc(${percent * 100}% - 12px)`;
  updateMap(val);
}

slider.addEventListener("input", () => {
  const val = (slider.value - slider.min) / (slider.max - slider.min);
  slider.style.background = `linear-gradient(to right, #f44343 ${val * 100}%, #e5e7eb ${val * 100}%)`;
  tooltip.textContent = slider.value;
  tooltip.style.left = `calc(${val * 100}% - 12px)`;
  updateMap(slider.value);
});

  renderLegend();
}

// 🎯 Update Choropleth
function updateMap(year) {
  const data = co2Data[year] || {};
  const missing = [];

  mapLayer.eachLayer(layer => {
    const props = layer.feature.properties;
    const names = [
      props.name_long,
      props.formal_en,
      props.name,
      props.brk_name,
      props.name_sort,
      props.geounit,
      props.admin,
      props.sovereignt
    ];

    let val = null;
    for (let n of names) {
      if (n && data[n] != null) {
        val = data[n];
        break;
      }
    }

    if (val == null) {
      missing.push(props.name);
    }

    const fillColor = val != null ? getColor(val) : "url(#diagonalHatch)";
    layer.setStyle({
      fillColor,
      color: "#555",
      weight: 1,
      fillOpacity: 0.7
    });

    const display = val != null ? `${formatCO2(val)} tonnes CO₂` : "No data";
    layer.getTooltip().setContent(`${props.name}: ${display}`);
  });

  if (missing.length > 0) {
    console.warn(`🚫 Missing CO₂ data → ${year}:`, missing.sort());
  }
}

// 🧾 Render Legend
function renderLegend() {
  const legend = document.getElementById("map-legend");
  legend.innerHTML = colorBins.map(b =>
    `<div class="legend-item"><span class="legend-color" style="background:${b.color};"></span>${b.label}</div>`
  ).join("") + `<div class="legend-item"><span class="legend-color" style="background:url(#diagonalHatch);"></span>No data</div>`;
}

// 🌡 Temperature Bar Chart
function initTemperature(csv) {
  const rows = csv.trim().split("\n").slice(1);
  const labels = [], data = [], colors = [];

  for (let row of rows) {
    const [year, value] = row.split(",");
    const v = parseFloat(value);
    labels.push(year);
    data.push(v);
    const r = Math.min(255, Math.round(255 * (v + 0.5)));
    const b = Math.max(0, 255 - r);
    colors.push(`rgb(${r},0,${b})`);
  }

  new Chart(document.getElementById("temperatureBarChart"), {
    type: "bar",
    data: { labels, datasets: [{ data, backgroundColor: colors }] },
    options: { plugins: { legend: { display: false } } }
  });
}

// 📈 CO₂ Line Chart
function initLineChart(yearRange) {


  sliderRange = document.getElementById("slider-range");
  noUiSlider.create(sliderRange, {
    start: [yearRange.min_year, yearRange.max_year],
    connect: true,
    step: 1,
    range: { min: yearRange.min_year, max: yearRange.max_year },
    tooltips: [true, true],
    format: { to: v => Math.round(v), from: v => Number(v) }
  });

  sliderRange.noUiSlider.on("update", updateLineChart);
  updateLineChart();
}

// 🔁 Update CO₂ Line Chart
function updateLineChart() {
  const [start, end] = sliderRange.noUiSlider.get().map(Number);
  document.getElementById("range-label").textContent = `${start} – ${end}`;

  const years = Object.keys(co2Data).map(Number).filter(y => y >= start && y <= end).sort();
  const countries = ["World", "China", "United States", "India"];
  const datasets = countries.map(c => ({
    label: c,
    data: years.map(y => co2Data[y]?.[c] ?? 0),
    fill: false,
    borderWidth: 2,
    pointRadius: 2,
    tension: 0.1
  }));

  if (lineChart) lineChart.destroy();
  lineChart = new Chart(document.getElementById("co2-line-chart"), {
    type: "line",
    data: { labels: years, datasets },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          callbacks: {
            label: context => {
              const val = context.raw;
              return `${context.dataset.label}: ${formatCO2(val)} tonnes`;
            }
          }
        }
      },
      scales: { y: { beginAtZero: true } }
    }
  });
}

// ⚠ Disaster Bar Chart
function initDisasters(csv) {
  const lines = csv.trim().split("\n");
  const headers = lines[0].split(",").map(h => h.trim());
  const rows = lines.slice(1).map(r => r.split(","));
  const years = rows.map(r => r[0]);
  const droughts = rows.map(r => +r[headers.indexOf("Drought")]);
  const floods = rows.map(r => +r[headers.indexOf("Flood")]);
  const wildfires = rows.map(r => +r[headers.indexOf("Wildfire")]);

  new Chart(document.getElementById("disasterChart"), {
    type: "bar",
    data: {
      labels: years,
      datasets: [
        { label: "Floods", data: floods, backgroundColor: "#3498db" },
        { label: "Wildfires", data: wildfires, backgroundColor: "#f39c12" },
        { label: "Droughts", data: droughts, backgroundColor: "#e74c3c" }
      ]
    },
    options: {
      responsive: true,
      scales: { x: { stacked: true }, y: { stacked: true } }
    }
  });
}

// 🚀 Load All
Promise.all([
  fetch("/static/data/formatted_temperature.csv").then(r => r.text()),
  fetch("/static/data/co2_by_year.json").then(r => r.json()),
  fetch("/static/data/countries.geojson").then(r => r.json()),
  fetch("/static/data/co2_year_range.json").then(r => r.json()),
  fetch("/static/data/formatted_disasters.csv").then(r => r.text())
]).then(([tempCsv, co2Json, geoJson, yearRange, disastersCsv]) => {
  co2Data = co2Json;
  initTemperature(tempCsv);
  initMap(geoJson, yearRange);
  initLineChart(yearRange);
  initDisasters(disastersCsv);
});

const mapBtn = document.getElementById("mapViewBtn");
const chartBtn = document.getElementById("chartViewBtn");
const mapSection = document.getElementById("co2-map-section");
const chartSection = document.getElementById("co2-line-section");

mapBtn.addEventListener("click", () => {
  mapSection.style.display = "block";
  chartSection.style.display = "none";
  mapBtn.classList.add("bg-white", "text-black", "shadow");
  mapBtn.classList.remove("text-gray-700");
  chartBtn.classList.remove("bg-white", "text-black", "shadow");
  chartBtn.classList.add("text-gray-700");
});

chartBtn.addEventListener("click", () => {
  mapSection.style.display = "none";
  chartSection.style.display = "block";
  chartBtn.classList.add("bg-white", "text-black", "shadow");
  chartBtn.classList.remove("text-gray-700");
  mapBtn.classList.remove("bg-white", "text-black", "shadow");
  mapBtn.classList.add("text-gray-700");

  updateLineChart(); // 💡 Make sure chart updates when switching to it
});

