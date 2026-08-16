"""Generate a per-venue SWSconfig from an SGP competition.

Usage:
    python3 tools/gen_swsconfig.py --list
    python3 tools/gen_swsconfig.py [--comp-id 94] [--config-dir /home/angel/src]

Asks for the SGP event ID (or takes --comp-id), pulls the venue from
crosscountry.aero, writes SWSconfig.<location> next to the current
SWSconfig.ini and points SWSconfig.ini at it with a symlink.

The airfield object in the SGP day payload carries the ICAO code ('j') when the
venue has one: with an ICAO the server resolves the position itself and the
latitude/longitude lines stay commented out; without one they are written from
the airfield's own coordinates.

Data is pulled through src/SGP/sgp_api.py (no MCP runtime required).
"""
import argparse
import re
import sys
from pathlib import Path

import httpx
import pycountry

_SGP = str(Path(__file__).resolve().parent.parent / "src" / "SGP")
if _SGP not in sys.path:
    sys.path.insert(0, _SGP)

import sgp_api  # noqa: E402

CANCELLED = 3
COORDS = ("location_latitude", "location_longitud")
LIST_LIMIT = 10


# --------------------------------------------------------------------------- #
# SGP
# --------------------------------------------------------------------------- #
def fetch_airfield(comp_id: int, days: list[dict]) -> dict:
    """Return the raw airfield object of the first day that has a task.

    decode_task() drops the airfield's coordinates and ICAO code, so the raw day
    payload is read here instead. Days without a task return an empty body.
    """
    for day in days:
        if day.get("type") == CANCELLED:
            continue
        url = sgp_api.DAY_URL.format(comp_id=comp_id, day_id=day["day_id"])
        try:
            day_obj = sgp_api._get_json(url)
        except (httpx.HTTPError, ValueError):
            continue
        airfield = ((day_obj.get("k") or {}).get("data") or {}).get("at")
        if airfield:
            return airfield
    raise SystemExit(f"No day of competition {comp_id} has a task with an airfield.")


def list_competitions() -> None:
    """Print the most recent SGP competitions as id / title / venue / dates."""
    comps = sorted(sgp_api.fetch_competitions(),
                   key=lambda c: c.get("first_date") or "", reverse=True)
    for comp in comps[:LIST_LIMIT]:
        venue = ", ".join(filter(None, (comp.get("venue"), comp.get("country"))))
        print(f"{comp['id']:>4}  {(comp.get('title') or ''):<44.44}  {venue:<26.26}  "
              f"{comp.get('first_date')} .. {comp.get('last_date')}")


def country_name(alpha2: str) -> str:
    country = pycountry.countries.get(alpha_2=(alpha2 or "").upper())
    return country.name if country else alpha2


def collect(comp_id: int) -> tuple[dict, tuple]:
    """Return the config settings, plus the keys that must stay commented out."""
    try:
        comp = sgp_api.fetch_competition(comp_id)
    except (httpx.HTTPError, ValueError) as exc:
        raise SystemExit(f"Cannot read SGP competition {comp_id}: {exc}")
    if not comp.get("name"):
        raise SystemExit(f"No SGP competition with id {comp_id}.")
    summary = next(
        (c for c in sgp_api.fetch_competitions() if c["id"] == comp_id), {})

    airfield = fetch_airfield(comp_id, comp["days"])
    icao = (airfield.get("j") or "").strip().upper()
    name = airfield.get("n")
    latitude, longitude = airfield.get("a"), airfield.get("o")

    if latitude is None or longitude is None:
        raise SystemExit(f"Airfield '{name}' has no coordinates in the SGP data.")

    # With an ICAO code the server looks the position up itself, so the
    # coordinates are still written but left commented out, as documentation.
    is_icao = bool(re.fullmatch(r"[A-Z]{4}", icao))

    venue = summary.get("venue") or name
    country = country_name(airfield.get("c") or summary.get("country"))
    event = f"{comp['name']} - {venue}, {country}"

    settings = {
        "location_name": icao if is_icao else name,
        "location_latitude": latitude,
        "location_longitud": longitude,
        "eventname1": event,
        "eventdesc1": event,
        "eventdesc2": f"OGN Live tracking in {venue}, {country}",
    }
    return settings, COORDS if is_icao else ()


# --------------------------------------------------------------------------- #
# Config rewriting
# --------------------------------------------------------------------------- #
def _line_re(key: str) -> re.Pattern:
    """Match a key line, live or ';'-commented, capturing its layout."""
    return re.compile(rf"^(;\s*)?({key})(\s*[:=]\s*)(.*?)(\s*)$")


def _rewrite(match: re.Match, value, comment: bool) -> str:
    """Re-emit a matched line with a new value, keeping its separator and quoting.

    Quoting follows the line being replaced: 'LILC' and "event text" keep their
    quotes, the bare decimal coordinates stay bare.
    """
    _, key, sep, old, trail = match.groups()
    quote = old[0] if old[:1] in ("'", '"') else ""
    return f"{';' if comment else ''}{key}{sep}{quote}{value}{quote}{trail}\n"


def apply_settings(text: str, settings: dict, commented: tuple = ()) -> str:
    """Set each key in place, leaving every other line byte-for-byte intact."""
    patterns = {key: _line_re(key) for key in settings}
    seen, out = set(), []

    for line in text.splitlines(keepends=True):
        for key, pattern in patterns.items():
            match = pattern.match(line.rstrip("\n"))
            if not match:
                continue
            seen.add(key)
            out.append(_rewrite(match, settings[key], comment=key in commented))
            break
        else:
            out.append(line)

    missing = [key for key in settings if key not in seen]
    if missing:
        raise SystemExit("Keys not found in the template config: " + ", ".join(missing))
    return "".join(out)


def slug(location: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", location).strip("_")


def write_config(config_dir: Path, settings: dict, commented: tuple) -> Path:
    ini = config_dir / "SWSconfig.ini"
    if not ini.exists():
        raise SystemExit(f"{ini} not found.")

    target = config_dir / f"SWSconfig.{slug(settings['location_name'])}"
    target.write_text(apply_settings(ini.read_text(), settings, commented))
    print(f"wrote {target}")

    if ini.is_symlink():
        ini.unlink()
    elif ini.is_file():
        backup = config_dir / "SWSconfig.ini.bak"
        if backup.exists():
            ini.unlink()
        else:
            ini.rename(backup)
            print(f"backed up previous SWSconfig.ini -> {backup.name}")
    ini.symlink_to(target.name)
    print(f"SWSconfig.ini -> {target.name}")
    return target


# --------------------------------------------------------------------------- #
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Generate SWSconfig.<location> from an SGP competition.")
    ap.add_argument("--list", action="store_true",
                    help=f"list the {LIST_LIMIT} most recent SGP competitions and exit")
    ap.add_argument("--comp-id", type=int, default=None,
                    help="SGP event id (prompted for when omitted)")
    ap.add_argument("--config-dir", type=Path,
                    default=Path(__file__).resolve().parent.parent / "src",
                    help="directory holding SWSconfig.ini")
    args = ap.parse_args(argv)

    if args.list:
        list_competitions()
        return 0

    comp_id = args.comp_id
    if comp_id is None:
        try:
            comp_id = int(input("SGP event ID: ").strip())
        except ValueError:
            raise SystemExit("The SGP event ID must be a number.")

    settings, commented = collect(comp_id)
    write_config(args.config_dir, settings, commented)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
