#!/usr/bin/env python3
"""Pryntor Source Vault R0: explicitly imported, local-only research snapshots."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

MAX_TEXT_BYTES = 1_000_000
TRACKING = {"fbclid", "gclid", "msclkid", "igshid", "mc_cid", "mc_eid"}


def canonical_url(raw: str) -> str:
    p = urlsplit(raw.strip())
    if p.scheme.lower() not in {"https", "http"} or not p.hostname:
        raise ValueError("URL must be an absolute HTTP(S) URL")
    if p.username or p.password:
        raise ValueError("Credentials in URLs are forbidden")
    if any(c.isspace() for c in p.netloc) or p.hostname in {"localhost", "localhost.localdomain"}:
        raise ValueError("Localhost or malformed hostname is forbidden")
    host = p.hostname.lower().rstrip(".")
    if host.endswith((".local", ".internal", ".localhost")):
        raise ValueError("Private hostname is forbidden")
    try:
        import ipaddress
        ip = ipaddress.ip_address(host.strip("[]"))
        if not ip.is_global:
            raise ValueError("Private or non-global IP URLs are forbidden")
    except ValueError as e:
        if "forbidden" in str(e):
            raise
    port = p.port
    netloc = f"[{host}]" if ":" in host else host
    if port and not (p.scheme.lower() == "https" and port == 443) and not (p.scheme.lower() == "http" and port == 80):
        netloc += f":{port}"
    query = urlencode(sorted((k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
                             if not k.lower().startswith("utm_") and k.lower() not in TRACKING))
    return urlunsplit((p.scheme.lower(), netloc, p.path or "/", query, ""))


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            tags TEXT NOT NULL,
            visibility TEXT NOT NULL CHECK (visibility IN ('public','internal')),
            sha256 TEXT NOT NULL,
            captured_at TEXT NOT NULL
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
            title, body, content='documents', content_rowid='id'
        );
        CREATE TRIGGER IF NOT EXISTS docs_ai AFTER INSERT ON documents BEGIN
            INSERT INTO documents_fts(rowid,title,body) VALUES (new.id,new.title,new.body);
        END;
        CREATE TRIGGER IF NOT EXISTS docs_ad AFTER DELETE ON documents BEGIN
            INSERT INTO documents_fts(documents_fts,rowid,title,body) VALUES('delete',old.id,old.title,old.body);
        END;
        CREATE TRIGGER IF NOT EXISTS docs_au AFTER UPDATE ON documents BEGIN
            INSERT INTO documents_fts(documents_fts,rowid,title,body) VALUES('delete',old.id,old.title,old.body);
            INSERT INTO documents_fts(rowid,title,body) VALUES (new.id,new.title,new.body);
        END;
    """)
    return con


def add(con: sqlite3.Connection, url: str, title: str, body: str, tags: str = "", visibility: str = "public") -> int:
    url = canonical_url(url)
    if visibility not in {"public", "internal"}:
        raise ValueError("visibility must be public or internal")
    if not title.strip() or not body.strip():
        raise ValueError("title and body must not be empty")
    if len(body.encode("utf-8")) > MAX_TEXT_BYTES:
        raise ValueError("Snapshot exceeds 1 MB limit")
    taglist = sorted({t.strip().lower() for t in tags.split(",") if t.strip()})
    stamp = dt.datetime.now(dt.timezone.utc).isoformat()
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    with con:
        con.execute("""INSERT INTO documents(url,title,body,tags,visibility,sha256,captured_at)
                       VALUES(?,?,?,?,?,?,?)
                       ON CONFLICT(url) DO UPDATE SET title=excluded.title,body=excluded.body,
                       tags=excluded.tags,visibility=excluded.visibility,sha256=excluded.sha256,
                       captured_at=excluded.captured_at""",
                    (url, title.strip(), body, json.dumps(taglist), visibility, digest, stamp))
    return con.execute("SELECT id FROM documents WHERE url=?", (url,)).fetchone()["id"]


def search(con: sqlite3.Connection, query: str, include_internal: bool = False, limit: int = 20) -> list[dict]:
    terms = re.findall(r"\w+", query, re.UNICODE)[:12]
    if not terms:
        return []
    match = " AND ".join('"' + t.replace('"', '') + '"*' for t in terms)
    visibility = "" if include_internal else "AND d.visibility='public'"
    return [dict(row) for row in con.execute(f"""SELECT d.id, d.url, d.title, d.tags, d.visibility,
        d.sha256, d.captured_at, snippet(documents_fts,1,'[',']',' … ',16) AS snippet
        FROM documents_fts JOIN documents d ON d.id=documents_fts.rowid
        WHERE documents_fts MATCH ? {visibility} ORDER BY rank LIMIT ?""", (match, min(limit, 100)))]


def export_public(con: sqlite3.Connection, include_internal: bool = False) -> list[dict]:
    scope = "" if include_internal else "WHERE visibility='public'"
    return [dict(row) for row in con.execute(f"""SELECT id,url,title,body,tags,visibility,sha256,captured_at
        FROM documents {scope} ORDER BY id""")]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path(".pryntor-source-vault.sqlite3"))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    a = sub.add_parser("add", help="Store an explicitly supplied text snapshot; never fetches the URL")
    a.add_argument("--url", required=True); a.add_argument("--title", required=True)
    a.add_argument("--text-file", type=Path, required=True)
    a.add_argument("--tags", default=""); a.add_argument("--visibility", choices=["public","internal"], default="public")
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--include-internal", action="store_true")
    e = sub.add_parser("export"); e.add_argument("--out", type=Path, required=True)
    e.add_argument("--include-internal", action="store_true", help="Sensitive: opt in explicitly")
    d = sub.add_parser("delete"); d.add_argument("id", type=int)
    sub.add_parser("stats")
    args = parser.parse_args(argv)
    try:
        with connect(args.db) as con:
            if args.command == "init":
                print(f"Initialized local vault at {args.db}")
            elif args.command == "add":
                if not args.text_file.is_file():
                    raise ValueError("Text file does not exist")
                if args.text_file.stat().st_size > MAX_TEXT_BYTES:
                    raise ValueError("Snapshot exceeds 1 MB limit")
                body = args.text_file.read_text(encoding="utf-8")
                doc_id = add(con, args.url, args.title, body, args.tags, args.visibility)
                print(json.dumps({"id":doc_id, "url":canonical_url(args.url)}))
            elif args.command == "search":
                print(json.dumps(search(con,args.query,args.include_internal),indent=2,ensure_ascii=False))
            elif args.command == "export":
                data = export_public(con,args.include_internal)
                args.out.parent.mkdir(parents=True,exist_ok=True)
                args.out.write_text("".join(json.dumps(row,ensure_ascii=False)+"\n" for row in data),encoding="utf-8")
                print(f"Exported {len(data)} records to {args.out}")
            elif args.command == "delete":
                with con:
                    count = con.execute("DELETE FROM documents WHERE id=?",(args.id,)).rowcount
                print(f"Deleted {count} record(s)")
            elif args.command == "stats":
                print(json.dumps({r["visibility"]:r["count"] for r in con.execute("SELECT visibility,count(*) count FROM documents GROUP BY visibility")}))
        return 0
    except (ValueError,UnicodeError,sqlite3.Error,OSError) as e:
        print(f"error: {e}",file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
