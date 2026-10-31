# Enable-group source applicability — connectivity research only

Actual package map (not GPIO/package-number substitution): U101.37 = GPIO47 / CAM_BUS_EN; U101.47 = GPIO41 / CAM_PWR_EN; U101.48 = GPIO42 / existing CAM_IO_EN. GPIO48 is a different ILLUM_STROBE net and is not reassigned. Values, netlist, bridges and all footprint poses remain unchanged.

## GPIO / rail / startup gates
Official ESP32-S3-PICO-1 datasheet v1.2, Table1-1 and Table2-1: actual N8R8 has quad8MB flash and octal8MB PSRAM with nominal3.3V SPI supply. GPIO47/48 can select VDD3P3_CPU (default) or VDD_SPI; do not import a different S3 module's1.8V assumption. GPIO41 is MTDI; GPIO42 MTMS. GPIO3/eFuse/JTAG ownership and actual firmware mux/reset states require explicit validation. No eFuse or firmware change is performed. Input enable or external pulldowns do not establish a defined safe complete startup sequence.
Sources: https://www.espressif.com/sites/default/files/documentation/esp32-s3-pico-1_datasheet_en.pdf ; https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html

## Bus-enable (not Schmitt inversion)
CAM_BUS_EN joins U101.37, R108.1 (100k1% pulldown), JP202.1. JP202 remains OPEN. Its other side SCCB_ENABLE_LINK feeds R204100ohm then SCCB_EN_SAFE, with R2054.7k pulldown and TCA9517 U204.5 EN. U204 VCCA=SENS_VIO1V8, VCCB=AON3V3. TCA9517 EN is active high, VIH>=.7VCCB/VIL<=.3VCCB. A nominal ideal3.3V divider4700/(4700+100) is not loaded GPIO VOH/PVT/partial-power proof. No downstream EN merge is counted across the open bridge.
Source: https://www.ti.com/lit/ds/symlink/tca9517.pdf

## Existing IO-enable / translator OE
CAM_IO_EN joins U101.48/R107100k/JP201.1. Its source copper is locally replaced only to admit GPIO41; the complete old physical pad partition must remain exact. JP201 OPEN separates IO_ENABLE_LINK, R2011k, ISO_GATE/R20210k, SN74LVC1G14 U205.2. Inversion produces CAM_ISO_OE_N at U205.4, with R20310k AON pullup and existing translator OE core. This is the Schmitt path; it must not be attributed to CAM_BUS_EN. Dynamic OE, brownout, loaded levels and actual input slew remain unqualified.
Source: https://www.ti.com/lit/ds/symlink/sn74lvc1g14.pdf

## Power-enable
CAM_PWR_EN joins U101.47, R106.1 (100k1% pulldown), R302.1 (1k1%), TP301.1 (ENABLE MEASURE). R302.2 CAM_ON already joins R301100k pulldown and TPS22918 U301.3. ON VIH>=1V, VIL<=.5V; do not leave floating. ON asserted before VIN can lose controlled output slew even within absolute ratings. C3031nF CT and R303100ohm QOD do not prove actual startup/shutdown or discharge under load. JP301 stays OPEN, separating PRELINK from CAM_3V3_SW. Probe/tool/contact/ownership at TP301 is unqualified; connecting the physical land is not permission to drive or energize it.
Source: https://www.ti.com/lit/ds/symlink/tps22918.pdf

## Joint source construction and measurement obligations
Source-only preflight replaces IO_EN/RESET gateways and a short XCLK In3 source approach. It does not alter the original AON/C104/USB copper or any component pose. RESET has a newly explicit In2 crossover, so power-plane fill/material is NOT unchanged. Exact old partition preservation, current powered-node islands/feed corridors, retained/new reference projections, source/input/output/private-arm lengths and changed XCLK/RESET/IO_EN paths must be measured on the eventual selected native. The GPIO47 continuation has a small nominal full-installation-envelope clearance (.060mm after improvement), not a manufacturing-margin claim. No universal courtyard-as-routing-ban is inferred, but all actual full bodies/Fab, explicit keepouts and operation guards remain hard.

NOFAB / NO POWER / providerNULL / JP201,JP202,JP301 OPEN. This does not demonstrate camera safe-off, initialization, capture, storage duration, or sensor-role compatibility. Parent is independently evaluating storage architecture; no further long successor follows this bounded checkpoint until that review.
