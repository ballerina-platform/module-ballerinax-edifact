# Ballerina EDIFACT libraries

[![Build](https://github.com/ballerina-platform/edifact/actions/workflows/build.yml/badge.svg)](https://github.com/ballerina-platform/edifact/actions/workflows/build.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## Overview

This repository holds the EDI schemas for the UN/EDIFACT **D03A** directory and
publishes them to Ballerina Central as seven libraries, one per business domain.
Each library provides Ballerina record types and parser functions for its
messages, so an EDIFACT interchange can be read into typed records and written
back out.

| Package | Messages | Covers |
| ------- | -------- | ------ |
| [`ballerinax/edifact.d03a.finance`](https://central.ballerina.io/ballerinax/edifact.d03a.finance) | 32 | Payment orders, credit and debit advices, direct debits, financial statements, balance-of-payments reporting, invoicing, VAT and tax control |
| [`ballerinax/edifact.d03a.logistics`](https://central.ballerina.io/ballerinax/edifact.d03a.logistics) | 28 | Forwarding and multimodal transport instructions, bookings and status reports, freight costs and rates, dangerous goods notifications, cargo handling |
| [`ballerinax/edifact.d03a.manufacturing`](https://central.ballerina.io/ballerinax/edifact.d03a.manufacturing) | 17 | Product service and project planning, quality and safety data, utilities master data and time series, metered consumption, accounting entries |
| [`ballerinax/edifact.d03a.retail`](https://central.ballerina.io/ballerinax/edifact.d03a.retail) | 23 | Product data and inquiries, requests for quote, pricing history, returns, reservations, insurance policy administration and reinsurance |
| [`ballerinax/edifact.d03a.services`](https://central.ballerina.io/ballerinax/edifact.d03a.services) | 29 | Insurance premiums and claims, job orders and applications, payroll deductions, medical prescriptions and reports, stowage and berth management |
| [`ballerinax/edifact.d03a.shipping`](https://central.ballerina.io/ballerinax/edifact.d03a.shipping) | 34 | Container announcement, release, gate-in/gate-out, discharge/loading and stuffing/stripping, bayplans, customs declarations and responses |
| [`ballerinax/edifact.d03a.supplychain`](https://central.ballerina.io/ballerinax/edifact.d03a.supplychain) | 29 | Purchase orders and responses, delivery schedules and just-in-time calls, despatch and receiving advices, inventory reports, documentary credit |

Each message is a separate submodule, so a program only pulls in the records for
the messages it actually handles. The records and schemas are generated from the
UN/EDIFACT D03A directory with the
[Ballerina EDI tool](https://central.ballerina.io/ballerina/edi) and are
envelope-aware: an interchange is parsed from `UNB` through `UNZ`, including the
`UNH`/`UNT` message header and trailer.

## Quick start

To use a library in your Ballerina application, import the package and the
submodules for the messages you handle.

### Step 1: Import the library

```ballerina
import ballerina/io;
import ballerinax/edifact.d03a.supplychain;
import ballerinax/edifact.d03a.supplychain.mORDERS;
```

### Step 2: Read an EDI message

Convert an EDIFACT interchange into a Ballerina record:

```ballerina
public function main() returns error? {
    string ediText = check io:fileReadString("orders.edi");
    mORDERS:EDI_ORDERS_ORDERS message =
        check supplychain:fromEdiString(ediText, supplychain:EDI_ORDERS).ensureType();
    io:println(message);
}
```

### Step 3: Write an EDI message

Convert a Ballerina record back into an EDIFACT interchange:

```ballerina
string ediText = check supplychain:toEdiString(message, supplychain:EDI_ORDERS);
```

`supplychain:getEDINames()` returns every message name the package supports.
`interchangeFromEdiString` and `interchangeToEdiString` give access to the full
`UNB`/`UNZ` interchange, and `headersFromEdiString` reads just the headers.

## Build from the source

### Prerequisites

1. JDK 21 and Python 3.9 or later.
2. [Ballerina Swan Lake](https://ballerina.io/downloads/). The version is pinned
   as `ballerinaLangVersion` in [`gradle.properties`](gradle.properties) and is
   what the packages declare as their `distribution`.

The EDI tool version is pinned as `ediToolVersion` in the same file and is
pulled by the build.

### Build the libraries

```bash
./gradlew build
```

This generates every library from the committed EDI schemas into
`build/packages`, packs each one, and fails if the committed schemas were not
post-processed. No generated source is committed.

Useful tasks:

| Task | Description |
| ---- | ----------- |
| `./gradlew build` | Generate, pack and validate everything |
| `./gradlew generateLibraries` | Generate all seven packages without packing |
| `./gradlew packD03aFinance` | Generate and pack a single package |
| `./gradlew validateSchemas` | Check the committed schemas are post-processed |
| `./gradlew publishToCentral` | Push every package to Ballerina Central |
| `./gradlew regenSchemas -PediArchive=d03a.zip` | Regenerate the committed schemas |

Package metadata — keywords, licence, authors, repository — lives in
[`metadata/packages.json`](metadata/packages.json), and the `Ballerina.toml` and
`README.md` templates live under
[`build-config/resources`](build-config/resources). `bal edi libgen` does not emit
that metadata and overwrites `Ballerina.toml` on every run, so the build
re-applies it after each generation.

## Regenerate the schemas

The schemas under `d03a/` are generated from the UN/EDIFACT D03A release archive.

1. Download `d03a.zip` from the
   [UN/EDIFACT directories download page](https://unece.org/trade/uncefact/unedifact/download).
   The site is behind a bot check, so the archive has to be fetched with a
   browser rather than `curl`.
2. Regenerate:

   ```bash
   ./gradlew regenSchemas -PediArchive=d03a.zip
   ```

The task converts the archive, copies each message over the package directory
that already owns it — the domain grouping is a curation decision recorded by the
directory layout — and then runs `scripts/postprocess_schemas.py`.

That script repairs three defects in the converter output that otherwise make the
generated libraries fail to compile; see its docstring and
[ballerina-library#9065](https://github.com/ballerina-platform/ballerina-library/issues/9065)
for the details. `./gradlew build` fails if the committed schemas are not
post-processed.

`convertEdifactSchema` exits non-zero after emitting all 192 messages because it
also picks up the interactive message directory and fails on `RESRSP`; the 192
files it wrote first are complete, and `regenSchemas` tolerates that exit code.

## Contribute to Ballerina

As an open-source project, Ballerina welcomes contributions from the community.

For more information, go to
[the contribution guidelines](https://github.com/ballerina-platform/ballerina-lang/blob/master/CONTRIBUTING.md).

## Code of conduct

All the contributors are encouraged to read the
[Ballerina Code of Conduct](https://ballerina.io/code-of-conduct).

## Useful links

- Chat live with us via our [Discord server](https://discord.gg/ballerinalang).
- Post all technical questions on Stack Overflow with the
  [#ballerina](https://stackoverflow.com/questions/tagged/ballerina) tag.
