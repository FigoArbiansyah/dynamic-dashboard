/** @odoo-module **/

import { Component } from "@odoo/owl";

export class CardMetric extends Component {
    static template = "dynamic_dashboard.CardMetric";
    static props = {
        comp: Object,
        onCardClick: { type: Function, optional: true },
    };

    get formattedValue() {
        const val = this.props.comp.value ?? 0;
        if (typeof val !== "number") return val;
        // Format with thousand separators
        return new Intl.NumberFormat("id-ID", { maximumFractionDigits: 2 }).format(val);
    }

    get cardClass() {
        const style = this.props.comp.card_style || "solid";
        return `dd-card dd-card--${style}`;
    }

    get cardStyle() {
        const color = this.props.comp.color || "#4F46E5";
        const style = this.props.comp.card_style || "solid";
        if (style === "solid") {
            return `background-color: ${color}; color: #fff;`;
        } else if (style === "outline") {
            return `border: 2px solid ${color}; color: ${color};`;
        } else if (style === "gradient") {
            return `background: linear-gradient(135deg, ${color}dd, ${color}88); color: #fff;`;
        } else if (style === "soft") {
            return `background-color: ${color}22; color: ${color}; border: 1px solid ${color}44;`;
        }
        return "";
    }

    get iconStyle() {
        const color = this.props.comp.color || "#4F46E5";
        const style = this.props.comp.card_style || "solid";
        if (style === "solid" || style === "gradient") {
            return "color: rgba(255,255,255,0.85);";
        }
        return `color: ${color};`;
    }

    get isClickable() {
        return !!this.props.comp.click_action_id && !!this.props.onCardClick;
    }

    handleClick() {
        if (this.isClickable) {
            this.props.onCardClick();
        }
    }
}
