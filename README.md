# SWiface-PHP

**SWiface-PHP** is the server-side interface between the **Open Glider Network (OGN)** and
**Silent Wings Studio / SWviewer**. It is a set of PHP endpoints (thin wrappers, run by
Apache2) backed by Python scripts (all the real work) that:

- serve live and archived glider fixes to SWviewer using the
  [Silent Wings Tracking Protocol](https://github.com/swingsopen/swtracking/wiki/Tracking-Protocol)
  (protocol version `1.3`);
- convert competition data from **SoaringSpot**, **SGP / crosscountry.aero** and **Strepla**
  into the JSON/task files that Silent Wings and the FAI glider-tracking front ends consume;
- provide competition support utilities — IGC file rebuilding from FLARM records (SAR),
  FAI Sporting Licence lookup, OGN-tracker/FLARM pairing, and results extraction.

It provides real-time scoring data to [sgp.aero](http://sgp.aero).

---

## Contents

- [How it fits together](#how-it-fits-together)
- [Requirements](#requirements)
- [Silent Wings protocol endpoints](#silent-wings-protocol-endpoints)
- [Competition feed converters](#competition-feed-converters)
- [IGC / SAR utilities](#igc--sar-utilities)
- [FAI and OGN utilities](#fai-and-ogn-utilities)
- [Shared Python modules](#shared-python-modules)
- [Configuration](#configuration)
- [Database](#database)
- [Installation](#installation)
- [Directories and assets](#directories-and-assets)
- [Operational notes](#operational-notes)
- [Known rough edges](#known-rough-edges)
- [Documentation](#documentation)
- [Author and licence](#author-and-licence)

---

## How it fits together

```
  OGN APRS feed ──► collector (separate repo) ──► MySQL / SQLite3  (OGNDATA, GLIDERS, …)
                                                        │
  SoaringSpot API ─┐                                    │
  SGP  (crosscountry.aero) ─┼─► *2sws.py converters ──► cuc/*.json  *.tsk  *.csv
  Strepla (strepla.de) ─────┘                           │
                                                        ▼
                                  PHP endpoints (Apache2)  ──►  SWviewer / Silent Wings Studio
                                  event.php, trackpoints.php,
                                  eventgroups.php, gettrackerdata.php, …
```

Two independent data paths meet in this repo:

1. **Live tracking** — fixes previously collected from OGN into the database are served as
   Silent Wings JSON by `event.py` / `trackpoints.py` / `eventgroups.py` / `sgpgetfixes.py`.
2. **Competition metadata** — pilots, gliders, tasks and turnpoints are pulled from the
   scoring platforms by the `*2sws.py` converters and written as `.json` (Silent Wings event),
   `.tsk` (task) and `_filter.csv` (glidertracker filter) files into `cucFileLocation`
   (`cuc/` by default), where `event.py` and `eventgroups.py` pick them up.

The PHP layer never contains logic beyond argument sanitising: each endpoint `passthru()`s
`/usr/bin/python3 <script>.py` and echoes the output. The one exception is
`gettrackerdata.php`, which queries the database directly.

---

## Requirements

- Linux with **Apache2**, `mod_rewrite`, and CGI enabled (historically a Raspberry Pi;
  the MySQL variant runs against a NAS/NFS-hosted server).
- **PHP** with `mysqli` / `SQLite3` and `zlib` (for `gzip` compression of fix streams).
- **Python 3** with the packages in [`requirements.txt`](requirements.txt) — notably
  `pandas`, `geopy`, `pycountry`, `beautifulsoup4`, `requests`, `httpx`, `ogn_client`,
  `MySQL-python` (i.e. `MySQLdb`), `airportsdata`, `suntime`, `termcolor`, `GitPython`,
  `playwright`.
- A **MySQL/MariaDB** or **SQLite3** database populated by the OGN collector.

---

## Silent Wings protocol endpoints

These implement the tracking protocol consumed by SWviewer. All are GET unless noted.

| Endpoint | Query parameters | Backed by | Returns |
|---|---|---|---|
| `getprotocolinfo.php` | `username`, `cpassword`, `version` | — | `{version}1.3{/version}` plus server date/time |
| `getactivecontests.php` | — | — | Static contest descriptors (`QSGP`, `LIVE`) with site, lat/lon/alt |
| `getcontestinfo.php` | `contestname`, `date`, `username`, `cpassword` | `gencuc.py` (for `LIVE` + today) | Contest days, or the contents of `cuc/<contest><date>.cuc` |
| `gettrackerdata.php` | `contestname`, `querytype=getintfixes`, `trackerid`, `starttime`, `endtime`, `compression` | direct SQL on `OGNDATA` | CSV fixes `flarmid,YYYYMMDDHHMMSS,lat,lon,alt,1`, optionally gzipped |
| `getbannerinfo.php` | — | — | Banner image list |
| `event.php` | `eventid` | `event.py` | Silent Wings event JSON (turnpoints + tracks) for one event |
| `eventgroups.php` | — | `eventgroups.py` | Event list built by scanning `cuc/` for `.cuc` / `.json` files |
| `trackpoints.php` | `trackid`, `begin` | `trackpoints.py` | `{"trackId":…, "live":…, "track":[{"t":ts,"e":lon,"n":lat,"a":alt}, …]}` |
| `sgpgetfixes.php` | `id`, `since`, `compression` | `sgpgetfixes.py` | Fixes in the SGP scoring JSON format, optionally gzipped |
| `info.php` | — | — | `phpinfo()` (not tracked; see `.gitignore`) |

`eventid` is of the form `<4-char initials><YYYY>MMDD…`; the first four characters select the
event kind (`LIVE` for the live feed, otherwise a competition prefix such as `QSGP`), and
characters 7–12 carry the date used to query the fixes table.

---

## Competition feed converters

Each converter has an HTML form, a PHP wrapper and a Python implementation.

| Source | Form | PHP | Python | Arguments |
|---|---|---|---|---|
| SoaringSpot (`api.soaringspot.com`) | `soa2sws.html` | `soa2sws.php` (POST `class`, `indexday`) | `soa2sws.py` | `indexday [class]` |
| SGP (`crosscountry.aero`) | `sgp2sws.html` | `sgp2sws.php` (POST `compid`, `indexday`) | `sgp2sws.py` | `compid indexday [ip] [print]` |
| Strepla (`strepla.de`) | `str2sws.html` | `str2sws.php` (POST `compid`, `indexday`) | `str2sws.py` | `compid indexday` |

**Index day** is `0` for the first/most recent day, `1`, `2`, … for previous days;
`sgp2sws.py` also accepts `today`. `sgp2sws.py 0` (or `--list`) prints the list of SGP
competitions instead of converting one.

Output files, written to `config.cucFileLocation`:

| File | Description |
|---|---|
| `<Initials><YYYYMMDD>[-<class>].json` | Silent Wings event: turnpoints + per-pilot tracks (pilot name, CN, country, aircraft, registration, 3D model, ribbon colours, portrait URL) |
| `<Initials><YYYYMMDD>[-<class>].tsk` | Task file; a `<class>-latest.tsk` symlink/copy is kept per class |
| `<class>_filter.csv` / `competitiongliders.csv` | `ID,CALL,CN,TYPE,INDEX` filter list for glidertracker.org |
| `competitiongliders.lst` | Flat list of the competing gliders |

SoaringSpot access is HMAC-signed: credentials come from `config.clientid` / `config.secretkey`,
or, when those are empty, from `SoaringSpot/clientid` and `SoaringSpot/secretkey`
(the `SoaringSpot/` directory is git-ignored). SoaringSpot credentials are issued per
competition and are not valid for other competitions.

Related:

- `soa2pil.py` — extract pilot information from SoaringSpot for FlyTool.
- `ccucxtocuc.py` — convert SeeYou `.cucx` files into the pseudo-`.cuc` format Silent Wings uses.
- `gencuc.py` — scan the database for gliders currently flying and build a live `.cuc` file
  (invoked by `getcontestinfo.php` for the `LIVE` contest).
- `show_competition.py` / `sgp_api.py` — SGP REST client; `sgp_api.py` decodes the terse
  single-letter API keys into readable dicts (events, comp + pilots + days, day task, FAI
  ranking entry) and its `decode_*` functions are pure, so they can be tested against fixtures.
- `gen_swsconfig.py` — build a per-venue `SWSconfig.<location>` from an SGP competition
  (`--list`, `--comp-id`, `--config-dir`) and point `SWSconfig.ini` at it via symlink.
- `SSextractresults.py` / `SSextractresults.php` / `.html` — scrape a SoaringSpot competition
  (`-c <competition-slug>`) and write the final results to CSV.

---

## IGC / SAR utilities

FLARM radio messages recorded inside other pilots' IGC files (`LLXV FLARM…` records) can be
used to reconstruct the track of a glider whose own logger file is missing — the basis of the
search-and-rescue tooling here.

| Script | Purpose |
|---|---|
| `SAR4comp.py` (`SAR4comp.php`, `SAR4comp.html`) | Front end for all three sources: `-t SOA\|SGP\|DIR`, `-f FLARMID`, `-r registration`, `-g sgpid`, `-c clientid`, `-s secretkey`, `-i indexday`, `-w` (web output). Rebuilds the flight and links to `cunimb.net/igc2map.php` |
| `soa2fil.py` / `soa2filfuncs.py` | Download every IGC file of a SoaringSpot day; `soa2fil.py <indexday> [-e FLARMID]` extracts the FLARM traces |
| `sgp2fil.py` / `sgp2filfuncs.py` | Same for an SGP competition: `sgp2fil.py <compid> <indexday> [-e FLARMID] [print]` |
| `dir2fil.py` / `dir2filfuncs.py` | Same over a local directory of IGC files (`SARpath/IGCfiles/DIR/` → `…/TMP/`) |
| `genIGC.py` | Rebuild a valid IGC file from collected FLARM messages; filters implausible fixes using `DISTHOME`, `DIFFALT`, `DIFFAVG` |
| `buildigc.sh` | Shell wrapper: `buildigc.sh <day> <flarmid> <name>` — greps the FLARM records and pipes them through `genIGC.py` |
| `soa2fil.sh`, `sgp2fil.sh` | Batch a whole competition, one run per day index |
| `igc2geo.py` | Convert an `.IGC` file to JSON |

---

## FAI and OGN utilities

| Script | Purpose |
|---|---|
| `SearchFAISL.py` (`.php`, `.html`) | Search/validate a pilot's **FAI Sporting Licence** on the FAI extranet: `-c IOC-country`, `-n surname`, `-f firstname`, `-s licence-number`, `-w` |
| `validate_fai_sl.py` | The underlying FAI extranet client (licences per country, full licence details); uses `config.FAIPWD` |
| `iso2ioc.py` | ISO 3166-1 alpha-3 → IOC country-code mapping (mismatches only) |
| `pairtrk.py` (`pairtrk.php`, `pairtrkadd.html`) | Pair an OGN tracker with the FLARM on the same glider so the two appear as one device. Actions: `list`, `add`, `update`, with `trk`, `flarmid`, `owner`, `deleteyn`, `active` (table `TRKDEVICES`) |
| `pairsynch.php` | `?synch=synch` — replicate `TRKDEVICES` between servers with `pt-table-sync` |
| `ognddbfuncs.py` | OGN DDB lookups (registration, CN, aircraft type, FLARM id) with host failover |
| `ogntfuncs.py`, `flarmfuncs.py` | OGN-tracker ↔ FLARM pairing tables and `GLIDERS` lookups |

---

## Shared Python modules

| Module | Contents |
|---|---|
| `config.py` | **Generated** — see [Configuration](#configuration) |
| `parserfuncs.py` | OGN APRS parsing helpers, airport/sunrise data (`airportsdata`, `suntime`) |
| `geofuncs.py` | Geodesy: degrees↔DMS, geodesic distances, coordinate line conversion |
| `dtfuncs.py` | Timezone-aware / naive UTC helpers |
| `gistfuncs.py` | GitHub Gist publishing, plus `obscure()` / `unobscure()` (zlib + base64) used for stored passwords |
| `simplehal.py` | Minimal HAL+JSON document walker for the SoaringSpot API |
| `dummyfile.py` | `fixcoding()` — strip accents/non-ASCII from names |
| `web_scraper.py` | `WebScraper` — static (requests/BeautifulSoup) and dynamic scraping |
| `kpilot.py`, `kglider.py`, `ksta.py` | Local tables of known pilots, gliders to display, and OGN receiver stations |

---

## Configuration

Nothing is configured by editing Python. The single source of truth is an INI file,
`$CONFIGDIR/SWSconfig.ini` (default `CONFIGDIR=/etc/local/`):

```bash
python3 genconfig.py     # reads SWSconfig.ini (+ configtail.txt) → config.py and config.php
```

`genconfig.py` writes both `config.py` (imported by every Python script) and `config.php`
(included by the PHP that needs credentials), then `chmod 740` / `chown :www-data` on them.
Passwords and the Gist token are stored obscured (`gistfuncs.obscure`) and read back with
`unobscure()`. Both generated files are git-ignored. `configtail.template` is a sample of the
`configtail.txt` tail (accent-stripping helper plus the fallback event/turnpoint/track
definitions used when no JSON file is found).

`SWSconfig.ini` keys, by section:

**`[server]`** — `cucFileLocation`, `DBpath`, `SARpath`, `MySQL`, `DBhost`, `DBname`,
`DBtable`, `SQLite3`, `DBuser`, `DBpasswd`, `DBuserread`, `DBpasswdread`, `Initials`,
`SWSserver`, `TPTserver`, `DDBhost`, `DDBport`, `DDBurl1`, `DDBurl2`, `GIST`, `GIST_USER`,
`GIST_TOKEN`, `clientid`, `secretkey`, `OGNTRACKERS`, `DISTHOME`, `DIFFALT`, `DIFFAVG`,
`FAIPWD`.

**`[location]`** — `location_name`, `location_latitude`, `location_longitud`, `eventname1`,
`eventname2`, `eventdesc1`, `eventdesc2`, `PicPilots`.

Only `DBpath`, `MySQL`, `DBhost`, `DBuser`, `DBpasswd`, `DBname`, `SQLite3`, `Initials` and
the `[location]` names/descriptions are mandatory; the rest have defaults.

---

## Database

Both back ends are supported and selected by `config.MySQL`:

- **MySQL/MariaDB** — `MySQLdb.connect(host=DBhost, user=DBuserread, passwd=…, db=DBname)`.
- **SQLite3** — the file `DBpath + SQLite3` (e.g. `/nfs/OGN/SWdata/SWiface.db`), opened
  read-only.

Tables read by this repo (populated by the OGN collector, not by these scripts):

| Table | Used for |
|---|---|
| `OGNDATA` (name from `DBtable`) | The fixes: `idflarm, date (YYMMDD), time (HHMMSS), latitude, longitude, altitude` |
| `GLIDERS` | `idglider, registration, cn, type, flarmtype` |
| `TRKDEVICES` | OGN-tracker ↔ FLARM pairing (`id, flarmid, registration`) |
| `CONTEST`, `CONTESTANT`, `PILOT`, `POINT`, `LOCATION` | Competition metadata mirrored from the scoring platform |

---

## Installation

```bash
# 1. Get the code into the Apache document root
cd /var/www/html
git clone https://github.com/acasadoalonso/SWiface-PHP.git SWS
cd SWS

# 2. Python dependencies
pip install -r requirements.txt

# 3. Working directories
mkdir -p cuc cucfiles
sudo chown -R $USER:www-data . cuc cucfiles

# 4. Configuration
sudo vi /etc/local/SWSconfig.ini      # see the Configuration section
cp configtail.template configtail.txt # adjust the fallback event/turnpoints if needed
python3 genconfig.py                  # → config.py and config.php

# 5. Competition data (pick the one that applies)
cp ../*.cucx cucfiles/ && (cd cucfiles && unzip '*.cucx')
python3 ccucxtocuc.py                 # SeeYou .cucx  → .cuc
python3 soa2sws.py 0                  # SoaringSpot   → .json/.tsk
python3 sgp2sws.py <compid> today     # SGP           → .json/.tsk

# 6. Local pilot/glider tables, if you use them
vi kpilot.py kglider.py

sudo service apache2 restart
```

For SoaringSpot without credentials in the INI file, create `SoaringSpot/clientid` and
`SoaringSpot/secretkey` in the repo root (git-ignored).

The bundled `.htaccess` enables `mod_rewrite` (so `event` resolves to `event.php`), runs
`.py` as CGI, sets `Access-Control-Allow-Origin: *`, and requires HTTP Basic auth against
`/etc/apache2/.htpasswd`.

---

## Directories and assets

| Path | Contents |
|---|---|
| `cuc/` | Generated `.cuc` / `.json` / `.tsk` / `.csv` per event and day, plus the `LIVEhdr.txt` / `LIVEtail.txt` / `LIVEtail2.txt` templates used to assemble live `.cuc` files |
| `cucfiles/` | Original SeeYou `.cucx` files (git-ignored) |
| `doc/` | Protocol and API documentation (see below) |
| `banners/`, `gif/` | Logos and banners served to SWviewer |
| `tptextures/` | Start/finish/turnpoint textures used in the 3-D rendering |
| `SoaringSpot/`, `LT24/`, `PilotImages/`, `pic/`, `utils/`, `files/` | Site-local, git-ignored |

---

## Operational notes

- **Auto-deploy** — `ogn.pull.php` is a GitHub *push* webhook: it runs `git pull origin master`,
  fixes permissions and touches `UPDATED.by.GIT`.
- **Vendored modules** — `sscommit.sh` copies the shared `*funcs.py` and `ksta.py` from the
  author's `/nfs/OGN/src` tree into the repo, regenerates `requirements.txt` with `pipreqs`,
  and pushes to both the `origin` and `glidernet` remotes. `sslink.sh` symlinks them instead,
  for development on the source machine.
- **Quick check** — `test.sh` fetches the SGP event list (`data.crosscountry.aero/public/get/events`).
- **CI** — `.github/workflows/label.yml` labels pull requests by modified path.

---

## Known rough edges

Worth knowing before you deploy or change things:

- `getflarm.py` is imported by `soa2filfuncs.py`, `sgp2filfuncs.py` and `dir2filfuncs.py` but
  is **git-ignored and not in the repo**; the IGC/FLARM extraction path will not run without it.
- `gettrackerdata.php` carries hard-coded database host/user/password and a hard-coded
  `Europe/Madrid` timezone, and its `$mysql` flag is commented out — it therefore always takes
  the SQLite3 branch. It does not use `config.php`.
- `getactivecontests.php` and `getbannerinfo.php` return static strings (a 2016 contest and
  fixed banner paths) rather than reading the configuration.
- `config.bkup`, a committed sample configuration that carried a GitHub token and obscured DB
  passwords, has been deleted — but it remains in the git history, so those credentials must be
  treated as exposed and rotated. `config.py` is generated by `genconfig.py`; do not commit it.
- `soa2fil.py` references `FalrmID` in its 9-character FLARM-ID branch (typo for `FlarmID`),
  which raises `NameError` for `ICAxxxxxx`-form ids.
- `requirements.txt` is generated by `pipreqs` and lists `GitPython` and `pyOpenSSL` twice
  with different versions.
- `setup.py` is a one-line placeholder; the project is not installable as a package.

---

## Documentation

In [`doc/`](doc):

| File | Contents |
|---|---|
| `README.SWS.PHP.INTERFACE`, `INSTALL.SWS.PHP.INTERFACE` | The original interface notes and install steps |
| `SWS interface for real time scoring.pdf` | Real-time scoring interface specification |
| `SGP API.txt`, `sgpcall.txt`, `sgp_json_specs.txt`, `sgpoutput.txt` | SGP REST API notes, sample calls and payloads |
| `Ranking list REST api v.0.23.pdf` | FAI ranking-list REST API |
| `LECD.doc.json` | Sample event document (La Cerdanya) |
| `COPYING` | Licence |

External references:

- [Silent Wings Tracking Protocol](https://github.com/swingsopen/swtracking/wiki/Tracking-Protocol)
  and the [Silent Wings wiki](http://wiki.silentwings.no/index.php?title=Tracking_Protocol)
- [SGP — Sailplane Grand Prix](http://sgp.aero) · [crosscountry.aero](https://www.crosscountry.aero)
- [SoaringSpot](https://www.soaringspot.com) · [Open Glider Network](https://www.ogn.org/)

---

## Author and licence

Angel Casado — `acasado (at) acm.org`. Licence: **GNU GPL v2** — see [`doc/COPYING`](doc/COPYING).

Bug reports and questions: please open an issue on
[GitHub](https://github.com/acasadoalonso/SWiface-PHP/issues).
