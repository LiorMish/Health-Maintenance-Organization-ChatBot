from __future__ import annotations
from pathlib import Path
from typing import List, Dict
import re
from bs4 import BeautifulSoup, Tag
from logger import init_logger


logger = init_logger(name="chatbot.rag", level="DEBUG", filename="rag.log")

HMO_NAMES = ["מכבי", "מאוחדת", "כללית"]

class ChunkedKnowledgeBase:
    """Parses the HTML knowledge base into ready-to-embed text chunks."""

    def __init__(self, data_dir: Path):
        self.chunks: List[Dict] = []
        self._load(data_dir)

    # ────────────────────────────────────────────────────────────────
    # Helpers
    # ────────────────────────────────────────────────────────────────
    @staticmethod
    def _clean(txt: str) -> str:
        """Collapse whitespace + strip."""
        return re.sub(r"\s+", " ", txt).strip()

    @staticmethod
    def _hmo_index(hmo: str) -> int:
        """Return the column index inside <table> for the wanted HMO."""
        return {"מכבי": 1, "מאוחדת": 2, "כללית": 3}[hmo]

    # ────────────────────────────────────────────────────────────────
    # Loader
    # ────────────────────────────────────────────────────────────────
    def _load(self, data_dir: Path):
        logger.info("Initializing ChunkedKnowledgeBase with %s", data_dir)
        for html_path in data_dir.glob("*.html"):
            soup  = BeautifulSoup(html_path.read_text("utf-8"), "html.parser")
            topic = self._clean(soup.h2.get_text())

            # full-page description = every <p> before the first <table>
            first_table = soup.find("table")
            desc_parts  = []
            for elem in first_table.find_previous_siblings():
                if isinstance(elem, Tag) and elem.name == "p":
                    desc_parts.insert(0, self._clean(elem.get_text()))
            page_desc = " ".join(desc_parts)

            # treatment table → dict[hmo] = list[str]
            treatments_per_hmo: Dict[str, List[str]] = {h: [] for h in HMO_NAMES}
            rows = first_table.find_all("tr")[1:]       # skip header
            for row in rows:
                cells = [self._clean(td.get_text(" ", strip=True))
                         for td in row.find_all("td")]
                treatment = cells[0]
                for hmo in HMO_NAMES:
                    benefit = cells[self._hmo_index(hmo)]
                    treatments_per_hmo[hmo].append(f"{treatment} – {benefit}")

            # phone numbers section (under the <h3> containing 'מספרי טלפון')
            phone_map = {h: "" for h in HMO_NAMES}
            phone_h3  = soup.find("h3",
                                  string=lambda t: t and "מספרי טלפון" in t)
            if phone_h3:
                for li in phone_h3.find_next("ul").find_all("li"):
                    txt = self._clean(li.get_text())
                    for hmo in HMO_NAMES:
                        if txt.startswith(hmo):
                            phone_map[hmo] = txt.split(":", 1)[1].strip()

            # “לפרטים נוספים” → extra phone/url
            url_map   = {h: "" for h in HMO_NAMES}
            details_h3 = soup.find("h3",
                                   string=lambda t: t and "לפרטים נוספים" in t)
            if details_h3:
                for li in details_h3.find_next("ul").find_all("li"):
                    hmo_name = next((h for h in HMO_NAMES if li.text.strip().startswith(h)), None)
                    if not hmo_name:
                        continue
                    link = li.find("a")
                    if link:
                        url_map[hmo_name] = link["href"]

            # build final chunk per HMO
            for hmo in HMO_NAMES:
                chunk_lines = [
                    f"{topic} | {hmo}",
                    page_desc,
                    "",
                    "טיפולים והטבות",
                    *[f"• {line}" for line in treatments_per_hmo[hmo]],
                ]
                if phone_map[hmo]:
                    chunk_lines += ["", f"טלפון להזמנת טיפולים: {phone_map[hmo]}"]
                if url_map[hmo]:
                    chunk_lines += [f"מידע נוסף: {url_map[hmo]}"]

                chunk_text = "\n".join(chunk_lines)
                self.chunks.append({"hmo": hmo, "topic": topic, "text": chunk_text})

                # debug log
                logger.info("Chunk built: %s | %s (%d chars)",
                          hmo, topic, len(chunk_text))

        logger.info("Loaded %d chunks", len(self.chunks))