import logging, os, sys
from pathlib import Path


LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


FMT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

def init_logger(name: str,
                level: int = logging.DEBUG,
                filename: str | None = None) -> logging.Logger:
    """
    Create/reuse a logger that logs both to stdout *and* to logs/<name>.log.
    """

    logger = logging.getLogger(name)
    if logger.handlers:        # already configured → return it
        return logger

    logger.setLevel(level)

    # ── stdout handler ────────────────────────────────────────────────
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(level)
    sh.setFormatter(logging.Formatter(FMT))
    logger.addHandler(sh)

    # ── file handler ─────────────────────────────────────────────────
    if filename is None:
        filename = name.replace(".", "_") + ".log"
    fh_path = LOG_DIR / filename
    fh = logging.FileHandler(fh_path, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter(FMT))
    logger.addHandler(fh)

    logger.propagate = False   # don’t duplicate under root logger
    return logger



# def init_logger(logger_name) -> logging.Logger:
#     path = os.path.join(LOG_PATH, logger_name)
#     os.makedirs(LOG_PATH, exist_ok=True)
#     os.makedirs(os.path.dirname(path), exist_ok=True)
    
#     fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
#     logging.basicConfig(
#         level=logging.INFO,
#         format=fmt,
#         handlers=[
#             logging.StreamHandler(),
#             logging.FileHandler(path, encoding="utf-8")
#         ],
#     )
#     return logging.getLogger("chatbot")