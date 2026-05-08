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
    menu_parent_id = fields.Many2one(
        'ir.ui.menu',
        string='Parent Menu',
        default=lambda self: self.env.ref('dynamic_dashboard.menu_dynamic_dashboard_root', raise_if_not_found=False),
        help='Parent menu used when auto-generating the dashboard menu item.',
    )
    dashboard_action_id = fields.Many2one(
        'ir.actions.client',
        string='Dashboard Action',
        ondelete='set null',
        help='Client action used by the auto-generated dashboard menu.',
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

    def _default_parent_menu(self):
        return self.env.ref('dynamic_dashboard.menu_dynamic_dashboard_root', raise_if_not_found=False)

    def _prepare_dashboard_action_vals(self):
        self.ensure_one()
        return {
            'name': self.name,
            'tag': 'dynamic_dashboard.DashboardClientAction',
            'context': {'board_id': self.id},
        }

    def _prepare_dashboard_menu_vals(self, action):
        self.ensure_one()
        parent_menu = self.menu_parent_id or self._default_parent_menu()
        return {
            'name': self.name,
            'parent_id': parent_menu.id if parent_menu else False,
            'action': f'ir.actions.client,{action.id}',
            'active': self.is_active,
            'groups_id': [(6, 0, self.group_ids.ids)],
            'sequence': 20,
        }

    def _ensure_menu_and_action(self):
        for rec in self:
            action = rec.dashboard_action_id.sudo()
            if not action:
                action = self.env['ir.actions.client'].sudo().create(rec._prepare_dashboard_action_vals())
            else:
                action.write(rec._prepare_dashboard_action_vals())

            menu = rec.menu_id.sudo()
            menu_vals = rec._prepare_dashboard_menu_vals(action)
            if not menu:
                menu = self.env['ir.ui.menu'].sudo().create(menu_vals)
            else:
                menu.write(menu_vals)

            rec.with_context(skip_dashboard_menu_sync=True).sudo().write({
                'dashboard_action_id': action.id,
                'menu_id': menu.id,
            })

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._ensure_menu_and_action()
        return records

    def write(self, vals):
        result = super().write(vals)
        if not self.env.context.get('skip_dashboard_menu_sync'):
            sync_keys = {'name', 'menu_parent_id', 'group_ids', 'is_active'}
            if sync_keys.intersection(vals.keys()) or 'menu_id' in vals or 'dashboard_action_id' in vals:
                self._ensure_menu_and_action()
        return result

    def unlink(self):
        menus = self.mapped('menu_id').sudo()
        actions = self.mapped('dashboard_action_id').sudo()
        result = super().unlink()
        menus.unlink()
        actions.unlink()
        return result
