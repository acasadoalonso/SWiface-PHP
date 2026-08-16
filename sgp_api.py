"""
sgp_api.py — Fetch and decode SGP (Sailplane Grand Prix) competition data.

Data source: the crosscountry.aero SGP REST API, the same backend used by
sgp2sws.py. The API returns terse single-letter keys; the functions here fetch
the raw JSON and decode it into readable structures for competitions, pilots,
and tasks.

Endpoints:
  - https://data.crosscountry.aero/public/get/events  -> competition list
  - https://www.crosscountry.aero/c/sgp/rest/comp/{id} -> competition + pilots + days
  - https://www.crosscountry.aero/c/sgp/rest/day/{id}/{dayid} -> task + waypoints
  - https://rankingdata.fai.org/rest/api/rlpilot?id={id}       -> FAI ranking entry

The decode_* functions are pure (raw dict in, clean dict out) so they can be
unit-tested against saved fixtures without network access.
"""

import json

import httpx

EVENTS_URL = "https://data.crosscountry.aero/public/get/events"
COMP_URL = "https://www.crosscountry.aero/c/sgp/rest/comp/{comp_id}"
DAY_URL = "https://www.crosscountry.aero/c/sgp/rest/day/{comp_id}/{day_id}"

# FAI ranking-list REST API (Ranking list REST API v.0.23). The public rlpilot
# call resolves one pilot by their ranking-list id; used to validate the
# ranking_id carried by each SGP pilot.
RANKING_PILOT_URL = "https://rankingdata.fai.org/rest/api/rlpilot?id={ranking_id}"

USER_AGENT = "Mozilla/5.0 (compatible; sgp-mcp/1.0)"

# Day types as documented in sgp2sws.py.
DAY_TYPES = {1: "Race", 2: "Practice", 3: "Cancelled", 4: "Rest", 9: "Other"}

# Results status, from the day payload's scoring object ('r.u').
RESULT_STATUS = {0: "preliminary", 1: "unofficial", 2: "official"}


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def _get_json(url: str) -> dict | list:
    """GET a URL and parse JSON. Raise a clear error on failure."""
    resp = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=15.0)
    resp.raise_for_status()
    text = resp.text.strip()
    if not text:
        raise ValueError(f"Empty response from {url} (competition not activated yet?)")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Non-JSON response from {url}: {exc}") from exc


# --------------------------------------------------------------------------- #
# Decoders (pure)
# --------------------------------------------------------------------------- #
def decode_competition_summary(event: dict) -> dict:
    """Decode one entry from the /get/events list."""
    return {
        "id": event.get("id"),
        "title": event.get("fullEditionTitle"),
        "edition_title": event.get("editionTitle"),
        "venue": event.get("venue"),
        "country": event.get("country"),
        "status": event.get("status"),
        "first_date": event.get("firstDate"),
        "first_racing_date": event.get("firstRacingDate"),
        "last_date": event.get("lastDate"),
        "final": event.get("final"),
    }


def decode_pilot(raw: dict) -> dict:
    """Decode one pilot from the comp 'p' map."""
    first = raw.get("f", "")
    last = raw.get("l", "")
    return {
        "id": raw.get("i"),
        "name": f"{first} {last}".strip(),
        "first_name": first,
        "last_name": last,
        "competition_number": raw.get("d"),
        "country": raw.get("z"),
        "aircraft": raw.get("s"),
        "registration": (raw.get("w") or "").strip(),
        "flarm_id": (raw.get("q") or "").strip(),
        "ranking_id": (raw.get("r") or "").strip(),
    }


def decode_day_index_entry(raw: dict) -> dict:
    """Decode one day from the comp 'i' day index."""
    day_type = raw.get("y")
    return {
        "day_id": raw.get("i"),
        "date": raw.get("d"),
        "title": raw.get("t"),
        "short_title": raw.get("l"),
        "type": day_type,
        "type_label": DAY_TYPES.get(day_type, "Unknown"),
    }


def decode_competition(comp_obj: dict) -> dict:
    """Decode the comp/{id} payload into competition info plus its day index."""
    comp = comp_obj.get("c") or {}
    days_raw = comp_obj.get("i")
    days = [decode_day_index_entry(d) for d in days_raw] if isinstance(days_raw, list) else []
    pilots = comp_obj.get("p") or {}
    return {
        "id": comp.get("i"),
        "name": comp.get("t"),
        "short_name": comp.get("l"),
        "first_day": comp.get("a"),
        "last_day": comp.get("b"),
        "pilot_count": len(pilots),
        "active_days": comp_obj.get("j"),
        "days": days,
    }


def _decode_turnpoint(raw: dict, index: int, last_index: int) -> dict:
    """Decode one waypoint from the task 'g' list."""
    oz = "Line" if raw.get("y") == "line" else "Cylinder"
    if index == 0:
        role = "Start"
    elif index == last_index:
        role = "Finish"
    else:
        role = "Turnpoint"
    return {
        "index": index,
        "name": raw.get("n"),
        "role": role,
        "latitude": raw.get("a"),
        "longitude": raw.get("o"),
        "observation_zone": oz,
        "radius": raw.get("r"),
    }


def decode_task(day_obj: dict) -> dict:
    """Decode a day/{id}/{dayid} payload into task info and turnpoints."""
    task = day_obj.get("k")
    if not task:
        return {"error": "No task set for this day."}

    data = task.get("data") or {}
    airfield = data.get("at") or {}
    waypoints = data.get("g") or []

    # description is itself a JSON string: {"d": "205.16 km", "ta": "..."}
    length = None
    task_from = None
    desc_raw = task.get("description")
    if desc_raw:
        try:
            desc = json.loads(desc_raw)
            length = desc.get("d")
            task_from = desc.get("ta")
        except (json.JSONDecodeError, TypeError):
            pass

    last_index = len(waypoints) - 1
    turnpoints = [_decode_turnpoint(w, i, last_index) for i, w in enumerate(waypoints)]

    return {
        "task_id": task.get("id"),
        "name": task.get("name"),
        "type": task.get("@type"),
        "length": length,
        "task_from": task_from,
        "airfield": airfield.get("n"),
        "elevation": airfield.get("e"),
        "timezone": airfield.get("z"),
        "start_altitude": day_obj.get("h"),
        "finish_altitude": day_obj.get("f"),
        "start_time_millis": day_obj.get("a"),
        "date_millis": day_obj.get("d"),
        "turnpoints": turnpoints,
    }


def _pilot_label(pilots_by_id: dict | None, pilot_id) -> dict:
    """Look up name/country for a pilot id; blank fields if unknown."""
    pilot = (pilots_by_id or {}).get(pilot_id) or {}
    return {
        "name": pilot.get("name"),
        "country": pilot.get("country"),
    }


def decode_day_results(day_obj: dict, pilots_by_id: dict | None = None) -> dict:
    """Decode one day's individual results from the day payload's 'r.s' list.

    `pilots_by_id` maps pilot id -> decoded pilot dict; when given, each result
    is enriched with the pilot's name and country.
    """
    scoring = day_obj.get("r") or {}
    scores = scoring.get("s")
    if not scores:
        return {"error": "No results for this day."}

    results = []
    for e in scores:
        pilot_id = e.get("h")
        rank_raw = e.get("r")
        results.append({
            "rank": int(rank_raw) if str(rank_raw).isdigit() else rank_raw,
            "competition_number": e.get("j"),
            "pilot_id": pilot_id,
            **_pilot_label(pilots_by_id, pilot_id),
            "points": e.get("p"),
            "speed_kph": e.get("s"),
            "distance_km": e.get("d"),
            "task_time_seconds": (e.get("t") or 0) / 1000,
            "finished": e.get("c"),
            "start_time_millis": e.get("a"),
            "finish_time_millis": e.get("b"),
            "igc_file": e.get("g"),
        })

    results.sort(key=lambda r: r["rank"] if isinstance(r["rank"], int) else 9999)
    status = scoring.get("u")
    return {
        "day_id": day_obj.get("i"),
        "results_status": status,
        "results_status_label": RESULT_STATUS.get(status, "unknown"),
        "results": results,
    }


def decode_total_results(day_obj: dict, pilots_by_id: dict | None = None) -> dict:
    """Decode cumulative standings as of this day from the 'r.t' aggregation map.

    'r.t' maps pilot id -> total points scored to date. `pilots_by_id`, when
    given, enriches each standing with the pilot's name and country.
    """
    scoring = day_obj.get("r") or {}
    totals = scoring.get("t")
    if not totals:
        return {"error": "No cumulative results for this day."}

    standings = []
    for pid_str, points in totals.items():
        pilot_id = int(pid_str) if str(pid_str).isdigit() else pid_str
        pilot = (pilots_by_id or {}).get(pilot_id) or {}
        standings.append({
            "pilot_id": pilot_id,
            "competition_number": pilot.get("competition_number"),
            **_pilot_label(pilots_by_id, pilot_id),
            "total_points": points,
        })

    standings.sort(key=lambda s: s["total_points"], reverse=True)
    for rank, s in enumerate(standings, start=1):
        s["rank"] = rank

    status = scoring.get("u")
    return {
        "day_id": day_obj.get("i"),
        "results_status": status,
        "results_status_label": RESULT_STATUS.get(status, "unknown"),
        "standings": standings,
    }


def decode_ranking_pilot(payload: dict | None, requested_id) -> dict:
    """Validate an rlpilot?id= response against the requested ranking-list id.

    For a known id the live API returns {"data": [ {...} ]}; for an unknown one
    "data" is null. Returns a flat verdict: `valid` plus the pilot's name,
    nationality, and ranking points/position when found.
    """
    requested = str(requested_id)
    payload = payload if isinstance(payload, dict) else {}
    data = payload.get("data")
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        records = data.get("object_name") or []
    else:
        records = payload.get("object_name") or []
    rec = records[0] if records else None

    if not rec:
        return {
            "ranking_id": requested,
            "valid": False,
            "message": "No FAI ranking-list entry found for this id.",
        }

    first = rec.get("firstname") or ""
    surname = rec.get("surname") or ""
    return {
        "ranking_id": requested,
        "valid": str(rec.get("pilotid")) == requested,
        "pilot_id": rec.get("pilotid"),
        "name": f"{first} {surname}".strip(),
        "nationality": rec.get("nationality"),
        "ranking_points": rec.get("rankingpts"),
        "ranking_position": rec.get("rankingpos"),
    }


# --------------------------------------------------------------------------- #
# Fetch wrappers (network + decode)
# --------------------------------------------------------------------------- #
def fetch_competitions() -> list[dict]:
    events = _get_json(EVENTS_URL)
    if not isinstance(events, list):
        raise ValueError("Unexpected events payload (expected a list).")
    return [decode_competition_summary(e) for e in events]


def fetch_competition(comp_id: int) -> dict:
    return decode_competition(_get_json(COMP_URL.format(comp_id=comp_id)))


def fetch_pilots(comp_id: int) -> list[dict]:
    comp_obj = _get_json(COMP_URL.format(comp_id=comp_id))
    pilots = comp_obj.get("p") or {}
    return [decode_pilot(pilots[k]) for k in pilots]


def fetch_task(comp_id: int, day_id: int) -> dict:
    return decode_task(_get_json(DAY_URL.format(comp_id=comp_id, day_id=day_id)))


def fetch_task_waypoints(comp_id: int, day_id: int) -> list[dict]:
    return fetch_task(comp_id, day_id).get("turnpoints", [])


def fetch_task_length(comp_id: int, day_id: int) -> dict:
    task = fetch_task(comp_id, day_id)
    return {
        "task_id": task.get("task_id"),
        "name": task.get("name"),
        "type": task.get("type"),
        "length": task.get("length"),
        "waypoint_count": len(task.get("turnpoints", [])),
    }


def _pilots_by_id(comp_id: int) -> dict:
    return {p["id"]: p for p in fetch_pilots(comp_id)}


def fetch_day_results(comp_id: int, day_id: int) -> dict:
    day_obj = _get_json(DAY_URL.format(comp_id=comp_id, day_id=day_id))
    return decode_day_results(day_obj, _pilots_by_id(comp_id))


def fetch_total_results(comp_id: int, day_id: int) -> dict:
    day_obj = _get_json(DAY_URL.format(comp_id=comp_id, day_id=day_id))
    return decode_total_results(day_obj, _pilots_by_id(comp_id))


def fetch_ranking_pilot(ranking_id) -> dict:
    payload = _get_json(RANKING_PILOT_URL.format(ranking_id=ranking_id))
    return decode_ranking_pilot(payload, ranking_id)
