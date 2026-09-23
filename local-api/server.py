#!/usr/bin/env python3
"""
Khabs — local automation API + static site (stdlib only).
Serves agencia-ai-pages/ and CRM API on port 8787.
No real email send — drafts go to crm-lite/outbound/.
"""
from __future__ import annotations

import csv
import json
import os
import re
import secrets
import sys
import urllib.parse
from datetime import datetime, timezone, timedelta
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BRT = timezone(timedelta(hours=-3))
PORT = int(os.environ.get("KHABS_PORT", "8787"))

PAGES_DIR = Path(__file__).resolve().parent.parent  # agencia-ai-pages/
AGENCIA = Path(os.environ.get("KHABS_AGENCIA", str(PAGES_DIR / "agencia-ai" if (PAGES_DIR / "agencia-ai").is_dir() else PAGES_DIR.parent / "agencia-ai")))
CRM = AGENCIA / "crm-lite"
INBOX = CRM / "inbox"
ACCOUNTS = CRM / "accounts"
OUTBOUND = CRM / "outbound"
PIPELINE = CRM / "pipeline.csv"
ACCOUNTS_CSV = CRM / "accounts.csv"

STAGES = [
    "visit",
    "qualify",
    "lead",
    "diagnose_auto",
    "proposal_draft",
    "won",
    "intake_selfserve",
    "kickoff_auto",
    "sprint30",
    "retain",
]

STAGE_CHECKLIST = {
    "lead": ["Lead registrado", "Auto-resposta enfileirada"],
    "diagnose_auto": ["Audit prep", "Engines baseline queued", "Pacote sugerido"],
    "proposal_draft": ["Proposta rascunho", "Aguarda revisão de preço (gate humano se exceção)"],
    "won": ["Contrato assinado (gate humano)", "Setup faturado"],
    "intake_selfserve": ["Intake Parte A", "Acessos solicitados"],
    "kickoff_auto": ["Kickoff notes", "Email pós-kickoff draft", "AuditBot D1"],
    "sprint30": ["Backlog P0", "Primeiro lote conteúdo", "MeasureBot"],
    "retain": ["Retainer ativo", "Relatório recorrente"],
}

PACKAGE_MRR = {"starter": 4900, "growth": 9900, "authority": 19900}
PACKAGE_SETUP = {"starter": 4900, "growth": 8900, "authority": 14900}


def now_iso() -> str:
    return datetime.now(BRT).strftime("%Y-%m-%dT%H:%M:%S-03:00")


def ensure_dirs() -> None:
    for d in (INBOX, ACCOUNTS, OUTBOUND, CRM):
        d.mkdir(parents=True, exist_ok=True)
    if not PIPELINE.exists():
        PIPELINE.write_text(
            "id,created_at,updated_at,company,contact_name,email,phone,source,package_interest,stage,mrr_brl,setup_brl,next_action,owner,notes,token\n",
            encoding="utf-8",
        )
    else:
        # ensure token column
        text = PIPELINE.read_text(encoding="utf-8")
        if text and "token" not in text.splitlines()[0]:
            lines = text.splitlines()
            lines[0] = lines[0].rstrip() + ",token"
            for i in range(1, len(lines)):
                if lines[i].strip():
                    lines[i] = lines[i].rstrip() + ","
            PIPELINE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not ACCOUNTS_CSV.exists():
        ACCOUNTS_CSV.write_text(
            "id,created_at,updated_at,company,website,package,mrr_brl,setup_brl,contract_start,contract_min_months,primary_contact,email,status,engines,prompt_count,notes,token,slug,stage,lead_id\n",
            encoding="utf-8",
        )
    else:
        text = ACCOUNTS_CSV.read_text(encoding="utf-8")
        if text and "token" not in text.splitlines()[0]:
            lines = text.splitlines()
            extra = ",token,slug,stage,lead_id"
            lines[0] = lines[0].rstrip() + extra
            for i in range(1, len(lines)):
                if lines[i].strip():
                    lines[i] = lines[i].rstrip() + ",,,,"
            ACCOUNTS_CSV.write_text("\n".join(lines) + "\n", encoding="utf-8")


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:48] or "conta"


def new_id(prefix: str) -> str:
    ts = datetime.now(BRT).strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{ts}-{secrets.token_hex(3)}"


def new_token() -> str:
    return secrets.token_urlsafe(16)


def read_csv(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    if not fieldnames and rows:
        fieldnames = list(rows[0].keys())
    if not fieldnames:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def append_csv_row(path: Path, row: dict) -> None:
    rows = read_csv(path)
    fieldnames = list(rows[0].keys()) if rows else list(row.keys())
    for k in row:
        if k not in fieldnames:
            fieldnames.append(k)
    rows.append(row)
    write_csv(path, rows, fieldnames)


def update_csv_row(path: Path, match_key: str, match_val: str, updates: dict) -> dict | None:
    rows = read_csv(path)
    if not rows:
        return None
    fieldnames = list(rows[0].keys())
    for k in updates:
        if k not in fieldnames:
            fieldnames.append(k)
    found = None
    for r in rows:
        if r.get(match_key) == match_val:
            r.update(updates)
            found = r
            break
    if found:
        write_csv(path, rows, fieldnames)
    return found


def find_by_token(token: str) -> tuple[str, dict] | None:
    if not token:
        return None
    for r in read_csv(PIPELINE):
        if r.get("token") == token:
            return ("lead", r)
    for r in read_csv(ACCOUNTS_CSV):
        if r.get("token") == token:
            return ("account", r)
    # also search inbox json
    for p in INBOX.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if data.get("token") == token:
                return ("lead", data)
        except Exception:
            pass
    return None


def enqueue_outbound(kind: str, to_email: str, subject: str, body: str, meta: dict | None = None) -> str:
    oid = new_id("OUT")
    payload = {
        "id": oid,
        "created_at": now_iso(),
        "kind": kind,
        "to": to_email,
        "from": "contato@getkhabs.com",
        "subject": subject,
        "body": body,
        "status": "draft_queued",
        "meta": meta or {},
    }
    (OUTBOUND / f"{oid}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return oid


def auto_email_lead(lead: dict) -> str:
    pkg = lead.get("package_interest") or "diagnóstico"
    body = (
        f"Olá {lead.get('contact_name', '').split()[0] or 'olá'},\n\n"
        f"Recebemos seu pedido de diagnóstico GEO para {lead.get('company', 'sua empresa')}.\n\n"
        f"Próximos passos automáticos (Khabs):\n"
        f"1. Em até 1 dia útil: recomendação de pacote + rascunho de proposta ({pkg}).\n"
        f"2. Prep de auditoria nas engines (ChatGPT, Perplexity, Gemini).\n"
        f"3. Você pode adiantar o intake em: onboarding.html?lead={lead.get('id')}&token={lead.get('token')}\n\n"
        f"Portal de status: portal.html?token={lead.get('token')}\n\n"
        f"— Equipe Khabs\ncontato@getkhabs.com\n"
        f"(rascunho local — não enviado)"
    )
    return enqueue_outbound(
        "auto-resposta-lead",
        lead.get("email", ""),
        f"Khabs — recebemos seu diagnóstico ({lead.get('company', '')})",
        body,
        {"lead_id": lead.get("id"), "stage": lead.get("stage")},
    )


def cors_ok(origin: str | None) -> bool:
    if not origin:
        return True
    try:
        u = urllib.parse.urlparse(origin)
        host = (u.hostname or "").lower()
        return host in ("localhost", "127.0.0.1", "::1") or host.endswith(".localhost")
    except Exception:
        return False


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PAGES_DIR), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[khabs-local] {self.address_string()} {fmt % args}\n")

    def _set_cors(self) -> None:
        origin = self.headers.get("Origin")
        if origin and cors_ok(origin):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        elif not origin:
            self.send_header("Access-Control-Allow-Origin", "http://localhost:8787")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")

    def _json(self, code: int, obj: dict) -> None:
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self._set_cors()
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def do_OPTIONS(self) -> None:
        origin = self.headers.get("Origin")
        if origin and not cors_ok(origin):
            self.send_response(403)
            self.end_headers()
            return
        self.send_response(204)
        self._set_cors()
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/status":
            return self.handle_status(parsed)
        if parsed.path == "/api/leads":
            return self.handle_list_leads()
        if parsed.path == "/api/health":
            return self._json(200, {"ok": True, "service": "khabs-local", "port": PORT, "time": now_iso()})
        # static
        return super().do_GET()

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        origin = self.headers.get("Origin")
        if origin and not cors_ok(origin):
            return self._json(403, {"error": "CORS: only localhost"})
        if parsed.path == "/api/leads":
            return self.handle_create_lead()
        if parsed.path == "/api/intake":
            return self.handle_intake()
        if parsed.path == "/api/advance":
            return self.handle_advance()
        return self._json(404, {"error": "not found"})

    def handle_list_leads(self) -> None:
        items = []
        for p in sorted(INBOX.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                items.append(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                pass
        # merge pipeline stages
        pipe = {r.get("id"): r for r in read_csv(PIPELINE)}
        for it in items:
            if it.get("id") in pipe:
                it["stage"] = pipe[it["id"]].get("stage", it.get("stage"))
                it["updated_at"] = pipe[it["id"]].get("updated_at", it.get("updated_at"))
        outbound = []
        for p in sorted(OUTBOUND.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:30]:
            try:
                outbound.append(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                pass
        return self._json(200, {"leads": items, "outbound": outbound, "stages": STAGES})

    def handle_create_lead(self) -> None:
        data = self._read_json()
        nome = (data.get("nome") or data.get("contact_name") or "").strip()
        email = (data.get("email") or "").strip()
        empresa = (data.get("empresa") or data.get("company") or "").strip()
        if len(nome) < 2 or "@" not in email or len(empresa) < 2:
            return self._json(400, {"error": "nome, email e empresa obrigatórios"})

        lid = new_id("L")
        token = new_token()
        pacote = (data.get("pacote") or data.get("package_interest") or "").strip().lower()
        if pacote not in PACKAGE_MRR:
            pacote = ""
        stage = "lead"
        ts = now_iso()
        qual = data.get("qualification") or {}
        lead = {
            "id": lid,
            "created_at": ts,
            "updated_at": ts,
            "company": empresa,
            "contact_name": nome,
            "email": email,
            "phone": data.get("phone") or data.get("telefone") or "",
            "source": data.get("source") or "site-contato",
            "package_interest": pacote,
            "stage": stage,
            "mrr_brl": PACKAGE_MRR.get(pacote, ""),
            "setup_brl": PACKAGE_SETUP.get(pacote, ""),
            "next_action": "diagnose_auto",
            "owner": "QualifyBot",
            "notes": (data.get("mensagem") or data.get("notes") or "")[:2000],
            "token": token,
            "qualification": qual,
            "mensagem": data.get("mensagem") or "",
            "recommended_package": data.get("recommended_package") or pacote,
            "utm": data.get("utm") or {},
        }
        INBOX.mkdir(parents=True, exist_ok=True)
        (INBOX / f"{lid}.json").write_text(json.dumps(lead, ensure_ascii=False, indent=2), encoding="utf-8")
        append_csv_row(
            PIPELINE,
            {
                "id": lid,
                "created_at": ts,
                "updated_at": ts,
                "company": empresa,
                "contact_name": nome,
                "email": email,
                "phone": lead["phone"],
                "source": lead["source"],
                "package_interest": pacote,
                "stage": stage,
                "mrr_brl": lead["mrr_brl"],
                "setup_brl": lead["setup_brl"],
                "next_action": "diagnose_auto",
                "owner": "QualifyBot",
                "notes": lead["notes"][:200],
                "token": token,
            },
        )
        out_id = auto_email_lead(lead)
        # auto-advance to diagnose_auto immediately (bots)
        self._advance_lead(lid, "diagnose_auto", note="auto após lead")
        lead["stage"] = "diagnose_auto"
        lead["outbound_id"] = out_id
        return self._json(
            201,
            {
                "ok": True,
                "id": lid,
                "token": token,
                "stage": lead["stage"],
                "portal_url": f"/portal.html?token={token}",
                "onboarding_url": f"/onboarding.html?lead={lid}&token={token}",
                "obrigado_url": f"/obrigado.html?id={lid}&token={token}",
            },
        )

    def handle_intake(self) -> None:
        data = self._read_json()
        token = (data.get("token") or "").strip()
        lead_id = (data.get("lead_id") or data.get("lead") or "").strip()
        company = (data.get("company") or data.get("empresa") or data.get("nome_fantasia") or "").strip()
        found = find_by_token(token) if token else None
        if not found and lead_id:
            for r in read_csv(PIPELINE):
                if r.get("id") == lead_id:
                    found = ("lead", r)
                    token = r.get("token") or token
                    break
        if not company and found:
            company = found[1].get("company", "")
        if not company:
            return self._json(400, {"error": "company/empresa obrigatório"})

        slug = data.get("slug") or slugify(company)
        acc_dir = ACCOUNTS / slug
        acc_dir.mkdir(parents=True, exist_ok=True)
        ts = now_iso()
        if not token:
            token = new_token()

        intake_path = acc_dir / "intake.json"
        existing = {}
        if intake_path.exists():
            try:
                existing = json.loads(intake_path.read_text(encoding="utf-8"))
            except Exception:
                existing = {}

        account_id = existing.get("account_id") or new_id("A")
        intake = {**existing, **data}
        intake.update(
            {
                "account_id": account_id,
                "slug": slug,
                "token": token,
                "lead_id": lead_id or existing.get("lead_id") or (found[1].get("id") if found else ""),
                "updated_at": ts,
                "created_at": existing.get("created_at") or ts,
                "stage": data.get("stage") or existing.get("stage") or "intake_selfserve",
                "progress_pct": int(data.get("progress_pct") or existing.get("progress_pct") or 0),
                "complete": bool(data.get("complete")),
            }
        )
        intake_path.write_text(json.dumps(intake, ensure_ascii=False, indent=2), encoding="utf-8")

        pkg = (intake.get("package") or intake.get("pacote") or "").lower()
        if pkg not in PACKAGE_MRR and found:
            pkg = (found[1].get("package_interest") or "").lower()

        # upsert accounts.csv
        rows = read_csv(ACCOUNTS_CSV)
        fieldnames = (
            list(rows[0].keys())
            if rows
            else [
                "id",
                "created_at",
                "updated_at",
                "company",
                "website",
                "package",
                "mrr_brl",
                "setup_brl",
                "contract_start",
                "contract_min_months",
                "primary_contact",
                "email",
                "status",
                "engines",
                "prompt_count",
                "notes",
                "token",
                "slug",
                "stage",
                "lead_id",
            ]
        )
        for extra in ("token", "slug", "stage", "lead_id"):
            if extra not in fieldnames:
                fieldnames.append(extra)
        matched = False
        for r in rows:
            if r.get("slug") == slug or r.get("token") == token or r.get("id") == account_id:
                r.update(
                    {
                        "updated_at": ts,
                        "company": company,
                        "website": intake.get("website") or intake.get("site") or r.get("website", ""),
                        "package": pkg or r.get("package", ""),
                        "mrr_brl": PACKAGE_MRR.get(pkg, r.get("mrr_brl", "")),
                        "setup_brl": PACKAGE_SETUP.get(pkg, r.get("setup_brl", "")),
                        "primary_contact": intake.get("decisor_nome") or intake.get("contact_name") or r.get("primary_contact", ""),
                        "email": intake.get("decisor_email") or intake.get("email") or r.get("email", ""),
                        "status": "onboarding" if not intake.get("complete") else "active",
                        "token": token,
                        "slug": slug,
                        "stage": "intake_selfserve" if not intake.get("complete") else intake.get("stage", "intake_selfserve"),
                        "lead_id": intake.get("lead_id", ""),
                        "notes": f"intake {intake.get('progress_pct', 0)}%",
                    }
                )
                matched = True
                break
        if not matched:
            rows.append(
                {
                    "id": account_id,
                    "created_at": ts,
                    "updated_at": ts,
                    "company": company,
                    "website": intake.get("website") or "",
                    "package": pkg,
                    "mrr_brl": PACKAGE_MRR.get(pkg, ""),
                    "setup_brl": PACKAGE_SETUP.get(pkg, ""),
                    "contract_start": "",
                    "contract_min_months": "3" if pkg != "authority" else "6",
                    "primary_contact": intake.get("decisor_nome") or "",
                    "email": intake.get("decisor_email") or intake.get("email") or "",
                    "status": "onboarding",
                    "engines": "",
                    "prompt_count": "",
                    "notes": f"intake {intake.get('progress_pct', 0)}%",
                    "token": token,
                    "slug": slug,
                    "stage": "intake_selfserve",
                    "lead_id": intake.get("lead_id", ""),
                }
            )
        write_csv(ACCOUNTS_CSV, rows, fieldnames)

        if intake.get("lead_id"):
            self._advance_lead(intake["lead_id"], "intake_selfserve", note="intake iniciado")
            if intake.get("complete"):
                self._advance_lead(intake["lead_id"], "kickoff_auto", note="intake completo → kickoff_auto")
                enqueue_outbound(
                    "auto-lembrete-acessos",
                    intake.get("decisor_email") or intake.get("email") or "",
                    f"Khabs — acessos pendentes ({company})",
                    f"Olá,\n\nRecebemos o intake de {company}. Se ainda faltarem CMS/GA4/GSC, responda este rascunho com os convites.\n\nPortal: portal.html?token={token}\n\n— Ops Khabs (rascunho local)",
                    {"slug": slug, "token": token},
                )

        return self._json(
            200,
            {
                "ok": True,
                "account_id": account_id,
                "slug": slug,
                "token": token,
                "stage": intake.get("stage"),
                "progress_pct": intake.get("progress_pct"),
                "portal_url": f"/portal.html?token={token}",
            },
        )

    def handle_status(self, parsed) -> None:
        qs = urllib.parse.parse_qs(parsed.query)
        token = (qs.get("token") or [""])[0].strip()
        if not token:
            return self._json(400, {"error": "token obrigatório"})
        found = find_by_token(token)
        if not found:
            return self._json(404, {"error": "token não encontrado"})
        kind, row = found
        stage = row.get("stage") or "lead"
        # check account intake
        slug = row.get("slug") or slugify(row.get("company", ""))
        intake = None
        intake_path = ACCOUNTS / slug / "intake.json"
        if not intake_path.exists():
            # search by token
            for p in ACCOUNTS.glob("*/intake.json"):
                try:
                    d = json.loads(p.read_text(encoding="utf-8"))
                    if d.get("token") == token:
                        intake = d
                        slug = d.get("slug") or p.parent.name
                        break
                except Exception:
                    pass
        else:
            try:
                intake = json.loads(intake_path.read_text(encoding="utf-8"))
            except Exception:
                intake = None
        if intake and intake.get("stage"):
            stage = intake.get("stage") or stage

        checklist = []
        try:
            idx = STAGES.index(stage) if stage in STAGES else 2
        except ValueError:
            idx = 2
        for i, s in enumerate(STAGES):
            items = STAGE_CHECKLIST.get(s, [])
            status = "done" if i < idx else ("current" if i == idx else "pending")
            checklist.append({"stage": s, "status": status, "items": items})

        pending = []
        if stage in ("proposal_draft", "won"):
            pending.append({"type": "human_gate", "label": "Assinatura de contrato / exceção de preço (Leandro)"})
        if intake and not intake.get("complete"):
            pending.append({"type": "client", "label": f"Completar intake ({intake.get('progress_pct', 0)}%)"})
        if stage in ("intake_selfserve", "kickoff_auto"):
            pending.append({"type": "client", "label": "Convidar acessos CMS / GA4 / GSC"})

        next_report = "placeholder — após kickoff (D28–D30)"
        if stage in ("sprint30", "retain"):
            next_report = "próximo relatório: placeholder (cadência do pacote)"

        return self._json(
            200,
            {
                "ok": True,
                "kind": kind,
                "id": row.get("id") or (intake or {}).get("account_id"),
                "company": row.get("company") or (intake or {}).get("company"),
                "contact_name": row.get("contact_name") or (intake or {}).get("decisor_nome"),
                "email": row.get("email") or (intake or {}).get("email"),
                "package": row.get("package_interest") or row.get("package") or (intake or {}).get("package"),
                "stage": stage,
                "stages": STAGES,
                "checklist": checklist,
                "pending_approvals": pending,
                "next_report_date": next_report,
                "intake_progress": (intake or {}).get("progress_pct", 0) if intake else None,
                "token": token,
                "slug": slug,
                "updated_at": row.get("updated_at") or (intake or {}).get("updated_at"),
            },
        )

    def _advance_lead(self, lead_id: str, to_stage: str, note: str = "") -> dict | None:
        if to_stage not in STAGES:
            return None
        ts = now_iso()
        updated = update_csv_row(
            PIPELINE,
            "id",
            lead_id,
            {"stage": to_stage, "updated_at": ts, "next_action": to_stage, "notes": note[:200]},
        )
        inbox_path = INBOX / f"{lead_id}.json"
        if inbox_path.exists():
            try:
                data = json.loads(inbox_path.read_text(encoding="utf-8"))
                data["stage"] = to_stage
                data["updated_at"] = ts
                if note:
                    data["advance_note"] = note
                inbox_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                pass
        # sync account stage if exists
        for r in read_csv(ACCOUNTS_CSV):
            if r.get("lead_id") == lead_id:
                update_csv_row(ACCOUNTS_CSV, "id", r["id"], {"stage": to_stage, "updated_at": ts})
                slug = r.get("slug")
                if slug:
                    ip = ACCOUNTS / slug / "intake.json"
                    if ip.exists():
                        try:
                            d = json.loads(ip.read_text(encoding="utf-8"))
                            d["stage"] = to_stage
                            d["updated_at"] = ts
                            ip.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
                        except Exception:
                            pass
                break
        return updated

    def handle_advance(self) -> None:
        data = self._read_json()
        lead_id = (data.get("id") or data.get("lead_id") or "").strip()
        token = (data.get("token") or "").strip()
        to_stage = (data.get("stage") or data.get("to") or "").strip()
        note = (data.get("note") or "").strip()

        if token and not lead_id:
            found = find_by_token(token)
            if found:
                lead_id = found[1].get("id") or found[1].get("lead_id") or ""
                if not to_stage:
                    cur = found[1].get("stage") or "lead"
                    try:
                        i = STAGES.index(cur)
                        to_stage = STAGES[min(i + 1, len(STAGES) - 1)]
                    except ValueError:
                        to_stage = "diagnose_auto"

        if not lead_id:
            return self._json(400, {"error": "id ou token obrigatório"})
        if not to_stage:
            # next stage
            rows = read_csv(PIPELINE)
            cur = "lead"
            for r in rows:
                if r.get("id") == lead_id:
                    cur = r.get("stage") or "lead"
                    break
            try:
                i = STAGES.index(cur)
                to_stage = STAGES[min(i + 1, len(STAGES) - 1)]
            except ValueError:
                to_stage = "diagnose_auto"

        if to_stage not in STAGES:
            return self._json(400, {"error": f"stage inválido; use {STAGES}"})

        # human gates — still allow local advance but flag
        human_gates = {"won": "contract_signature", "proposal_draft": "price_exception_if_any"}
        updated = self._advance_lead(lead_id, to_stage, note=note or f"advance → {to_stage}")
        if not updated:
            # create minimal if only in inbox
            inbox_path = INBOX / f"{lead_id}.json"
            if inbox_path.exists():
                self._advance_lead(lead_id, to_stage, note=note)
                updated = json.loads(inbox_path.read_text(encoding="utf-8"))
            else:
                return self._json(404, {"error": "lead não encontrado"})

        # enqueue stage emails as drafts
        email = updated.get("email", "") if isinstance(updated, dict) else ""
        company = updated.get("company", "") if isinstance(updated, dict) else ""
        tok = updated.get("token", token) if isinstance(updated, dict) else token
        if to_stage == "proposal_draft":
            enqueue_outbound(
                "auto-proposta-rascunho",
                email,
                f"Khabs — rascunho de proposta ({company})",
                f"Rascunho de proposta para {company}. Pacote: {updated.get('package_interest','')}.\nVer portal: portal.html?token={tok}\n(rascunho local)",
                {"lead_id": lead_id},
            )
        elif to_stage == "kickoff_auto":
            enqueue_outbound(
                "auto-email-pos-kickoff",
                email,
                f"Khabs — kickoff e próximos 30 dias ({company})",
                f"Kickoff automático iniciado para {company}. AuditBot D1–D5 enfileirado.\nPortal: portal.html?token={tok}\n(rascunho local)",
                {"lead_id": lead_id},
            )
        elif to_stage in ("sprint30", "retain"):
            enqueue_outbound(
                "auto-relatorio-pronto",
                email,
                f"Khabs — relatório / status ({company})",
                f"Atualização de estágio: {to_stage}. Portal: portal.html?token={tok}\n(rascunho local)",
                {"lead_id": lead_id},
            )

        return self._json(
            200,
            {
                "ok": True,
                "id": lead_id,
                "stage": to_stage,
                "human_gate": human_gates.get(to_stage),
                "updated": updated,
            },
        )


def main() -> None:
    ensure_dirs()
    # rewrite pipeline header if empty body only
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Khabs local stack → http://127.0.0.1:{PORT}/", flush=True)
    print(f"  Static: {PAGES_DIR}", flush=True)
    print(f"  CRM:    {CRM}", flush=True)
    print(f"  API:    POST /api/leads | /api/intake | /api/advance | GET /api/status?token=", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutdown", flush=True)
        server.server_close()


if __name__ == "__main__":
    main()
