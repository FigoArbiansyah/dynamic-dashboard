from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Dashboard(models.Model):
    _name = 'dashboard.board'
    _description = 'Dashboard'

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Dashboard Name', required=True)
    chart_ids = fields.One2many('dashboard.chart', 'dashboard_id', string='Charts')
    active = fields.Boolean(default=True)
    user_id = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.user)
    
    def action_view_dashboard(self):
        """Open dashboard view"""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'dynamic_dashboard',
            'name': self.name,
            'context': {'default_dashboard_id': self.id}
        }


class DashboardChart(models.Model):
    _name = 'dashboard.chart'
    _description = 'Dashboard Chart'

    name = fields.Char(string='Chart Title', required=True)
    dashboard_id = fields.Many2one('dashboard.board', string='Dashboard', ondelete='cascade')
    chart_type = fields.Selection([
        ('bar', 'Bar Chart'),
        ('line', 'Line Chart'),
        ('pie', 'Pie Chart'),
        ('doughnut', 'Doughnut Chart'),
        ('polarArea', 'Polar Area Chart'),
    ], string='Chart Type', required=True, default='bar')
    
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    model_name = fields.Char(related='model_id.model', string='Model Name', store=True)
    
    # Field untuk data
    group_by_field_id = fields.Many2one('ir.model.fields', string='Group By Field',
                                        domain="[('model_id', '=', model_id)]",
                                        ondelete='cascade')
    measure_field_id = fields.Many2one('ir.model.fields', string='Measure Field',
                                       domain="[('model_id', '=', model_id), ('ttype', 'in', ['integer', 'float', 'monetary'])]",
                                       ondelete='cascade')
    aggregation_function = fields.Selection([
        ('count', 'Count'),
        ('sum', 'Sum'),
        ('avg', 'Average'),
    ], string='Aggregation', default='count')
    
    # Domain filter
    domain = fields.Text(string='Domain', default='[]',
                        help='Python domain filter for records')
    
    # Chart styling
    color_scheme = fields.Selection([
        ('default', 'Default'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('red', 'Red'),
        ('purple', 'Purple'),
        ('orange', 'Orange'),
    ], string='Color Scheme', default='default')
    
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(default=True)

    @api.constrains('domain')
    def _check_domain(self):
        for record in self:
            if record.domain:
                try:
                    eval(record.domain)
                except Exception as e:
                    raise ValidationError(f'Invalid domain: {str(e)}')

    def get_chart_data(self):
        """Fetch data untuk chart berdasarkan konfigurasi"""
        self.ensure_one()
        
        try:
            domain = eval(self.domain) if self.domain else []
        except:
            domain = []
        
        Model = self.env[self.model_name]
        
        # Jika ada group by
        if self.group_by_field_id:
            group_field = self.group_by_field_id.name
            
            # Read group untuk aggregasi
            if self.aggregation_function == 'count':
                groups = Model.read_group(
                    domain,
                    [group_field],
                    [group_field]
                )
                labels = []
                data = []
                for group in groups:
                    label = group.get(group_field, 'Undefined')
                    if isinstance(label, tuple):
                        label = label[1]
                    labels.append(str(label))
                    data.append(group.get(f'{group_field}_count', 0))
            else:
                if not self.measure_field_id:
                    return {'labels': [], 'datasets': []}
                
                measure_field = self.measure_field_id.name
                groups = Model.read_group(
                    domain,
                    [group_field, f'{measure_field}:{self.aggregation_function}'],
                    [group_field]
                )
                labels = []
                data = []
                for group in groups:
                    label = group.get(group_field, 'Undefined')
                    if isinstance(label, tuple):
                        label = label[1]
                    labels.append(str(label))
                    data.append(group.get(measure_field, 0))
        else:
            # Simple count tanpa grouping
            count = Model.search_count(domain)
            labels = [self.model_id.name]
            data = [count]
        
        return {
            'labels': labels,
            'datasets': [{
                'label': self.name,
                'data': data,
            }]
        }