# SIEMzinho (Nginx) — Flask API + Textual TUI

Um “mini-SIEM” feito para fins de estudo e portfólio: ele **ingere eventos de log (estilo Nginx)** via API, **armazena em SQLite**, permite **consulta com filtros** e gera **alertas** com regras simples (detecção de comportamento suspeito).

A interface é uma **TUI (Terminal UI)** feita com **Textual**, para você usar tudo direto no terminal.

---

## ✨ O que ele faz

### API (Flask)
- **Ingestão de eventos** via `POST /ingest` (um evento ou lista)
- **Consulta de eventos** via `GET /events` com filtros
- **Consulta de alertas** via `GET /alerts` com filtros
- **Healthcheck** via `GET /health`

### Detecções (regras)
- **`nginx_404_burst`**: gera alerta quando um IP retorna muitos `404` em uma janela curta (útil para identificar scanning/recon).

### Front (Textual)
- Aba **Events**: tabela + filtros
- Aba **Alerts**: tabela + filtros
- Aba **Ingest**: colar JSON e enviar para a API

---

## 🧱 Stack

- Python 3.10+ (recomendado)
- Flask
- Flask-SQLAlchemy
- SQLite
- Requests
- Textual (TUI)

---

## 📁 Estrutura do projeto

```
.
├─ app.py                  # runner do backend (chama create_app)
├─ src/
│  ├─ __init__.py           # create_app(), registra blueprints e init do DB
│  ├─ config.py             # configs (DATABASE_URL etc)
│  ├─ extensions.py         # instancia db (SQLAlchemy)
│  ├─ models.py             # models Event e Alert
│  ├─ routes/
│  │  ├─ health.py
│  │  ├─ ingest.py
│  │  ├─ events.py
│  │  └─ alerts.py
│  └─ services/
│     ├─ normalize.py       # valida e normaliza evento
│     └─ detections.py      # regras (ex: nginx_404_burst)
└─ tui/
   ├─ __init__.py
   ├─ api_client.py         # cliente HTTP para a API
   └─ app.py                # TUI Textual (Events / Alerts / Ingest)
```
✅ Pré-requisitos

Ter o Python instalado

Ter o Git (opcional, mas recomendado)

🚀 Como rodar (passo a passo)
1) Crie e ative um virtualenv

Windows (PowerShell):

python -m venv .env
.\.env\Scripts\Activate.ps1

Linux/Mac:

python -m venv .env
source .env/bin/activate
2) Instale dependências
python -m pip install -U pip
python -m pip install flask flask-sqlalchemy requests textual python-dateutil

Se você tiver um requirements.txt, pode usar pip install -r requirements.txt.

3) Rode o backend (API)

Na raiz do projeto:

python app.py

Teste rápido:

GET http://127.0.0.1:5000/health → {"status":"ok"}

4) Rode a TUI (Textual)

Em outro terminal (com o mesmo venv ativo):

python -m tui.app
🔌 Endpoints da API
GET /health

Retorna status da API.

Resposta:

{ "status": "ok" }
POST /ingest

Ingere um evento (objeto JSON) ou vários (lista JSON).

Evento mínimo (Nginx):

{
  "ts": "2026-03-04T13:45:10Z",
  "src_ip": "203.0.113.10",
  "method": "GET",
  "path": "/",
  "status": 200,
  "user_agent": "Mozilla/5.0"
}

Resposta:

{
  "ingested": 1,
  "errors": [],
  "created_alerts": 0
}
GET /events

Lista eventos com filtros via query params:

src_ip

status

path_contains

from (ISO 8601)

to (ISO 8601)

limit (até 200)

offset

Exemplo:

/events?status=404&src_ip=203.0.113.10&limit=50
GET /alerts

Lista alertas com filtros:

severity

rule_name

src_ip

from

to

limit

offset

Exemplo:

/alerts?rule_name=nginx_404_burst

🖥️ Como usar a TUI (Textual)
Teclas

r → refresh geral

q → sair

Aba Events

preencha filtros (src_ip, status, path_contains, from/to)

clique Buscar

tabela mostra os últimos eventos

Aba Alerts

filtros (severity, rule_name, src_ip, from/to)

clique Buscar

tabela mostra os alertas gerados

Aba Ingest

cole o JSON (objeto ou lista)

clique Enviar

ele ingere e atualiza Events/Alerts

🧪 JSON pequeno para testar (menos de 5KB)

Cole na aba Ingest:

[
  {"ts":"2026-03-04T13:40:15Z","src_ip":"203.0.113.10","method":"GET","path":"/admin","status":404,"user_agent":"Mozilla/5.0"},
  {"ts":"2026-03-04T13:40:20Z","src_ip":"203.0.113.10","method":"GET","path":"/wp-login.php","status":404,"user_agent":"Mozilla/5.0"},
  {"ts":"2026-03-04T13:40:25Z","src_ip":"203.0.113.10","method":"GET","path":"/.env","status":404,"user_agent":"Mozilla/5.0"},
  {"ts":"2026-03-04T13:40:30Z","src_ip":"203.0.113.10","method":"GET","path":"/phpmyadmin","status":404,"user_agent":"Mozilla/5.0"}
]

Se você quiser forçar o alerta nginx_404_burst, precisa atingir o threshold configurado na regra (ex: 20x 404 em 5 minutos).

🛠️ Problemas comuns
“No module named textual”

Você instalou no Python errado. Use sempre:

python -m pip install textual
A TUI abre mas não aparece alerta

Provavelmente você ainda não gerou um burst de 404 suficiente. Envie mais eventos 404 do mesmo IP (na mesma janela de tempo), ou reduza o threshold na regra.

Erro de blueprint duplicado (“name ingest already registered”)

Você está registrando o mesmo blueprint duas vezes (ou tem dois arquivos com Blueprint("ingest", ...)).
Garanta que só existe um create_app() e um src/routes/ingest.py.

📌 Próximos upgrades (ideias)

Regra paths sensíveis (/.env, /.git, /wp-login.php…) com severidade maior

Endpoint de métricas (/metrics/summary) com Top IPs e contagem por status

Persistir evidence como JSON de verdade (quando trocar SQLite → Postgres)

Autenticação por API Key + rate limit no /ingest

Exportar relatório (CSV/PDF)

📜 Licença

Projeto educacional / portfólio. Use e modifique à vontade.
