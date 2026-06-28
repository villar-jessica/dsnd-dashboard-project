"""
DSND Employee Dashboard - resilient entry point.
"""
import os
import sys
import warnings
import traceback

os.environ.setdefault('MPLCONFIGDIR', '/tmp/matplotlib')
os.makedirs('/tmp/matplotlib', exist_ok=True)

warnings.filterwarnings('ignore')
import matplotlib
matplotlib.use('Agg')

from pathlib import Path
from fasthtml.common import *
import uvicorn

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE / 'report'))
sys.path.insert(0, str(_HERE / 'python-package'))

_import_error = None
_import_tb = None

try:
    import matplotlib.pyplot as plt
    from employee_events.employee import Employee
    from employee_events.team import Team
    from utils import load_model
    from base_components import (
        Dropdown, BaseComponent, Radio, MatplotlibViz, DataTable
    )
    from combined_components import FormGroup, CombinedComponent

    class ReportDropdown(Dropdown):
        def build_component(self, entity_id, model):
            self.label = model.name
            return super().build_component(entity_id, model)
        def component_data(self, entity_id, model):
            return model.names()

    class Header(BaseComponent):
        def build_component(self, entity_id, model):
            return H1(model.name)

    class LineChart(MatplotlibViz):
        def visualization(self, entity_id, model):
            df = model.event_counts(entity_id)
            df = df.fillna(0)
            df = df.set_index('event_date').sort_index().cumsum()
            df.columns = ['Positive', 'Negative']
            fig, ax = plt.subplots()
            df.plot(ax=ax)
            self.set_axis_styling(ax, bordercolor='black', fontcolor='black')
            ax.set_title('Cumulative Event Counts')
            ax.set_xlabel('Date')
            ax.set_ylabel('Count')

    class BarChart(MatplotlibViz):
        predictor = load_model()
        def visualization(self, entity_id, model):
            data = model.model_data(entity_id)
            preds = self.predictor.predict_proba(data)[:, 1]
            pred = preds.mean() if model.name == 'team' else preds[0]
            fig, ax = plt.subplots()
            ax.barh([''], [pred])
            ax.set_xlim(0, 1)
            ax.set_title('Predicted Recruitment Risk', fontsize=20)
            self.set_axis_styling(ax, bordercolor='black', fontcolor='black')

    class Visualizations(CombinedComponent):
        children = [LineChart(), BarChart()]
        outer_div_type = Div(cls='grid')

    class NotesTable(DataTable):
        def component_data(self, entity_id, model):
            return model.notes(entity_id)

    class DashboardFilters(FormGroup):
        id = "top-filters"
        action = "/update_data"
        method = "POST"
        children = [
            Radio(values=["Employee", "Team"], name='profile_type',
                  hx_get='/update_dropdown', hx_target='#selector'),
            ReportDropdown(id="selector", name="user-selection")
        ]

    class Report(CombinedComponent):
        children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]

    _css_path = _HERE / 'assets' / 'report.css'
    app, rt = fast_app(hdrs=[Style(_css_path.read_text())])
    report = Report()

    @rt('/')
    def get():
        return report(1, Employee())

    @rt('/employee/{id}')
    def get(id: str):
        return report(id, Employee())

    @rt('/team/{id}')
    def get(id: str):
        return report(id, Team())

    @app.get('/update_dropdown{r}')
    def update_dropdown(r):
        dropdown = DashboardFilters.children[1]
        if r.query_params['profile_type'] == 'Team':
            return dropdown(None, Team())
        return dropdown(None, Employee())

    @app.post('/update_data')
    async def update_data(r):
        from fasthtml.common import RedirectResponse
        data = await r.form()
        profile_type = data._dict['profile_type']
        id = data._dict['user-selection']
        if profile_type == 'Employee':
            return RedirectResponse(f"/employee/{id}", status_code=303)
        return RedirectResponse(f"/team/{id}", status_code=303)

except Exception as _e:
    _import_error = str(_e)
    _import_tb = traceback.format_exc()
    print(f'[ERROR] Dashboard failed to load: {_import_error}', flush=True)
    print(_import_tb, flush=True)

    app, rt = fast_app()

    @rt('/')
    def get():
        return Div(
            H1('Dashboard Loading Error'),
            P(f'Error: {_import_error}'),
            Pre(_import_tb)
        )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    uvicorn.run(app, host='0.0.0.0', port=port, reload=False)
