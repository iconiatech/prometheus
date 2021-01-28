// Chart Options
const options = {
    chart: {
        width: "100%",
        height: 255,
        type: "bar",
        stacked: true,
    },
    dataLabels: {
        enabled: false
    },
    series: [
        {
            name: "Actual",
            data: [800, 300, 700, 640, 1000, 700]
        },
        {
            name: "Projection",
            data: [1000, 400, 600, 540, 800, 900]
        }
    ],
    xaxis: {
        categories: ["Jan", "Feb", "Mar", "Apr", "May", "June"]
    },
    plotOptions: {
        bar: {
          columnWidth: "10%"
        }
    },
    legend: {
        show: false
    },
}

// Init Chart
const chart = new ApexCharts(document.querySelector("#projections-v-actual"),options)

// Render Chart
chart.render();

// Chart Options
const optionsOne = {
    chart: {
        width: "100%",
        height: 255,
        stacked: false,
    },
    dataLabels: {
        enabled: false
    },
    series: [
        {
            name: "Current",
            type: "line",
            data: [100000, 200000, 150000, 250000]
        },
        {
            name: "Previous",
            type: "line",
            data: [10000, 150000, 100000, 300000]
        }
    ],
    xaxis: {
        categories: ["Week One", "Week Two", "Week Three", "Week Four"]
    },
    plotOptions: {
        bar: {
          columnWidth: "10%"
        }
    },
    legend: {
        show: false
    },
    stroke: {
        curve: 'smooth',
    },
}

// Init Chart
const chartOne = new ApexCharts(document.querySelector("#projections-chart"),optionsOne)

// Render Chart
chartOne.render();
