from odoo import models, fields, api
import json


class DashboardBoard(models.Model):
    _name = 'dashboard.board'
    _description = 'Dynamic Dashboard Board'
    _order = 'name'

    name = fields.Char(string='Dashboard Name', required=True)
    menu_id = fields.Many2one(
        'ir.ui.menu', string='Menu', ondelete='set null',
        help='Menu where this dashboard will be displayed (one menu = one dashboard).'
    )
    group_ids = fields.Many2many(
        'res.groups', 'dashboard_board_group_rel', 'board_id', 'group_id',
        string='Access Groups',
        help='Leave empty to allow all users. Set groups to restrict access.'
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company
    )
    is_active = fields.Boolean(string='Active', default=True)
    layout_json = fields.Text(
        string='Layout JSON', default='[]',
        help='Stores grid positions of components as JSON.'
    )
    cache_ttl = fields.Integer(
        string='Cache TTL (seconds)', default=300,
        help='How long to cache component query results. 0 = no cache.'
    )
    component_ids = fields.One2many(
        'dashboard.component', 'board_id', string='Components'
    )
    component_count = fields.Integer(
        string='Components', compute='_compute_component_count'
    )

    @api.depends('component_ids')
    def _compute_component_count(self):
        for rec in self:
            rec.component_count = len(rec.component_ids)

    def _user_can_access(self):
        """Check if current user can access this board."""
        self.ensure_one()
        if not self.group_ids:
            return True
        return bool(self.group_ids & self.env.user.groups_id)

    def get_dashboard_data(self):
        """Return full dashboard data including all accessible components."""
        self.ensure_one()
        if not self._user_can_access():
            return {'error': 'Access denied'}

        components = []
        for comp in self.component_ids.filtered('is_active').sorted('sequence'):
            if comp._user_has_access():
                try:
                    components.append(comp._get_render_data())
                except Exception as e:
                    components.append({
                        'id': comp.id,
                        'type': comp.type,
                        'name': comp.name,
                        'error': str(e),
                    })

        return {
            'id': self.id,
            'name': self.name,
            'layout': json.loads(self.layout_json or '[]'),
            'components': components,
            'can_edit': self.env.user.has_group('dynamic_dashboard.group_dashboard_manager'),
        }

    def action_view_components(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Components',
            'res_model': 'dashboard.component',
            'view_mode': 'tree,form',
            'domain': [('board_id', '=', self.id)],
            'context': {'default_board_id': self.id},
        }
