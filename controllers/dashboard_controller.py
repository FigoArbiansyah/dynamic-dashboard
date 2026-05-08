import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class DynamicDashboardController(http.Controller):

    @http.route(
        '/dynamic_dashboard/get_data/<int:board_id>',
        type='json', auth='user', methods=['POST']
    )
    def get_dashboard_data(self, board_id, **kwargs):
        """Return full dashboard data for the frontend."""
        board = request.env['dashboard.board'].browse(board_id)
        if not board.exists() or not board.is_active:
            return {'error': 'Dashboard not found or inactive.'}
        return board.get_dashboard_data()

    @http.route(
        '/dynamic_dashboard/save_layout',
        type='json', auth='user', methods=['POST']
    )
    def save_layout(self, board_id, layout, **kwargs):
        """
        Persist drag-and-drop grid positions.
        layout: [{id, x, y, w, h}, ...]
        """
        if not request.env.user.has_group('dynamic_dashboard.group_dashboard_manager'):
            return {'error': 'Permission denied.'}

        board = request.env['dashboard.board'].browse(board_id)
        if not board.exists():
            return {'error': 'Board not found.'}

        board.write({'layout_json': json.dumps(layout)})

        Component = request.env['dashboard.component']
        for item in layout:
            comp = Component.browse(item.get('id'))
            if comp.exists() and comp.board_id.id == board_id:
                new_sequence = (item.get('y', 0) + 1) * 10  # convert index to sequence (10, 20, 30…)
                comp.write({
                    'pos_x': item.get('x', 0),
                    'pos_y': item.get('y', 0),
                    'pos_w': item.get('w', 4),
                    'pos_h': item.get('h', 2),
                    'sequence': new_sequence,
                })
        return {'status': 'ok'}

    @http.route(
        '/dynamic_dashboard/get_model_fields',
        type='json', auth='user', methods=['POST']
    )
    def get_model_fields(self, model_name, field_types=None, **kwargs):
        """Return available fields for a given model (used in ConfigDialog)."""
        try:
            ModelObj = request.env[model_name]
        except KeyError:
            return {'error': f'Model {model_name} not found.'}

        fields_data = ModelObj.fields_get(attributes=['string', 'type'])
        result = []
        for fname, finfo in sorted(fields_data.items(), key=lambda x: x[1]['string']):
            if field_types and finfo['type'] not in field_types:
                continue
            result.append({
                'name': fname,
                'label': finfo['string'],
                'type': finfo['type'],
            })
        return result

    @http.route(
        '/dynamic_dashboard/get_available_models',
        type='json', auth='user', methods=['POST']
    )
    def get_available_models(self, **kwargs):
        """Return all installed models for model selector in ConfigDialog."""
        models = request.env['ir.model'].search(
            [('transient', '=', False)],
            order='name'
        )
        return [{'id': m.id, 'name': m.name, 'model': m.model} for m in models]

    @http.route(
        '/dynamic_dashboard/save_component',
        type='json', auth='user', methods=['POST']
    )
    def save_component(self, board_id, component_data, **kwargs):
        """Create or update a single component."""
        if not request.env.user.has_group('dynamic_dashboard.group_dashboard_manager'):
            return {'error': 'Permission denied.'}

        Component = request.env['dashboard.component']
        comp_id = component_data.pop('id', None)

        # Resolve model_id from model string name if needed
        if 'model_name' in component_data and not component_data.get('model_id'):
            model = request.env['ir.model'].search(
                [('model', '=', component_data.pop('model_name'))], limit=1
            )
            component_data['model_id'] = model.id if model else False
        else:
            component_data.pop('model_name', None)

        if comp_id:
            comp = Component.browse(comp_id)
            if comp.exists() and comp.board_id.id == board_id:
                comp.write(component_data)
            else:
                return {'error': 'Component not found or board mismatch.'}
        else:
            component_data['board_id'] = board_id
            comp = Component.create(component_data)

        return {'id': comp.id, 'status': 'ok'}

    @http.route(
        '/dynamic_dashboard/delete_component',
        type='json', auth='user', methods=['POST']
    )
    def delete_component(self, component_id, **kwargs):
        """Delete a component."""
        if not request.env.user.has_group('dynamic_dashboard.group_dashboard_manager'):
            return {'error': 'Permission denied.'}

        comp = request.env['dashboard.component'].browse(component_id)
        if comp.exists():
            comp.unlink()
        return {'status': 'ok'}

    @http.route(
        '/dynamic_dashboard/refresh_component',
        type='json', auth='user', methods=['POST']
    )
    def refresh_component(self, component_id, **kwargs):
        """Refresh data for a single component (for manual refresh button)."""
        comp = request.env['dashboard.component'].browse(component_id)
        if not comp.exists() or not comp._user_has_access():
            return {'error': 'Component not found or access denied.'}
        try:
            return comp._get_render_data()
        except Exception as e:
            _logger.error('Error refreshing component %s: %s', component_id, e)
            return {'error': str(e)}
