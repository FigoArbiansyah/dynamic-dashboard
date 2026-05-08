/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { CardMetric } from "../card_metric/card_metric";
import { ChartWidget } from "../chart_widget/chart_widget";
import { registry } from "@web/core/registry";

export class DynamicDashboard extends Component {
    static template = "dynamic_dashboard.DashboardView";
    static components = { CardMetric, ChartWidget };

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.action = useService("action");

        this.gridRef = useRef("grid");

        this.state = useState({
            boardData: null,
            loading: true,
            error: null,
            editMode: false,
            canEdit: false,
        });

        onWillStart(() => this._loadDashboard());
        onMounted(() => {
            if (this.state.boardData) {
                this._initSortable();
            }
        });
    }

    get boardId() {
        return this.props.boardId || this.props.action?.context?.board_id;
    }

    async _loadDashboard() {
        if (!this.boardId) {
            this.state.error = "No dashboard configured for this menu.";
            this.state.loading = false;
            return;
        }
        try {
            const data = await this.rpc(`/dynamic_dashboard/get_data/${this.boardId}`, {});
            if (data.error) {
                this.state.error = data.error;
            } else {
                this.state.boardData = data;
                this.state.canEdit = data.can_edit;
            }
        } catch (e) {
            this.state.error = "Failed to load dashboard. Please refresh.";
            console.error(e);
        } finally {
            this.state.loading = false;
        }
    }

    _initSortable() {
        const grid = this.gridRef.el;
        if (!grid || !this.state.canEdit) return;

        // Dynamically load SortableJS from CDN if not already available
        if (typeof Sortable === "undefined") {
            const script = document.createElement("script");
            script.src = "https://cdnjs.cloudflare.com/ajax/libs/Sortable/1.15.2/Sortable.min.js";
            script.onload = () => this._createSortable(grid);
            document.head.appendChild(script);
        } else {
            this._createSortable(grid);
        }
    }

    _createSortable(grid) {
        if (typeof Sortable === "undefined") return;
        this._sortable = Sortable.create(grid, {
            animation: 200,
            handle: ".dd-drag-handle",
            ghostClass: "dd-ghost",
            chosenClass: "dd-chosen",
            onEnd: () => this._saveLayout(),
        });
    }

    async _saveLayout() {
        const items = [...this.gridRef.el.querySelectorAll(".dd-component")].map((el, idx) => ({
            id: parseInt(el.dataset.compId),
            x: parseInt(el.dataset.x || 0),
            y: idx,   // row order after drag
            w: parseInt(el.dataset.w || 4),
            h: parseInt(el.dataset.h || 2),
        }));
        try {
            await this.rpc("/dynamic_dashboard/save_layout", {
                board_id: this.boardId,
                layout: items,
            });
        } catch (e) {
            console.error("Failed to save layout", e);
        }
    }

    toggleEditMode() {
        this.state.editMode = !this.state.editMode;
    }

    openAddComponent() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Add Component",
            res_model: "dashboard.component",
            views: [[false, "form"]],
            target: "new",
            context: {
                default_board_id: this.boardId,
            },
        }, {
            onClose: async () => {
                await this._loadDashboard();
            },
        });
    }

    openEditComponent(comp) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Edit Component",
            res_model: "dashboard.component",
            res_id: comp.id,
            views: [[false, "form"]],
            target: "new",
        }, {
            onClose: async () => {
                await this._loadDashboard();
            },
        });
    }

    async deleteComponent(compId) {
        if (!confirm("Delete this component?")) return;
        try {
            await this.rpc("/dynamic_dashboard/delete_component", { component_id: compId });
            await this._loadDashboard();
            this.notification.add("Component deleted.", { type: "info" });
        } catch (e) {
            this.notification.add("Failed to delete component.", { type: "danger" });
        }
    }

    async refreshComponent(comp) {
        try {
            const data = await this.rpc("/dynamic_dashboard/refresh_component", {
                component_id: comp.id,
            });
            // Replace the component in state
            const idx = this.state.boardData.components.findIndex(c => c.id === comp.id);
            if (idx !== -1) {
                this.state.boardData.components[idx] = data;
            }
        } catch (e) {
            console.error("Refresh failed", e);
        }
    }

    onCardClick(comp) {
        if (!comp.click_action_id) return;
        this.action.doAction({
            type: "ir.actions.act_window",
            id: comp.click_action_id,
            domain: comp.click_domain ? JSON.parse(comp.click_domain) : [],
        });
    }
}

// Register as a client action so it can be linked to menus
registry.category("actions").add("dynamic_dashboard.DashboardClientAction", DynamicDashboard);
