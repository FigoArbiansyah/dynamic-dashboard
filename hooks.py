import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """Remove orphaned/corrupt view records before module upgrade.

    Previous versions of this module had extra XML files
    (dashboard_views.xml, dashboard_chart_views.xml) that created
    ir.ui.view records. Those files were later removed from the
    manifest, leaving ghost records in the database whose arch may
    be NULL — which causes ValueError on view loading.
    """
    _logger.info("dynamic_dashboard: cleaning up orphaned view records...")

    # Delete all ir.ui.view records owned by this module
    # (they will be recreated from the current XML files on upgrade)
    env.cr.execute("""
        DELETE FROM ir_ui_view
        WHERE id IN (
            SELECT res_id FROM ir_model_data
            WHERE module = 'dynamic_dashboard'
              AND model = 'ir.ui.view'
        )
    """)
    env.cr.execute("""
        DELETE FROM ir_model_data
        WHERE module = 'dynamic_dashboard'
          AND model = 'ir.ui.view'
    """)

    # Delete orphaned actions (e.g. action_dashboard_chart)
    env.cr.execute("""
        DELETE FROM ir_act_window
        WHERE id IN (
            SELECT res_id FROM ir_model_data
            WHERE module = 'dynamic_dashboard'
              AND model = 'ir.actions.act_window'
              AND name NOT IN ('action_dashboard_board', 'action_dashboard_component')
        )
    """)
    env.cr.execute("""
        DELETE FROM ir_model_data
        WHERE module = 'dynamic_dashboard'
          AND model = 'ir.actions.act_window'
          AND name NOT IN ('action_dashboard_board', 'action_dashboard_component')
    """)

    _logger.info("dynamic_dashboard: orphaned records cleaned up.")
