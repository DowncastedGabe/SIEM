import json
from typing import Dict, Any

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Button, Input, Static, DataTable,
    TabbedContent, TabPane
)

# TextArea pode não existir em versões antigas -> fallback para Input multiline simples
try:
    from textual.widgets import TextArea
    HAS_TEXTAREA = True
except Exception:
    TextArea = None
    HAS_TEXTAREA = False

from tui.api_client import APIClient


SAMPLE_INGEST = """[
  {"ts":"2026-03-04T13:40:00Z","src_ip":"203.0.113.10","method":"GET","path":"/admin","status":404,"user_agent":"Mozilla/5.0"},
  {"ts":"2026-03-04T13:40:10Z","src_ip":"203.0.113.10","method":"GET","path":"/wp-login.php","status":404,"user_agent":"Mozilla/5.0"}
]
"""


class SIEMTUI(App):
    CSS = """
    Screen { padding: 1; }
    .bar { height: auto; }
    .filters Input { width: 1fr; }
    DataTable { height: 1fr; }
    #api_status { margin-left: 2; }
    """

    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        super().__init__()
        self.api = APIClient(base_url)

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(classes="bar"):
            yield Static("SIEMzinho (Nginx) — Textual", id="title")
            yield Static("API: ...", id="api_status")
            yield Button("Health", id="btn_health")
            yield Button("Refresh", id="btn_refresh")

        with TabbedContent():
            with TabPane("Events", id="tab_events"):
                with Vertical():
                    with Horizontal(classes="filters"):
                        yield Input(placeholder="src_ip", id="ev_src_ip")
                        yield Input(placeholder="status", id="ev_status")
                        yield Input(placeholder="path_contains", id="ev_path")
                        yield Input(placeholder="from (ISO)", id="ev_from")
                        yield Input(placeholder="to (ISO)", id="ev_to")
                        yield Button("Buscar", id="btn_events_search")

                    self.events_table = DataTable(id="events_table")
                    yield self.events_table

            with TabPane("Alerts", id="tab_alerts"):
                with Vertical():
                    with Horizontal(classes="filters"):
                        yield Input(placeholder="severity", id="al_sev")
                        yield Input(placeholder="rule_name", id="al_rule")
                        yield Input(placeholder="src_ip", id="al_src_ip")
                        yield Input(placeholder="from (ISO)", id="al_from")
                        yield Input(placeholder="to (ISO)", id="al_to")
                        yield Button("Buscar", id="btn_alerts_search")

                    self.alerts_table = DataTable(id="alerts_table")
                    yield self.alerts_table

            with TabPane("Ingest", id="tab_ingest"):
                with Vertical():
                    yield Static("Cole um JSON (objeto ou lista) e envie para /ingest")

                    if HAS_TEXTAREA:
                        self.ingest_text = TextArea(SAMPLE_INGEST, id="ingest_text")
                        yield self.ingest_text
                        self.ingest_result = TextArea("", id="ingest_result")
                        self.ingest_result.read_only = True
                        yield Static("Resposta:")
                        yield self.ingest_result
                    else:
                        # fallback: sem TextArea — mostra aviso
                        yield Static("Seu Textual não tem TextArea. Atualize: pip install -U textual", id="no_textarea")

                    with Horizontal(classes="bar"):
                        yield Button("Enviar", id="btn_ingest_send")
                        yield Button("Carregar Exemplo", id="btn_ingest_sample")

        yield Footer()

    def on_mount(self) -> None:
        # Colunas
        self.events_table.add_columns("ts", "ip", "method", "path", "status", "ua")
        self.alerts_table.add_columns("window", "severity", "rule", "ip", "summary")

        self.check_health()
        self.refresh_all()

    def action_refresh(self) -> None:
        self.refresh_all()

    def set_status(self, msg: str) -> None:
        self.query_one("#api_status", Static).update(f"API: {msg}")

    def check_health(self) -> None:
        try:
            data = self.api.health()
            self.set_status(json.dumps(data))
        except Exception as e:
            self.set_status(f"ERRO: {e}")

    def refresh_all(self) -> None:
        self.refresh_events()
        self.refresh_alerts()

    def _events_params(self) -> Dict[str, str]:
        params: Dict[str, str] = {"limit": "50", "offset": "0"}
        src_ip = self.query_one("#ev_src_ip", Input).value.strip()
        status = self.query_one("#ev_status", Input).value.strip()
        path_contains = self.query_one("#ev_path", Input).value.strip()
        from_ts = self.query_one("#ev_from", Input).value.strip()
        to_ts = self.query_one("#ev_to", Input).value.strip()

        if src_ip: params["src_ip"] = src_ip
        if status: params["status"] = status
        if path_contains: params["path_contains"] = path_contains
        if from_ts: params["from"] = from_ts
        if to_ts: params["to"] = to_ts
        return params

    def refresh_events(self) -> None:
        self.events_table.clear()
        try:
            data = self.api.list_events(self._events_params())
            for e in data:
                ua = (e.get("user_agent") or "")[:35]
                self.events_table.add_row(
                    e.get("ts", ""),
                    e.get("src_ip", ""),
                    e.get("method", ""),
                    e.get("path", ""),
                    str(e.get("status", "")),
                    ua,
                )
        except Exception as e:
            self.set_status(f"ERRO /events: {e}")

    def _alerts_params(self) -> Dict[str, str]:
        params: Dict[str, str] = {"limit": "200", "offset": "0"}
        sev = self.query_one("#al_sev", Input).value.strip()
        rule = self.query_one("#al_rule", Input).value.strip()
        src_ip = self.query_one("#al_src_ip", Input).value.strip()
        from_ts = self.query_one("#al_from", Input).value.strip()
        to_ts = self.query_one("#al_to", Input).value.strip()

        if sev: params["severity"] = sev
        if rule: params["rule_name"] = rule
        if src_ip: params["src_ip"] = src_ip
        if from_ts: params["from"] = from_ts
        if to_ts: params["to"] = to_ts
        return params

    def refresh_alerts(self) -> None:
        self.alerts_table.clear()
        try:
            data = self.api.list_alerts(self._alerts_params())
            for a in data:
                window = f'{a.get("ts_start","")} → {a.get("ts_end","")}'
                self.alerts_table.add_row(
                    window,
                    a.get("severity", ""),
                    a.get("rule_name", ""),
                    a.get("src_ip", ""),
                    a.get("summary", ""),
                )
        except Exception as e:
            self.set_status(f"ERRO /alerts: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id

        if bid == "btn_health":
            self.check_health()
        elif bid == "btn_refresh":
            self.refresh_all()
        elif bid == "btn_events_search":
            self.refresh_events()
        elif bid == "btn_alerts_search":
            self.refresh_alerts()
        elif bid == "btn_ingest_sample" and HAS_TEXTAREA:
            self.ingest_text.text = SAMPLE_INGEST
        elif bid == "btn_ingest_send":
            self.send_ingest()

    def send_ingest(self) -> None:
        if not HAS_TEXTAREA:
            self.set_status("Atualize o Textual para usar a aba Ingest (TextArea).")
            return

        raw = self.ingest_text.text.strip()
        if not raw:
            self.ingest_result.text = "Cole um JSON primeiro."
            return

        try:
            payload: Any = json.loads(raw)
        except Exception as e:
            self.ingest_result.text = f"JSON inválido: {e}"
            return

        try:
            resp = self.api.ingest(payload)
            self.ingest_result.text = json.dumps(resp, indent=2, ensure_ascii=False)
            self.refresh_all()
        except Exception as e:
            self.ingest_result.text = f"Erro /ingest: {e}"


if __name__ == "__main__":
    SIEMTUI(base_url="http://127.0.0.1:5000").run()