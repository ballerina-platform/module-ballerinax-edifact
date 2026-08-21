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

1. [Ballerina Swan Lake](https://ballerina.io/downloads/) 2201.13.3 or later.
2. The EDI tool:

   ```bash
   bal tool pull edi:2.2.0
   ```

3. Python 3.9 or later, for the scripts under `scripts/`.

### Generate and build a package

```bash
bal edi libgen -p ballerinax/edifact.d03a.supplychain -i d03a/supplychain -o target
python3 scripts/apply_package_metadata.py target/edifact.d03a.supplychain supplychain 1.0.0
cd target/edifact.d03a.supplychain && bal pack
```

`apply_package_metadata.py` fills in the keywords, icon, licence, authors and
repository from [`metadata/packages.json`](metadata/packages.json), which
`bal edi libgen` does not emit and overwrites on every run.

## Regenerate the schemas

The schemas under `d03a/` are generated from the UN/EDIFACT D03A release archive.

1. Download `d03a.zip` from the
   [UN/EDIFACT directories download page](https://unece.org/trade/uncefact/unedifact/download).
   The site is behind a bot check, so the archive has to be fetched with a
   browser rather than `curl`.
2. Convert it, then post-process and redistribute the output:

   ```bash
   bal edi convertEdifactSchema -v d03a -i d03a.zip -o /tmp/d03a
   # copy each message into the package directory that already owns it
   for f in /tmp/d03a/*.json; do
     cp "$f" "$(find d03a -name "$(basename "$f")")"
   done
   python3 scripts/postprocess_schemas.py d03a
   ```

`postprocess_schemas.py` repairs three defects in the converter output that
otherwise make the generated libraries fail to compile; see the script's
docstring for the details. Run it after every regeneration — the build workflow
fails if the committed schemas are not post-processed.

The domain grouping is a curation decision recorded by the directory layout, so
regenerated messages are copied over their existing location rather than into a
flat directory. `convertEdifactSchema` exits non-zero after emitting all 192
messages because it also tries to convert a bogus `RESRSP` entry; the 192 files
it wrote before that are complete.

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
