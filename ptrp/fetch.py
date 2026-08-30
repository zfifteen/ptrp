"""Injectable fetch ports. Tests inject a scripted port; production uses HTTP."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser

from ptrp.constants import SOURCES

class FetchError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


PUBLIC_URLS = {
    "whitehouse_remarks": "https://www.whitehouse.gov/remarks/",
    "whitehouse_actions": "https://www.whitehouse.gov/presidential-actions/",
    "app": "https://www.presidency.ucsb.edu/documents",
    "factbase": "https://factba.se/",
    "federal_register": "https://www.federalregister.gov/api/v1/documents.json?per_page=20&order=newest&conditions[type][]=PRESDOCU",
    "truth_social": "https://truthsocial.com/api/v1/accounts/lookup?acct=realDonaldTrump",
    "x_personal": "https://x.com/realDonaldTrump",
    "campaign": "https://www.donaldjtrump.com/",
    "books": "https://www.presidency.ucsb.edu/documents",
    "interviews": "https://www.whitehouse.gov/remarks/",
    "legal": "https://www.courtlistener.com/api/rest/v4/search/?q=%22Donald%20Trump%22&type=o",
}

FALLBACK_URLS = {
    "whitehouse_remarks": [
        "https://www.whitehouse.gov/remarks/feed/",
        "https://www.whitehouse.gov/feed/",
    ],
    "whitehouse_actions": [
        "https://www.whitehouse.gov/presidential-actions/feed/",
    ],
    "x_personal": [
        "https://nitter.net/realDonaldTrump/rss",
    ],
}

SOURCE_SHAPE = {
    "whitehouse_remarks": {"kind": "remark", "channel": "spoken"},
    "whitehouse_actions": {"kind": "decision", "channel": "written_official", "act_type": "presidential_action", "direction": "issued"},
    "app": {"kind": "remark", "channel": "spoken"},
    "factbase": {"kind": "remark", "channel": "spoken"},
    "federal_register": {"kind": "decision", "channel": "written_official", "act_type": "executive_order", "direction": "issued"},
    "truth_social": {"kind": "social", "channel": "written_social"},
    "x_personal": {"kind": "social", "channel": "written_social"},
    "campaign": {"kind": "remark", "channel": "spoken"},
    "books": {"kind": "writing", "channel": "other"},
    "interviews": {"kind": "interview", "channel": "spoken"},
    "legal": {"kind": "legal", "channel": "legal", "named_party": "Donald Trump"},
}


def _strip_html(s):
    s = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", s or "")
    s = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", s)
    s = re.sub(r"(?is)<[^>]+>", " ", s)
    s = re.sub(r"&nbsp;", " ", s)
    s = re.sub(r"&amp;", "&", s)
    s = re.sub(r"&lt;", "<", s)
    s = re.sub(r"&gt;", ">", s)
    s = re.sub(r"&quot;", '"', s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _parse_when(value):
    if not value:
        return None
    s = str(value).strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(s.replace("GMT", "+0000"), fmt) if "GMT" in s and "%Z" in fmt else datetime.strptime(s, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            continue
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def _item(source, locator, title, text, when, url, extra=None):
    shape = dict(SOURCE_SHAPE.get(source, {"kind": "remark", "channel": "spoken"}))
    shape.update(extra or {})
    channel = shape["channel"]
    kind = shape["kind"]
    rec = {
        "locator": locator or url or title or "item",
        "text": (text or title or "").strip(),
        "kind": kind,
        "channel": channel,
        "title": title or "",
        "url": url or "",
        "attributed": True,
        "completeness": "excerpt" if text and len(text) < 400 else "full_transcript",
        "topics": [],
        "occasion": None,
        "people": [],
        "phrases": [],
    }
    rec.update(shape)
    rec["kind"] = kind
    rec["channel"] = channel
    if channel == "written_social":
        rec["published_time"] = when
        rec["author_handle"] = shape.get("author_handle") or "realDonaldTrump"
    else:
        rec["event_time"] = when
        if channel == "written_official":
            rec["published_time"] = when
    if source == "legal":
        rec["named_party"] = shape.get("named_party") or "Donald Trump"
    return rec


class _HTMLExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.articles = []
        self._in_a = False
        self._a_href = ""
        self._a_text = []
        self._in_time = False
        self._time_dt = ""
        self._in_p = False
        self._p = []
        self._in_h = False
        self._h = []
        self.paragraphs = []
        self.headings = []
        self.times = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a" and d.get("href"):
            self._in_a = True
            self._a_href = d.get("href")
            self._a_text = []
        elif tag == "time":
            self._in_time = True
            self._time_dt = d.get("datetime") or ""
        elif tag == "p":
            self._in_p = True
            self._p = []
        elif tag in ("h1", "h2", "h3"):
            self._in_h = True
            self._h = []

    def handle_endtag(self, tag):
        if tag == "a" and self._in_a:
            text = "".join(self._a_text).strip()
            if self._a_href:
                self.links.append((self._a_href, text))
            self._in_a = False
        elif tag == "time":
            self._in_time = False
        elif tag == "p":
            t = "".join(self._p).strip()
            if t:
                self.paragraphs.append(t)
            self._in_p = False
        elif tag in ("h1", "h2", "h3"):
            t = "".join(self._h).strip()
            if t:
                self.headings.append(t)
            self._in_h = False

    def handle_data(self, data):
        if self._in_a:
            self._a_text.append(data)
        if self._in_time:
            if data.strip():
                self.times.append(self._time_dt or data.strip())
        if self._in_p:
            self._p.append(data)
        if self._in_h:
            self._h.append(data)


def _abs(base, href):
    if not href:
        return href
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        from urllib.parse import urlparse
        p = urlparse(base)
        return f"{p.scheme}://{p.netloc}{href}"
    return href


def parse_feed(source, body, base_url):
    items = []
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return items
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"
    nodes = list(root.iter(ns + "item")) + list(root.iter(ns + "entry"))
    for node in nodes:
        def txt(names):
            for n in names:
                el = node.find(n)
                if el is None:
                    el = node.find(ns + n)
                if el is not None and (el.text or el.get("href")):
                    return (el.text or "").strip() or el.get("href")
            return ""
        title = txt(["title"])
        link = txt(["link"])
        if not link:
            ln = node.find("link") or node.find(ns + "link")
            if ln is not None:
                link = ln.get("href") or (ln.text or "").strip()
        desc = txt(["description", "summary", "content", "encoded"])
        when = _parse_when(txt(["pubDate", "published", "updated", "date"]))
        locator = link or title
        text = _strip_html(desc) or title
        if title or text:
            items.append(_item(source, locator, title, text, when, link or base_url))
    return items


def parse_json_body(source, body, base_url):
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return []
    items = []
    if isinstance(data, dict) and isinstance(data.get("results"), list):
        rows = data["results"]
    elif isinstance(data, dict) and isinstance(data.get("hits"), dict):
        rows = data["hits"].get("hits") or data.get("results") or []
    elif isinstance(data, list):
        rows = data
    else:
        rows = []
        if isinstance(data, dict) and data.get("id") and data.get("acct"):
            # mastodon account lookup — caller fetches statuses separately
            return [{"_account_id": data.get("id"), "_acct": data.get("acct")}]
    for row in rows:
        if not isinstance(row, dict):
            continue
        if source == "legal" and (row.get("_source") or row.get("caseName") or row.get("cluster_id")):
            src = row.get("_source") or row
            title = src.get("caseName") or src.get("case_name") or src.get("snippet") or "Filing"
            url = src.get("absolute_url") or src.get("url") or base_url
            if url and url.startswith("/"):
                url = "https://www.courtlistener.com" + url
            text = src.get("text") or src.get("snippet") or title
            when = _parse_when(src.get("dateFiled") or src.get("date_filed") or src.get("date_created"))
            items.append(_item(source, url or title, title, text, when, url, {"named_party": "Donald Trump"}))
            continue
        if row.get("content") and row.get("account"):
            acct = (row.get("account") or {}).get("acct") or "realDonaldTrump"
            text = _strip_html(row.get("content") or "")
            url = row.get("url") or row.get("uri") or base_url
            when = _parse_when(row.get("created_at"))
            items.append(_item(source, url, (text[:80] if text else "Post"), text, when, url, {"author_handle": acct}))
            continue
        title = row.get("title") or row.get("heading") or ""
        url = row.get("html_url") or row.get("url") or row.get("body_html_url") or ""
        abstract = row.get("abstract") or row.get("body") or row.get("excerpt") or row.get("description") or title
        when = _parse_when(row.get("publication_date") or row.get("date") or row.get("created_at"))
        extra = {}
        ptype = (row.get("presidential_document_type") or "").lower()
        if ptype:
            extra["act_type"] = ptype.replace(" ", "_")
            extra["direction"] = "issued"
        if title or abstract:
            items.append(_item(source, url or title, title, _strip_html(str(abstract)), when, url, extra))
    return items


def parse_html(source, body, base_url):
    ex = _HTMLExtractor()
    try:
        ex.feed(body)
    except Exception:
        pass
    items = []
    keywords = {
        "whitehouse_remarks": ("/remarks", "/briefing", "/speeches"),
        "whitehouse_actions": ("/presidential-actions", "/executive-order", "/proclamation"),
        "app": ("/documents/", "/node/"),
        "factbase": ("/transcript", "/trump"),
        "campaign": ("/news", "/agenda", "/platform"),
        "books": ("/documents/", "book"),
        "interviews": ("/remarks", "/gaggle", "/interview"),
        "legal": ("/docket", "/opinion"),
        "x_personal": ("/status/", "/realDonaldTrump"),
        "truth_social": ("/@", "/posts/"),
        "federal_register": ("/documents/", "/d/"),
    }.get(source, ("/documents", "/remarks"))
    seen = set()
    for href, text in ex.links:
        url = _abs(base_url, href)
        if any(k in (href or "") or k in (url or "") for k in keywords) or (text and len(text) > 40):
            if url in seen or not text or len(text) < 8:
                continue
            if href.startswith("#") or "javascript:" in href:
                continue
            seen.add(url)
            when = _parse_when(ex.times[0]) if ex.times else None
            para = ex.paragraphs[0] if ex.paragraphs else text
            items.append(_item(source, url, text, para, when, url))
            if len(items) >= 20:
                break
    if not items and (ex.headings or ex.paragraphs):
        title = ex.headings[0] if ex.headings else (ex.paragraphs[0][:80] if ex.paragraphs else source)
        text = " ".join(ex.paragraphs[:8]) or title
        when = _parse_when(ex.times[0]) if ex.times else None
        items.append(_item(source, base_url, title, text, when, base_url))
    return items


def parse_fetched(source, body, url="", content_type=""):
    """Turn a public HTTP body into item dicts. Tests call this with fixtures (no network)."""
    if body is None:
        return []
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    ct = (content_type or "").lower()
    url = url or PUBLIC_URLS.get(source, "")
    stripped = body.lstrip()
    items = []
    if "json" in ct or stripped[:1] in "{[":
        items = parse_json_body(source, stripped, url)
        items = [i for i in items if not i.get("_account_id")]
        if items:
            return items
    if "xml" in ct or "rss" in ct or "atom" in ct or stripped.startswith("<?xml") or "<rss" in stripped[:2000] or "<feed" in stripped[:2000]:
        items = parse_feed(source, stripped, url)
        if items:
            return items
    return parse_html(source, stripped, url)


class HttpFetch:
    """Production adapter. Tests must not use this (no live network)."""

    def __init__(self, getter=None):
        self._getter = getter

    def _http_get(self, url):
        if self._getter:
            return self._getter(url)
        req = urllib.request.Request(
            url, headers={"User-Agent": "PTRP/0.5 (Fate-operated pipeline)"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read(2_000_000)
                ct = resp.headers.get("Content-Type", "")
                charset = "utf-8"
                if "charset=" in ct:
                    charset = ct.split("charset=")[-1].split(";")[0].strip() or "utf-8"
                try:
                    body = raw.decode(charset, "replace")
                except LookupError:
                    body = raw.decode("utf-8", "replace")
                return body, ct, resp.geturl()
        except urllib.error.HTTPError as exc:
            raise FetchError(f"network error fetching {url}: HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise FetchError(f"network error fetching {url}: {exc}") from exc

    def fetch(self, source: str, job_type: str, params: dict):
        if source not in SOURCES:
            raise FetchError(f"source not configured: {source}")
        urls = [PUBLIC_URLS.get(source)] + list(FALLBACK_URLS.get(source) or [])
        urls = [u for u in urls if u]
        last_exc = None
        got_body = False
        items = []
        for url in urls:
            try:
                body, ct, final = self._http_get(url)
                got_body = True
            except FetchError as exc:
                last_exc = exc
                continue
            except Exception as exc:
                last_exc = FetchError(f"parse failed talking to {source}: {exc}")
                continue
            parsed_raw = []
            if body.lstrip()[:1] in "{[":
                try:
                    parsed_raw = parse_json_body(source, body, final)
                except Exception as exc:
                    last_exc = FetchError(f"parse failed talking to {source}: {exc}")
                    parsed_raw = []
            if parsed_raw and parsed_raw[0].get("_account_id"):
                acct_id = parsed_raw[0]["_account_id"]
                acct = parsed_raw[0].get("_acct") or "realDonaldTrump"
                try:
                    body2, ct2, final2 = self._http_get(
                        f"https://truthsocial.com/api/v1/accounts/{acct_id}/statuses?limit=20"
                    )
                    got = parse_fetched(source, body2, final2, ct2)
                    for it in got:
                        it["author_handle"] = acct
                    if got:
                        return got[:40]
                except FetchError as exc:
                    last_exc = exc
                except Exception as exc:
                    last_exc = FetchError(f"parse failed talking to {source}: {exc}")
            try:
                got = parse_fetched(source, body, final, ct)
            except Exception as exc:
                last_exc = FetchError(f"parse failed talking to {source}: {exc}")
                got = []
            if got:
                return got[:40]
        if not got_body and last_exc:
            raise last_exc
        return items
