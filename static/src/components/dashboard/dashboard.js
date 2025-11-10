/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { ChartRenderer } from "@web/views/graph/graph_renderer";
import ChartComponent from "../chart/chart";


console.log("✅ Dynamic Dashboard JS Loading");
export class DashboardView extends Component {
    static template = "dynamic_dashboard.DashboardView";
    
    static components = {
        ChartRenderer,
        ChartComponent,
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            dashboards: [],
            selectedDashboard: null,
            charts: [],
            loading: true,
        });

        onWillStart(async () => {
            await this.loadDashboards();
        });
    }

    async loadDashboards() {
        this.state.loading = true;
        try {
            this.state.dashboards = await this.orm.searchRead(
                "dashboard.board",
                [],
                ["id", "name"],
                { order: "name" }
            );
            if (this.state.dashboards.length > 0) {
                this.state.selectedDashboard = this.state.dashboards[0].id;
                await this.selectDashboard(this.state.dashboards[0].id);
            }
        } finally {
            this.state.loading = false;
        }
    }

    async selectDashboard(ev) {
        let dashboardId = parseInt(ev?.target?.value) ?? this.state.dashboards[0]?.id;
        console.log({dashboardId, dashboards: this.state.dashboards[0]})
        if (!dashboardId) {
            dashboardId = this.state.dashboards[0]?.id
        }
        this.state.selectedDashboard = dashboardId;
        this.state.loading = true;
        try {
            this.state.charts = await this.orm.searchRead(
                "dashboard.chart",
                [["dashboard_id", "=", dashboardId]],
                ["id", "name", "chart_type", "color_scheme"],
                { order: "sequence, id" }
            );
        } finally {
            this.state.loading = false;
        }
    }

    openDashboardForm() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "dashboard.board",
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    async editChart(chartId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "dashboard.chart",
            res_id: chartId,
            views: [[false, "form"]],
            target: "new",
        });
    }

    async refreshDashboard() {
        if (this.state.selectedDashboard) {
            await this.selectDashboard(this.state.selectedDashboard);
        }
    }
}

console.log("✅ Dynamic Dashboard JS Loaded");
// registry.category("actions").add("dynamic_dashboard.Component", DashboardView);
// Register also a simpler key to match older compiled assets and XML tags
// Some builds register 'dynamic_dashboard' (without .Component) in the assets.
DashboardView.template = "dynamic_dashboard.DashboardView";
registry.category("actions").add("dynamic_dashboard", DashboardView);