## Overview

UN/@package.display.name@ group EDI parser: reads and writes the @message.count@ messages covering @package.overview@

[UN/EDIFACT](https://unece.org/trade/uncefact/introducing-unedifact) is the
United Nations standard for electronic data interchange, used to exchange
business documents such as orders, invoices and despatch advices between trading
partners.

### Key Features

- Typed records for all @message.count@ messages in the **@package.domain@** group, each in its own submodule, so a program only pulls in the records for the messages it handles.
- Envelope-aware parsing and serialization: an interchange is read from `UNB`
  through `UNZ`, including the `UNH`/`UNT` message header and trailer.
- Round-trips in both directions — EDI text to records, and records back to
  conformant EDI text with the `UNT` segment count recomputed.
- Generated from the UN/EDIFACT @directory.upper@ directory with the
  [Ballerina EDI tool](https://central.ballerina.io/ballerina/edi), so the
  records follow the published specification.

## Quickstart

To use the `@package.name@` package in your Ballerina application, modify the `.bal` file as follows:

### Step 1: Import the module

Import the package and the submodules for the messages you handle.

```ballerina
import ballerina/io;
import @package.org@/@package.name@;
import @package.org@/@package.name@.m@sample.message@;
```

### Step 2: Read an EDI message

Convert an EDIFACT interchange into a Ballerina record.

```ballerina
public function main() returns error? {
    string ediText = check io:fileReadString("@sample.message.lower@.edi");
    m@sample.message@:EDI_@sample.message@_@sample.message@ message =
        check @package.domain@:fromEdiString(ediText, @package.domain@:EDI_@sample.message@).ensureType();
    io:println(message);
}
```

`@package.domain@:getEDINames()` returns every message name this package
supports. `interchangeFromEdiString` gives access to the full `UNB`/`UNZ`
interchange, and `headersFromEdiString` reads just the headers.

### Step 3: Write an EDI message

Convert a Ballerina record back into an EDIFACT interchange.

```ballerina
string ediText = check @package.domain@:toEdiString(message, @package.domain@:EDI_@sample.message@);
```

Use `interchangeToEdiString` to write the full interchange rather than the
message body alone.

### Step 4: Run the Ballerina application

```bash
bal run
```

## Supported messages

| Message | Description | Module |
| ------- | ----------- | ------ |
@message.table@
