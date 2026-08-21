# Ballerina EDIFACT @directory.upper@ @package.display@ library

## Overview

This package provides Ballerina record types and parser functions for the
@message.count@ UN/EDIFACT @directory.upper@ messages grouped under **@package.domain@**: @package.overview@

Each message is exposed as its own submodule, so a program only pulls in the
records for the messages it actually handles. The records and schemas are
generated from the UN/EDIFACT @directory.upper@ directory with the
[Ballerina EDI tool](https://central.ballerina.io/ballerina/edi) and are
envelope-aware: an interchange is parsed from `UNB` through `UNZ`, including the
`UNH`/`UNT` message header and trailer.

## Quick start

To use this library in your Ballerina application, import the package and the
submodules for the messages you handle.

### Step 1: Import the library

```ballerina
import ballerina/io;
import @package.org@/@package.name@;
import @package.org@/@package.name@.m@sample.message@;
```

### Step 2: Read an EDI message

Convert an EDIFACT interchange into a Ballerina record:

```ballerina
public function main() returns error? {
    string ediText = check io:fileReadString("@sample.message.lower@.edi");
    m@sample.message@:EDI_@sample.message@_@sample.message@ message =
        check @package.domain@:fromEdiString(ediText, @package.domain@:EDI_@sample.message@).ensureType();
    io:println(message);
}
```

### Step 3: Write an EDI message

Convert a Ballerina record back into an EDIFACT interchange:

```ballerina
string ediText = check @package.domain@:toEdiString(message, @package.domain@:EDI_@sample.message@);
```

`@package.domain@:getEDINames()` returns every message name this package supports.
`interchangeFromEdiString` and `interchangeToEdiString` give access to the full
`UNB`/`UNZ` interchange, and `headersFromEdiString` reads just the headers.

## Supported messages

| Message | Description | Module |
| ------- | ----------- | ------ |
@message.table@
