{
    'name': 'Dynamic Dashboard',
    'category': 'Tools',
    'summary': 'Create dynamic dashboards with Chart.js',
    'description': """
        Dynamic Dashboard Module
        ========================
        - Create multiple dashboards
        - Add/Edit/Remove charts dynamically
        - Support multiple chart types (bar, line, pie, doughnut)
        - Flexible model selection
        - Real-time data visualization
    """,
    'author': 'Figo Arbiansyah',
    'website': 'https://www.figo.my.id',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'views/dashboard_chart_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dynamic_dashboard/static/src/components/dashboard/dashboard.js',
            "dynamic_dashboard/static/src/components/chart/chart.js",
            'dynamic_dashboard/static/src/components/dashboard/dashboard.xml',
            "dynamic_dashboard/static/src/components/chart/chart.xml",
            'dynamic_dashboard/static/src/components/**/*.js',
            'dynamic_dashboard/static/src/components/**/*.xml',
            'dynamic_dashboard/static/src/components/**/*.css',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}