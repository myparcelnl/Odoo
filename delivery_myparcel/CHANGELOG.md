# Changelog

All notable changes to this project will be documented in this file.

## Known issues

### Open

* The module is currently still in development. New features/carriers are actively being implemented.

## 2025-07-18 (18.0.0.2.0)

### Added

* Integration for MyParcel carrier: PostNL
* Integration for MyParcel carrier: DHL Parcel Connect
* Multi-Collo package for PostNL
* Ability to select package types per carrier and select them in picking 'Put in Pack' while showing only available 
  options depending on the carrier
* Added insurance option for MyParcel shipments with ability to set a fixed or dynamic price for insurance

### Updated
* Contact information check for MyParcel shipments
* Access Denied error handling (using incorrect MyParcel API key)
* Use MyParcel's custom Track & Trace link instead of carrier specific url

## 2025-06-25 (18.0.0.1.2)

### Fixed

* Fixed issue when setting delivery method from webshop

## 2025-06-24 (18.0.0.1.1)

### Added

* Integration for MyParcel carrier: DHL For You
* Integration for MyParcel carrier: DHL Europlus
* Ability to fetch pricing information of a shipment directly from MyParcel
* Ability to set fixed prices for shipment, including setting-specific pricing, e.g. for Age Check (18+) or Signature
  request.
* Ability to create a shipment directly in MyParcel
* Option to generate a shipping label for a shipment, in 2 formats: A4 (includes option to set position) and A6
* Language support for English, Dutch

### Updated

*

### Fixed

*

### Removed

* n.v.t.
