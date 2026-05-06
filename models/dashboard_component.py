from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval
import json
import logging

_logger = logging.getLogger(__name__)

COMPONENT_TYPES = [
    ('card_count', 'Card — Count'),
    ('card_sum', 'Card — Sum'),
    ('chart', 'Chart'),
]

CHART_TYPES = [
    ('bar', 'Bar'),
    ('line', 'Line'),
    ('pie', 'Pie'),
    ('doughnut', 'Doughnut'),
    ('polarArea', 'Polar Area'),
    ('radar', 'Radar'),
]

CARD_STYLES = [
    ('solid', 'Solid'),
    ('outline', 'Outline'),
    ('gradient', 'Gradient'),
    ('soft', 'Soft'),
]


class DashboardComponent(models.Model):
    _name = 'dashboard.component'
    _description = 'Dashboard Component'
    _order = 'sequence, id'

    board_id = fields.Many2one(
        'dashboard.board', string='Dashboard', required=True, ondelete='cascade'
    )
    name = fields.Char(string='Component Name', required=True)
    type = fields.Selection(COMPONENT_TYPES, string='Type', required=True, default='card_count')
    sequence = fields.Integer(default=10)
    is_active = fields.Boolean(default=True)

    # ── Data source ──────────────────────────────────────────────────────────
    model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade')
    model_name = fields.Char(related='model_id.model', store=True, string='Model Name')
    domain = fields.Char(string='Domain Filter', default='[]')

    # ── Measure / Group ───────────────────────────────────────────────────────
    measure_field_id = fields.Many2one(
        'ir.model.fields', string='Measure Field (Sum)',
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['integer','float','monetary'])]"
    )
    group_by_field_id = fields.Many2one(
        'ir.model.fields', string='Group By Field',
        domain="[('model_id', '=', model_id)]"
    )

    # ── Card visual ───────────────────────────────────────────────────────────
    label = fields.Char(string='Label / Title')
    color = fields.Char(string='Color', default='#4F46E5')
    card_style = fields.Selection(CARD_STYLES, string='Card Style', default='solid')
    icon = fields.Char(string='Icon Class', default='fa-chart-bar',
                       help='FontAwesome class, e.g. fa-users, fa-dollar-sign')
    click_action_id = fields.Many2one(
        'ir.actions.act_window', string='Click Action',
        help='Action to open when user clicks the card.'
    )
    prefix = fields.Char(string='Value Prefix', help='e.g. Rp, $')
    suffix = fields.Char(string='Value Suffix', help='e.g. items, orders')

    # ── Chart ─────────────────────────────────────────────────────────────────
    chart_type = fields.Selection(CHART_TYPES, string='Chart Type', default='bar')
    chart_legend = fields.Boolean(string='Show Legend', default=True)
    chart_label = fields.Char(string='Dataset Label')

    # ── Grid position ─────────────────────────────────────────────────────────
    pos_x = fields.Integer(default=0)
    pos_y = fields.Integer(default=0)
    pos_w = fields.Integer(default=4, string='Width (columns)')
    pos_h = fields.Integer(default=2, string='Height (rows)')

    # ── ACL per component ─────────────────────────────────────────────────────
    group_ids = fields.Many2many(
        'res.groups', 'dashboard_comp_group_rel', 'comp_id', 'group_id',
        string='Component Access Groups',
        help='Leave empty to inherit board access. Set groups to restrict this component.'
    )

    def _user_has_access(self):
        self.ensure_one()
        if not self.group_ids:
            return True
        return bool(self.group_ids & self.env.user.groups_id)

    def _get_domain(self):
        self.ensure_one()
        try:
            return safe_eval(self.domain or '[]')
        except Exception:
            _logger.warning('Invalid domain on component %s: %s', self.id, self.domain)
            return []

    def _get_render_data(self):
        """Build the dict sent to the OWL frontend for rendering."""
        self.ensure_one()
        Model = self.env[self.model_id.model]
        domain = self._get_domain()

        data = {
            'id': self.id,
            'type': self.type,
            'name': self.name,
            'label': self.label or self.name,
            'color': self.color or '#4F46E5',
            'card_style': self.card_style,
            'icon': self.icon,
            'prefix': self.prefix or '',
            'suffix': self.suffix or '',
            'pos': {
                'x': self.pos_x,
                'y': self.pos_y,
                'w': self.pos_w,
                'h': self.pos_h,
            },
            'click_action_id': self.click_action_id.id if self.click_action_id else None,
            'click_domain': self.domain or '[]',
            'click_model': self.model_id.model if self.model_id else None,
        }

        if self.type == 'card_count':
            data['value'] = Model.search_count(domain)

        elif self.type == 'card_sum':
            if self.measure_field_id:
                fname = self.measure_field_id.name
                result = Model.read_group(domain, [fname], [])
                data['value'] = round(result[0].get(fname) or 0, 2) if result else 0
            else:
                data['value'] = 0

        elif self.type == 'chart':
            gb_field = self.group_by_field_id.name if self.group_by_field_id else None
            measure = self.measure_field_id.name if self.measure_field_id else None

            if gb_field:
                fields_to_read = [measure] if measure else []
                result = Model.read_group(domain, fields_to_read, [gb_field])
                labels = []
                values = []
                for r in result:
                    raw = r.get(gb_field)
                    # Handle many2one tuples
                    if isinstance(raw, (list, tuple)):
                        raw = raw[1] if len(raw) > 1 else str(raw[0])
                    labels.append(str(raw) if raw is not None else 'N/A')
                    key = measure if measure else f'{gb_field}_count'
                    values.append(round(r.get(key) or 0, 2))
            else:
                labels = ['Total']
                if measure:
                    result = Model.read_group(domain, [measure], [])
                    values = [round(result[0].get(measure) or 0, 2)] if result else [0]
                else:
                    values = [Model.search_count(domain)]

            data['chart_type'] = self.chart_type
            data['chart_legend'] = self.chart_legend
            data['chart_label'] = self.chart_label or self.name
            data['labels'] = labels
            data['values'] = values

        return data
