from odoo import models, fields


class DashboardCardConfig(models.Model):
    """
    Optional extension model for advanced card configurations.
    Currently used as a future hook for per-card theming, conditional
    formatting rules, and additional display options.
    """
    _name = 'dashboard.card.config'
    _description = 'Dashboard Card Advanced Config'

    component_id = fields.Many2one(
        'dashboard.component', string='Component',
        required=True, ondelete='cascade'
    )
    # Conditional formatting
    threshold_warning = fields.Float(string='Warning Threshold')
    threshold_danger = fields.Float(string='Danger Threshold')
    color_warning = fields.Char(string='Warning Color', default='#F59E0B')
    color_danger = fields.Char(string='Danger Color', default='#EF4444')
    color_success = fields.Char(string='Success Color', default='#10B981')

    # Display options
    show_trend = fields.Boolean(string='Show Trend Indicator', default=False)
    trend_period = fields.Selection([
        ('day', 'vs Yesterday'),
        ('week', 'vs Last Week'),
        ('month', 'vs Last Month'),
    ], default='month', string='Trend Period')

    decimal_places = fields.Integer(string='Decimal Places', default=0)
    number_format = fields.Selection([
        ('none', 'Plain Number'),
        ('comma', 'Comma Separated'),
        ('short', 'Shortened (K, M, B)'),
        ('currency', 'Currency'),
    ], default='comma', string='Number Format')
