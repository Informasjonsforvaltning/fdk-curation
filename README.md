# fdk-curation

Redaksjonelle markeringer av ressurser på [data.norge.no](https://data.norge.no).

## Datasett av høy verdi

[`high-value-dataset-types.csv`](high-value-dataset-types.csv) angir hvilke datasett som er markert som

| Kolonne               | Betydning                       |
|-----------------------|---------------------------------|
| `eu-hvd`              | Datasett av høy verdi (EU)      |
| `national-hvd`        | Nasjonalt datasett av høy verdi |
| `national-basic-data` | Nasjonale grunndata             |

Markeringene legges på datasettene som `dct:type` med koder fra
`https://data.norge.no/vocabulary/high-value-dataset-type`. Eventuelle markeringer med disse kodene fra utgiver blir
fjernet, slik at det bare er denne listen som gjelder.

### Format

```csv
fdkId,title,eu-hvd,national-hvd,national-basic-data
d40dbd5f-58f5-3a1c-96bc-8ecc2d712422,"Tittel, med komma",ja,nei,nei
```

- `fdkId` er id-en til datasettet på data.norge.no, den siste delen av adressen
  `https://data.norge.no/datasets/<fdkId>`.
- `title` er bare for å gjøre listen lesbar, og brukes ikke.
- Typekolonnene skal være `ja` eller `nei`.
- Skill kolonnene med komma, og sett anførselstegn rundt titler som inneholder komma.
- Hvert datasett skal bare stå én gang.

### Endringer

1. Rediger filen direkte på GitHub og foreslå endringen som en pull request.
2. Valideringen sjekker formatet, at ingen datasett står flere ganger, og at alle datasettene finnes på data.norge.no.
3. Når pull requesten er merget, blir endringen synlig på data.norge.no neste gang datasettet høstes.
