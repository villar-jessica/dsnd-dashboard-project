# Arquivos com Placeholders

Este documento resume todos os arquivos Python do projeto que contêm placeholders e o que cada um precisa implementar.

---

## 1. `python-package/employee_events/sql_execution.py`

**Função:** Camada de acesso ao banco de dados SQLite.

### O que implementar:
- **`db_path`**: Variável que usa `pathlib.Path` para apontar ao caminho absoluto do arquivo `employee_events.db`.
- **`QueryMixin.pandas_query(sql)`**: Método que executa uma query SQL e retorna o resultado como `pandas.DataFrame` (usar `pd.read_sql_query` com `connect(db_path)`).
- **`QueryMixin.query(sql)`**: Método que executa uma query SQL e retorna resultado como lista de tuplas usando cursor do sqlite3.

---

## 2. `python-package/employee_events/query_base.py`

**Função:** Classe base para todas as queries de entidade (Employee, Team).

### O que implementar:
- **Import** do `QueryMixin` de `sql_execution`.
- **Classe `QueryBase`** herdando de `QueryMixin`:
  - Atributo de classe `name = ""`.
  - **`names()`**: Retorna lista vazia por padrão (será sobrescrito nas subclasses).
  - **`event_counts(id)`**: Retorna DataFrame com query QUERY 1 — agrupa por `event_date`, soma `positive_events` e `negative_events`, juntando a tabela da entidade com `employee_events`, filtrando pelo `id`, ordenado por `event_date`.
  - **`notes(id)`**: Retorna DataFrame com query QUERY 2 — seleciona `note_date` e `note` da tabela `notes`, juntando com a tabela da entidade pelo ID.

---

## 3. `python-package/employee_events/employee.py`

**Função:** Subclasse de `QueryBase` para dados de **funcionários individuais**.

### O que implementar:
- **Import** de `QueryBase` de `query_base`.
- **Import** do decorator `query` e `QueryMixin` de `sql_execution`.
- **Classe `Employee(QueryBase)`**:
  - Atributo `name = "employee"`.
  - **`names()`**: Query 3 — seleciona nome completo (`first_name || ' ' || last_name`) e `employee_id` de todos os funcionários.
  - **`username(id)`**: Query 4 — seleciona o nome completo do funcionário pelo `employee_id` com WHERE filter.
  - **`model_data(id)`**: Adicionar decorator/mixin para que o método existente retorne um `pandas.DataFrame` em vez de a string SQL.

---

## 4. `python-package/employee_events/team.py`

**Função:** Subclasse de `QueryBase` para dados de **equipes**.

### O que implementar:
- **Import** de `QueryBase` de `query_base`.
- **Import** do decorator `query` e `QueryMixin` de `sql_execution`.
- **Classe `Team(QueryBase)`**:
  - Atributo `name = "team"`.
  - **`names()`**: Query 5 — seleciona `team_name` e `team_id` de todos os times.
  - **`username(id)`**: Query 6 — seleciona `team_name` pelo `team_id` com WHERE filter.
  - **`model_data(id)`**: Adicionar decorator/mixin para que o método existente retorne um `pandas.DataFrame`.

---

## 5. `report/utils.py`

**Função:** Utilitários para o dashboard, carregamento do modelo de ML.

### O que implementar:
- **`project_root`**: Variável `pathlib.Path` apontando para a raiz do projeto (pasta `report/` está dentro do projeto, então `project_root = Path(__file__).parent.parent`).
- **`model_path`**: Variável apontando para `assets/model.pkl` dentro do projeto root.
- O `load_model()` já está implementado e usa `model_path`.

---

## 6. `report/dashboard.py`

**Função:** Aplicação FastHTML que gera o dashboard interativo.

### O que implementar:
- **Imports**: `QueryBase`, `Employee`, `Team` de `employee_events`; `load_model` de `utils`.
- **`ReportDropdown(Dropdown)`**: 
  - `build_component()` — define `label` como `model.name`, chama método pai.
  - `component_data()` — chama `model.names()` para obter opções do dropdown.
- **`Header(BaseComponent)`**: `build_component()` — retorna `H1(model.name)`.
- **`LineChart(MatplotlibViz)`**: `visualization(asset_id, model, ax)` — obtém dados de `model.event_counts(asset_id)`, preenche nulos, define índice de data, ordena, calcula cumsum, plota com colunas `['Positive', 'Negative']`, aplica estilo.
- **`BarChart(MatplotlibViz)`**: 
  - `predictor` — atributo de classe com `load_model()`.
  - `visualization()` — obtém `model.model_data(asset_id)`, chama `predict_proba`, extrai coluna 2, calcula mean (equipe) ou valor individual, plota barra horizontal.
- **`Visualizations(CombinedComponent)`**: `children = [LineChart(), BarChart()]`.
- **`NotesTable(DataTable)`**: `component_data()` — retorna `model.notes(entity_id)`.
- **`Report(CombinedComponent)`**: `children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]`.
- **Inicialização do app FastHTML** com rotas:
  - `GET /` → exibe dashboard padrão para Employee ID 1.
  - `GET /employee/{id:str}` → exibe dashboard para funcionário pelo ID.
  - `GET /team/{id:str}` → exibe dashboard para equipe pelo ID.

---

## 7. `tests/test_employee_events.py`

**Função:** Testes pytest para o pacote `employee_events`.

### O que implementar:
- **`project_root`**: Variável com caminho absoluto para raiz do projeto.
- **`@pytest.fixture db_path()`**: Retorna caminho para `employee_events.db`.
- **`test_db_exists(db_path)`**: Asserta que o arquivo DB existe com `db_path.is_file()`.
- **`test_employee_table_exists(table_names)`**: Asserta que `'employee'` está em `table_names`.
- **`test_team_table_exists(table_names)`**: Asserta que `'team'` está em `table_names`.
- **`test_employee_events_table_exists(table_names)`**: Asserta que `'employee_events'` está em `table_names`.

---

## Banco de Dados (`employee_events.db`)

Tabelas existentes:
- **`employee`**: `index`, `employee_id`, `first_name`, `last_name`, `team_id`
- **`team`**: `index`, `team_id`, `team_name`, `shift`, `manager_name`
- **`notes`**: `index`, `employee_id`, `team_id`, `note`, `note_date`
- **`employee_events`**: `index`, `event_date`, `employee_id`, `team_id`, `positive_events`, `negative_events`

