/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";

const DEFAULT_STATE = {
    name: "",
    type: "card_count",
    model_name: "",
    domain: "[]",
    label: "",
    color: "#4F46E5",
    card_style: "solid",
    icon: "fa-chart-bar",
    prefix: "",
    suffix: "",
    chart_type: "bar",
    chart_legend: true,
    chart_label: "",
    measure_field_name: "",
    group_by_field_name: "",
    pos_w: 4,
    pos_h: 2,
};

export class ConfigDialog extends Component {
    static template = "dynamic_dashboard.ConfigDialog";
    static components = { Dialog };
    static props = {
        boardId: Number,
        component: { type: Object, optional: true },
        onSave: { type: Function, optional: true },
        close: Function,
    };

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");

        this.state = useState({
            ...DEFAULT_STATE,
            ...(this.props.component || {}),
            availableModels: [],
            numericFields: [],
            allFields: [],
            saving: false,
        });

        if (this.props.component) {
            // Populate field names from the existing component
            this.state.measure_field_name = this.props.component.measure_field_id?.[1] || "";
            this.state.group_by_field_name = this.props.component.group_by_field_id?.[1] || "";
        }

        onWillStart(() => this._loadModels());
    }

    async _loadModels() {
        const models = await this.rpc("/dynamic_dashboard/get_available_models", {});
        this.state.availableModels = models;
        if (this.state.model_name) {
            await this._loadFields(this.state.model_name);
        }
    }

    async _loadFields(modelName) {
        if (!modelName) return;
        const [numericFields, allFields] = await Promise.all([
            this.rpc("/dynamic_dashboard/get_model_fields", {
                model_name: modelName,
                field_types: ["integer", "float", "monetary"],
            }),
            this.rpc("/dynamic_dashboard/get_model_fields", {
                model_name: modelName,
            }),
        ]);
        this.state.numericFields = numericFields;
        this.state.allFields = allFields;
    }

    async onModelChange(ev) {
        this.state.model_name = ev.target.value;
        this.state.measure_field_name = "";
        this.state.group_by_field_name = "";
        await this._loadFields(this.state.model_name);
    }

    onTypeChange(ev) {
        this.state.type = ev.target.value;
    }

    get isCard() {
        return this.state.type === "card_count" || this.state.type === "card_sum";
    }

    get isChart() {
        return this.state.type === "chart";
    }

    get needsMeasure() {
        return this.state.type === "card_sum" || this.state.type === "chart";
    }

    async save() {
        if (!this.state.name) {
            this.notification.add("Component name is required.", { type: "warning" });
            return;
        }
        if (!this.state.model_name) {
            this.notification.add("Please select a model.", { type: "warning" });
            return;
        }

        this.state.saving = true;
        try {
            const payload = {
                id: this.props.component?.id,
                name: this.state.name,
                type: this.state.type,
                model_name: this.state.model_name,
                domain: this.state.domain || "[]",
                label: this.state.label,
                color: this.state.color,
                card_style: this.state.card_style,
                icon: this.state.icon,
                prefix: this.state.prefix,
                suffix: this.state.suffix,
                chart_type: this.state.chart_type,
                chart_legend: this.state.chart_legend,
                chart_label: this.state.chart_label,
                pos_w: parseInt(this.state.pos_w) || 4,
                pos_h: parseInt(this.state.pos_h) || 2,
            };

            // Resolve field IDs from names
            if (this.state.measure_field_name) {
                const f = this.state.numericFields.find(x => x.name === this.state.measure_field_name);
                if (f) payload.measure_field_name = f.name;
            }
            if (this.state.group_by_field_name) {
                payload.group_by_field_name = this.state.group_by_field_name;
            }

            const result = await this.rpc("/dynamic_dashboard/save_component", {
                board_id: this.props.boardId,
                component_data: payload,
            });

            if (result.error) {
                this.notification.add(result.error, { type: "danger" });
                return;
            }

            if (this.props.onSave) await this.props.onSave();
            this.props.close();
        } catch (e) {
            this.notification.add("Failed to save component.", { type: "danger" });
            console.error(e);
        } finally {
            this.state.saving = false;
        }
    }
}
