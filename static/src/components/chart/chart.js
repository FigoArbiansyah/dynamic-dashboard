/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

class ChartComponent extends Component {
    static template = "dynamic_dashboard.ChartComponent";
    static props = {
        chartId: Number,
        chartName: String,
        chartType: String,
        colorScheme: String,
        onEdit: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.chartInstance = null;
        this.state = useState({
            loading: true,
            error: null,
        });

        onWillStart(async () => {
            await this.loadChartJs();
        });

        onMounted(async () => {
            // Wait for DOM to be fully ready
            await new Promise(resolve => setTimeout(resolve, 100));
            await this.renderChart();
        });

        onWillUnmount(() => {
            if (this.chartInstance) {
                this.chartInstance.destroy();
            }
        });
    }

    async loadChartJs() {
        // Load Chart.js dari CDN jika belum ada
        if (typeof Chart === 'undefined') {
            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js';
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });
        }
    }

    async renderChart() {
    try {
        this.state.loading = true;
        this.state.error = null;

        // Ambil data dari backend
        const result = await this.orm.call(
            "dashboard.chart",
            "get_chart_data",
            [this.props.chartId]
        );

        if (!result || !result.datasets || result.datasets.length === 0) {
            this.state.error = "No data available";
            this.state.loading = false;
            return;
        }

        // Cari elemen canvas
        let canvasElement = document.getElementById(`canvas-chart-${this.props.chartId}`);

        // Jika belum ada, buat otomatis di dalam card-body komponen ini
        if (!canvasElement) {
            console.warn(`Canvas element not found, creating new one for chartId: ${this.props.chartId}`);

            // Cari elemen card-body dari komponen ini
            const cardBody = document.querySelector(`#card-body-${this.props.chartId}`);
            if (cardBody) {
                canvasElement = document.createElement('canvas');
                canvasElement.id = `canvas-chart-${this.props.chartId}`;
                canvasElement.style.width = "auto";
                canvasElement.style.height = "100px";
                cardBody.appendChild(canvasElement);
            } else {
                console.error("Card body not found, cannot create canvas.");
                this.state.error = "Container not ready";
                this.state.loading = false;
                return;
            }
        }

        // Destroy chart lama jika ada
        if (this.chartInstance) {
            this.chartInstance.destroy();
        }

        const ctx = canvasElement.getContext('2d');
        const colors = this.getColorScheme(this.props.colorScheme);

        const datasets = result.datasets.map(dataset => ({
            ...dataset,
            backgroundColor: colors.background,
            borderColor: colors.border,
            borderWidth: 2,
        }));

        this.chartInstance = new Chart(ctx, {
            type: this.props.chartType,
            data: {
                labels: result.labels,
                datasets: datasets,
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    },
                    title: {
                        display: false,
                    },
                },
                scales: this.props.chartType === 'pie' || this.props.chartType === 'doughnut'
                    ? {}
                    : {
                        y: {
                            beginAtZero: true,
                        },
                    },
            },
        });

        this.state.loading = false;

    } catch (error) {
        console.error("Error rendering chart:", error);
        this.state.error = error.message || "Failed to load chart";
        this.state.loading = false;
    }
}

    getColorScheme(scheme) {
        const schemes = {
            default: {
                background: [
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(255, 159, 64, 0.6)',
                ],
                border: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                ],
            },
            blue: {
                background: 'rgba(54, 162, 235, 0.6)',
                border: 'rgba(54, 162, 235, 1)',
            },
            green: {
                background: 'rgba(75, 192, 192, 0.6)',
                border: 'rgba(75, 192, 192, 1)',
            },
            red: {
                background: 'rgba(255, 99, 132, 0.6)',
                border: 'rgba(255, 99, 132, 1)',
            },
            purple: {
                background: 'rgba(153, 102, 255, 0.6)',
                border: 'rgba(153, 102, 255, 1)',
            },
            orange: {
                background: 'rgba(255, 159, 64, 0.6)',
                border: 'rgba(255, 159, 64, 1)',
            },
        };

        return schemes[scheme] || schemes.default;
    }

    async onRefresh() {
        await this.renderChart();
    }

    async onEdit() {
        this.props.onEdit(this.props.chartId);
        await this.renderChart();
    }
}

ChartComponent.template = "dynamic_dashboard.ChartComponent";
registry.category("components").add("ChartComponent", ChartComponent);
export default ChartComponent;
