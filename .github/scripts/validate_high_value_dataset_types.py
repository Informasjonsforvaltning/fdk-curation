import csv
import re
import sys
import time
import urllib.error
import urllib.request

EXPECTED_HEADER = ["fdkId", "title", "eu-hvd", "national-hvd", "national-basic-data"]
VALUES = {"ja", "nei"}
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
DATASET_API = "https://resource.api.fellesdatakatalog.digdir.no/v1/datasets/"
ATTEMPTS = 3
RETRY_DELAY_SECONDS = 5


def dataset_exists(fdk_id):
    for attempt in range(1, ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(DATASET_API + fdk_id, timeout=30) as response:
                return response.status == 200
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return False
            if attempt == ATTEMPTS:
                raise
        except urllib.error.URLError:
            if attempt == ATTEMPTS:
                raise
        time.sleep(RETRY_DELAY_SECONDS)


def validate(path, check_exists):
    errors = []
    with open(path, encoding="utf-8-sig", newline="") as file:
        rows = list(csv.reader(file))

    if not rows or rows[0] != EXPECTED_HEADER:
        found = ",".join(rows[0]) if rows else "(tom fil)"
        return [f"Linje 1: overskriften må være «{','.join(EXPECTED_HEADER)}», fant «{found}»"]

    seen = {}
    for line, row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue
        if len(row) != len(EXPECTED_HEADER):
            errors.append(f"Linje {line}: forventet {len(EXPECTED_HEADER)} kolonner, fant {len(row)}. Husk anførselstegn rundt titler med komma")
            continue

        fdk_id = row[0].strip()
        if not UUID.match(fdk_id):
            errors.append(f"Linje {line}: «{fdk_id}» er ikke en gyldig fdkId")
        elif fdk_id in seen:
            errors.append(f"Linje {line}: fdkId {fdk_id} finnes allerede på linje {seen[fdk_id]}")
        else:
            seen[fdk_id] = line

        for code, value in zip(EXPECTED_HEADER[2:], row[2:]):
            if value.strip().lower() not in VALUES:
                errors.append(f"Linje {line}: «{code}» må være ja eller nei, fant «{value}»")

    if check_exists:
        for fdk_id, line in seen.items():
            if not dataset_exists(fdk_id):
                errors.append(f"Linje {line}: fant ikke datasett med fdkId {fdk_id} på data.norge.no")

    return errors


if __name__ == "__main__":
    errors = validate(sys.argv[1], "--skip-exists" not in sys.argv)
    for error in errors:
        print(f"::error file={sys.argv[1]}::{error}")
    if errors:
        sys.exit(1)
    print("OK")
