/** @odoo-module **/

import { Component, useEffect, useRef } from "@odoo/owl";

// Chart color palette
const CHART_COLORS = [
    "#4F46E5", "#7C3AED", "#DB2777", "#DC2626",
    "#D97706", "#059669", "#0891B2", "#0284C7",
    "#6366F1", "#8B5CF6", "#EC4899", "#EF4444",
];

export class ChartWidget extends Component {
    static template = "dynamic_dashboard.ChartWidget";
    static props = { comp: Object };

    setup() {
        this.canvasRef = useRef("canvas");
        this._chart = null;

        useEffect(
            () => {
                this._renderChart();
                return () => this._destroyChart();
            },
            () => [this.props.comp]
        );
    }

    _destroyChart() {
        if (this._chart) {
            this._chart.destroy();
            this._chart = null;
        }
    }

    _loadChartJs(callback) {
        if (typeof Chart !== "undefined") {
            callback();
            return;
        }
        const script = document.createElement("script");
        script.src = "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js";
        script.onload = callback;
        document.head.appendChild(script);
    }

    _renderChart() {
        this._loadChartJs(() => {
            const canvas = this.canvasRef.el;
            if (!canvas) return;

            const comp = this.props.comp;
            const isPie = ["pie", "doughnut", "polarArea"].includes(comp.chart_type);

            const dataset = {
                label: comp.chart_label || comp.name,
                data: comp.values || [],
                backgroundColor: isPie
                    ? (comp.values || []).map((_, i) => CHART_COLORS[i % CHART_COLORS.length])
                    : (comp.color || "#4F46E5") + "cc",
                borderColor: isPie
                    ? (comp.values || []).map((_, i) => CHART_COLORS[i % CHART_COLORS.length])
                    : comp.color || "#4F46E5",
                borderWidth: isPie ? 2 : 2,
                borderRadius: comp.chart_type === "bar" ? 4 : 0,
                fill: comp.chart_type === "line",
            };

            this._chart = new Chart(canvas, {
                type: comp.chart_type || "bar",
                data: {
                    labels: comp.labels || [],
                    datasets: [dataset],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: comp.chart_legend !== false,
                            position: "bottom",
                        },
                        title: {
                            display: false,
                        },
                    },
                    scales: isPie ? {} : {
                        x: {
                            grid: { display: false },
                            ticks: { font: { size: 11 } },
                        },
                        y: {
                            beginAtZero: true,
                            grid: { color: "rgba(0,0,0,0.05)" },
                            ticks: { font: { size: 11 } },
                        },
                    },
                },
            });
        });
    }
}
