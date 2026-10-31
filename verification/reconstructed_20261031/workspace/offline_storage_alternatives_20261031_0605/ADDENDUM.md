# Bounded first-prototype alternatives — 2026-10-31
Read-only decision study; no adoption, firmware/PCB edits, purchase or supplier outreach. Companion to offline_storage_architecture_20261031_0600/REPORT.md. Accuracy/safety unchanged;24h remains cost-prioritized unmet target for smaller capacities, not a requirement to buy unavailable512MiB.

## One shortlisted SKU per smaller density
Prices below are from opened supplier pages, not search snippets. Catalog views may be cached and vary by location; not reserved or checkout-confirmed. USD retained without invented CNY conversion. All added component/assembly costs must still fit totalCNY760 for two complete pens.

|Class|ShortlistedSKU and opened supplier observation|Two storage ICs / actual outlay|Qualification|
|---|---|---|---|
|128MiB NAND|W25N01KVZEIR, LCSC C22472329:22,864stock; minimum/multiple8;USD6.628each at8|Nominal two consumedUSD13.256, but actual minimum orderUSD53.024 for8; do NOT budget13.256|Current manufacturer massproduction; no longevity commitment. No verified two-piece pack offer; plain URL lacks price while opened variant exposes it. Conditional supply evidence, not purchase-ready|
|256MiB NAND|W25N02KVZEIR TR, DigiKey:7,970stock;USD24.38qty1 cuttape|USD48.76 for2|Manufacturer now NRND despite distributorActive. Not recommended as default new-design choice|
|64MiB NOR|W25Q512JVEIQ, DigiKey:983stock;USD21.19qty1 tube|USD42.38 for2|DistributorActive; official datasheet available. No manufacturer current lifecycle confirmation obtained; verify before adoption. Simpler storage driver, but not demonstrated affordable|

Add twoTCA6408ARGTR at previously openedDigiKeyUSD1.66each: total storage+expander only respectivelyUSD56.344(actualMOQ8),USD52.08,USD45.70. Excludes taxes, passives, reset circuitry, board/FPC delta, assembly/inspection and paid validation. No existing cost headroom has been proven. Avoid custom-reel fee by quoting ordinary cuttape where applicable; no order placed.

Rejected from shortlist:128MiB oldGV offers may be stocked but show discontinued status; do not silently adopt.512MiB currentLV remains no verified immediate two-piece supply,24–36week catalog leadtime. SmallerKV256 likewise cannot be called current merely because stocked.

## Device constraints verified against manufacturer sources
128MiB W25N01KVZEIR:2.7–3.6V,SPI/Dual/Quad,8x6mmSON,2048Bmain+64Bspare page,4-bit built-inECC,buffer-read default,manufacturerP(massproduction). SourceM1.
256MiB W25N02KVZEIR:2.7–3.6V,SPI/Dual/Quad,8x6mmSON,2048Bmain+128Bspare page,8-bit built-inECC,buffer-read default,manufacturerN(NRND). SourceM2.
64MiB W25Q512JV:EIQ is8x6mmWSON,2.7–3.6V,1–256Bpageprogram and4KiBsector erase; driver must handle page-boundary wrap and address space beyond16MiB using correct4-byte addressing. Do not assume NAND-style built-inECC; retain softwareCRC/readback. SourceM3.
NAND must obey exact part's ECC/status, badblock, sequential/partial-program rules; no copy-paste of512MiB4KiBpage assumptions. Spare bytes not counted as usercapacity. Exact package drawings/height and solder landpatterns remain prerequisites; matching8x6body does not prove pin-compatible or mechanically placed. All require same unresolvedSPI pin/reset redesign; smallercapacity does not freeGPIO.

## Exact conservative capacity comparison
Canonical records remain64B, including exactmicrometre coordinates and64-bit microsecond timestamps plus typed quality/contact/fault/page evidence. To respect native2KiB NAND pages, adapt framing to64Bheader +30*64Brecords +64Bfooter per2048Bpage.512MiB uses62records per4096Bpage. NOR uses logical4096Bcontainers (not256Bphysical programmingpages) with62records and128Bframing; writes split safely across physicalpages.

Common budget assumptions:
-25%totalcapacity withheld for metadata,badblocks,wear/reclaim,tornwrites,growth; unboundedfailures excluded.
-Extraevent allowance E=ceil(N*800000/5184000),i.e.15.4321%ofobservations, matching earlier24hproposal; includescontinuations/sessionrecords. This is a sizing ratio, NOTpermissiontodrop/rate-limit events.
-Up to1024sessionboundary slack losses: nativecontainerrecordcount minus1 each. Sessionrecords themselves count withinE. Unlimitedreboots/idletime not guaranteed.
-60observations/s. No compression assumed. Nmax solves N+E <= recordpositions-session_slack.

|Capacity/type|Dataregion after25%reserve|Container/records|Recordpositions|Session-slack allowance|Nmax observations|Duration hours @60Hz|
|---|---:|---:|---:|---:|---:|---:|
|64MiB NOR|48MiB|4096/62|761856|62464|605890|2.8050463|
|128MiB NAND|96MiB|2048/30|1474560|29696|1251700|5.7949074|
|256MiB NAND|192MiB|2048/30|2949120|29696|2529126|11.7089167|
|512MiB NAND reference|384MiB|4096/62|6094848|62464|5225915|24.1940509|

These are exact mathematical conditional envelopes, not measured physical guaranteed durations. Moreevents/failures shorten them; lower observed event/session usage lengthens them. Without anyextras/slack, afterreserve/framing ceilings are3.5271/6.8267/13.6533/28.2169h respectively; do not advertise those asguarantees.

Compression may extend duration but no actual tracecodec measurements exist. No compressed24h claim for64/128/256MiB. Record all existing validsamples exactly; persist newlyrequired typed diagnostics rather than zeroingthem. Link no strokes across loss.

## Recommendation for a realistic first prototype
Do not redesign around unavailable512MiB or selectNRND256MiB just to approach24h. The present evidence supports two staged choices:
1. Cost-first engineering prototype: retain internal hardware while validating complete capture/coordinate/transport/receiver-v2 pipeline and exactlosslesscodec; declare17.64minrootceiling honestly, synchronizefrequently, and keep24htargetopen. This avoidsnewstorageparts but is NOT an acceptable24hfinalclaim and cannot be silently substituted for userexpectation.
2. If externalretention is needed in the first physicalprototype and the fullbudget can afford it,64MiB NOR is the simplest of these verifiedtwo-piece offers to investigate:approximately2.8hconservativeuncompressed envelope, knownNORprogramming model, andUSD45.70storage+expanders forbothpens before otherdelta. It still needs reset/pin redesign andcapacity-safeACKsegmentreclaim; not a drop-in. Calling itaffordable is premature.128MiB NAND givesapproximately5.8h but currentverifiedMOQ8 makesupfrontICoutlayhigher and addsNANDcomplexity; it becomes moreattractive only if a credible smallpackoffer is established. No more sourcing search in thisboundedtask.

Prefer provingcostedplacement andfirmwarecomplexity over unverifiedcompression promises. If completebudget cannot fit externalstorage, the userdecision would be whether thefirstprototype may use explicitly disclosed shorterofflinecapacity/frequent sync while retaining24h aslatercostoptimization goal; never offer reducedcoordinateprecision or silently deleteevents. If24h becomes mandatorywithoutcompression, revisitavailable512MiB-class sourcing or totalbudget/designscope; do not use the current unavailablepart asdefault.

## Sources opened
P128 https://www.lcsc.com/product-detail/C22472329.html?is_substitute=1&original_product_code=C6750725&original_unit_price=2.5696 (actual tableUSD6.628,notURLparameter2.5696;MOQ8)
P256 https://www.digikey.com/en/products/detail/winbond-electronics/W25N02KVZEIR-TR/14560433
P64 https://www.digikey.com/en/products/detail/winbond-electronics/W25Q512JVEIQ/10244706
M1 https://www.winbond.com/hq/product/code-storage-flash/qspi-nand/w25n-kv/?__locale=en&partNo=W25N01KVZEIR
M2 https://www.winbond.com/hq/product/code-storage-flash/qspi-nand/w25n-kv/?__locale=en&partNo=W25N02KVZEIR
M3 https://www.winbond.com/resource-files/W25Q512JV%20SPI%20RevB%2006252019%20KMS.pdf
Expander https://www.digikey.com/en/products/detail/texas-instruments/TCA6408ARGTR/2094640
