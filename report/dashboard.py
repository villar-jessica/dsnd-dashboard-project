from fasthtml.common import *
import matplotlib.pyplot as plt

# Import QueryBase, Employee, Team from employee_events
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'python-package'))

from employee_events.employee import Employee
from employee_events.team import Team
from utils import load_model

"""
Below, we import the parent classes
you will use for subclassing
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
    )

from combined_components import FormGroup, CombinedComponent


# Create a subclass of base_components/dropdown called `ReportDropdown`
class ReportDropdown(Dropdown):

    def build_component(self, entity_id, model):
        self.label = model.name
        return super().build_component(entity_id, model)

    def component_data(self, entity_id, model):
        return model.names()


# Create a subclass of base_components/BaseComponent called `Header`
class Header(BaseComponent):

    def build_component(self, entity_id, model):
        return H1(model.name)


# Create a subclass of base_components/MatplotlibViz called `LineChart`
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


# Create a subclass of base_components/MatplotlibViz called `BarChart`
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


# Create a subclass of combined_components/CombinedComponent called Visualizations
class Visualizations(CombinedComponent):

    children = [LineChart(), BarChart()]
    outer_div_type = Div(cls='grid')


# Create a subclass of base_components/DataTable called `NotesTable`
class NotesTable(DataTable):

    def component_data(self, entity_id, model):
        return model.notes(entity_id)


class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method="POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
            ),
        ReportDropdown(
            id="selector",
            name="user-selection")
        ]


# Create a subclass of CombinedComponents called `Report`
class Report(CombinedComponent):

    children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]


# Initialize a fasthtml app
app, rt = fast_app(hdrs=[Style(open(Path(__file__).parent.parent / 'assets' / 'report.css').read())])

# Initialize the `Report` class
report = Report()


# Route for root
@rt('/')
def get():
    return report(1, Employee())


# Route for employee by ID
@rt('/employee/{id}')
def get(id: str):
    return report(id, Employee())


# Route for team by ID
@rt('/team/{id}')
def get(id: str):
    return report(id, Team())


# Keep the below code unchanged!
@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)



serve()
