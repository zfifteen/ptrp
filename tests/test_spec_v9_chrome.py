"""Spec v9 A40 / F54 production chrome. Operator actions stay A1–A39."""

from __future__ import annotations

import re

from tests.conftest import spoken_remark

SCREENS = ("/", "/control", "/records", "/quarantine")
NAV_LABELS = ("Dashboard", "Control", "Records", "Quarantine")


def _chrome_nav_labels(html: str) -> list[str]:
    m = re.search(r"<nav\b[^>]*>(.*?)</nav>", html, flags=re.I | re.S)
    assert m, "chrome <nav> missing"
    return re.findall(r"<a\b[^>]*>([^<]+)</a>", m.group(1), flags=re.I)


def _body_css(html: str) -> str:
    styles = "".join(re.findall(r"<style>(.*?)</style>", html, flags=re.I | re.S))
    m = re.search(r"\bbody\s*\{([^}]*)\}", styles)
    return m.group(1) if m else ""


def _overlay_drawer_css(html: str) -> str:
    styles = "".join(re.findall(r"<style>(.*?)</style>", html, flags=re.I | re.S))
    chunks = []
    for m in re.finditer(
        r"(?:\.overlay\.drawer|\.drawer|#ov-job|#ov-record|#ov-qitem)[^{]*\{([^}]*)\}",
        styles,
    ):
        chunks.append(m.group(1))
    return "\n".join(chunks)


def test_A40_four_screens_cinematic_dark_console(env):
    for path in SCREENS:
        r = env.client.get(path)
        assert r.status_code == 200
        html = r.text
        assert "PTRP" in html
        assert 'id="product"' in html
        assert "brand-sub" in html
        assert re.search(r'class="[^"]*brand-sub[^"]*"[^>]*>\s*operator\s*<', html, flags=re.I)
        assert "--brass" in html
        assert "--void" in html or "#06070c" in html
        body = _body_css(html).replace(" ", "").lower()
        assert "color:#111" not in body
        assert "--void" in body or "#06070c" in body
        assert "MOCK ONLY" not in html
        assert "mock-only" not in html.lower()
        assert 'id="mock-only"' not in html.lower()
        labels = _chrome_nav_labels(html)
        assert tuple(labels) == NAV_LABELS
        assert "Operator" not in labels
        nav_html = re.search(r"<nav\b[^>]*>(.*?)</nav>", html, flags=re.I | re.S).group(1)
        assert "Operator" not in nav_html
        assert len(labels) == 4


def test_A40_dashboard_kind_totals_large_metric_tiles(env):
    html = env.client.get("/").text
    assert 'id="kind-totals"' in html
    assert "data-kind=" in html
    assert re.search(r'class="[^"]*\btile\b', html)
    styles = "".join(re.findall(r"<style>(.*?)</style>", html, flags=re.I | re.S))
    assert re.search(r"\.tile\s+\.v\s*\{[^}]*font-size:\s*32px", styles)
    assert re.search(r"#kind-totals\s+\.tile\s*\{[^}]*min-height", styles)


def test_A40_job_record_qitem_drawers_are_glass(env):
    e, c = env.engine, env.client
    e.add_topic("trade")
    e.add_occasion("press_conference")
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    job = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    assert job.ok
    e.drain()
    jid = job.job["id"]
    recs = e.records_for_job(jid)
    qs = e.list_quarantine()

    html_css = c.get("/").text
    styles = "".join(re.findall(r"<style>(.*?)</style>", html_css, flags=re.I | re.S))
    drawer_css = _overlay_drawer_css(html_css)
    assert "backdrop-filter" in styles
    assert ".drawer" in styles
    assert "rgba(" in drawer_css
    assert "#fafafa" not in drawer_css.lower()
    overlay_rules = re.findall(r"\.overlay\s*\{([^}]*)\}", styles)
    assert overlay_rules
    assert all("#fafafa" not in rule.lower() for rule in overlay_rules)

    job_html = c.get(f"/control?job={jid}").text
    assert 'id="ov-job"' in job_html
    assert re.search(r'id="ov-job"[^>]*class="[^"]*\bdrawer\b', job_html) or re.search(
        r'id="ov-job"[^>]*class="[^"]*\boverlay\b', job_html
    )

    if recs:
        rec_html = c.get(f"/records?record={recs[0]['record_id']}").text
        assert 'id="ov-record"' in rec_html
        assert re.search(
            r'id="ov-record"[^>]*class="[^"]*(\bdrawer\b|\boverlay\b)', rec_html
        )

    if qs:
        q_html = c.get(f"/quarantine?item={qs[0]['id']}").text
        assert 'id="ov-qitem"' in q_html
        assert re.search(
            r'id="ov-qitem"[^>]*class="[^"]*(\bdrawer\b|\boverlay\b)', q_html
        )
    else:
        # Glass chrome still names ov-qitem even when no quarantine row is open.
        assert "ov-qitem" in styles or "ov-qitem" in html_css


def test_F54_light_saas_wireframe_mock_only_fifth_screen_absent(env):
    for path in SCREENS:
        html = env.client.get(path).text
        assert "MOCK ONLY" not in html
        labels = _chrome_nav_labels(html)
        assert len(labels) == 4
        assert "Operator" not in labels
        body = _body_css(html).replace(" ", "").lower()
        assert "color:#111" not in body
        assert "--brass" in html
        assert "--void" in html or "#06070c" in html
