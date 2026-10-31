# Whole-product budget reconciliation before storage choice
2026-10-31 UTC — read-only. No further vendor search, purchases, contacts, source/PCB edits or adoption.

## Decision
**Do not recommend the USD45.70 NOR+expander offer from isolated pricing.** It is one verified catalog combination, not the cheapest market route, not a complete incremental quote and not demonstrated affordable insideCNY760. Current whole-product evidence establishes neither a complete total nor any amount of safely spendable headroom.

Lowest-complexity engineering baseline is existing8MiBPICO hardware, disabled-by-default software, and accepted archived receiver-v2 integration, while closing camera/accuracy/safety/whole-product costs. No new storage/expander/reset reassignment yet. If a first physical prototype eventually retains internal-only storage, disclose its short capacity explicitly and obtain the relevant user tradeoff rather than claiming24h or silently assuming frequent sync is acceptable. Current hardware remainsNOFAB/NOPOWER.

## What the budget artifacts actually establish
|Evidence / scenario|AmountCNY fortwo|Meaning / remainingunknown|
|---|---:|---|
|Historical2026-10-29 domestic fiveMPN installed subtotal|111.96|12installedICs only. Not completeBOM, currentprice or globalminimum; onepart then hadexactly2stock withoutspares|
|Budget minus only thissubset|648.04|Arithmeticunallocatedamount, NOTspendableheadroom: virtuallyallothercostsremain|
|Hypotheticalassembly/setup400 plusfiveMPN|511.96|Leaves248.04 forMCUs,charger,otherparts,cameras,batteries,PCB/FPC,shell/refills,losses,test;400notactualquote|
|Same plus2PICO atthenlisted62|635.96|Leaves124.04 forremainingcategories;PICOthenstock0,notavailablepurchaseroute|
|Two separateboardfamilies, standarddouble-sidedSMTfixedfee scenario|800.00|Thisconditionalroutealoneexceeds760beforeparts/boards; doesNOTproveallmarket/routesimpossible|
|Older14MPNDigiKeypartialreference|504.58|Manyrequiredpartsabsent; notdomesticminimum orcompletecurrentoffer|
|FiveMPN substituted into aboveDigiKeymix|345.30|Mixedhistoricalpartialreference,notcompleteavailableBOM|
|Above mixedpartial +officialPICO sample reference74|419.30|Stillpartial/unqualified; cannotdeclare340.70headroom|
|Actual supplier formalquotations in archivedaudit|0|No completecostupperbound orbudgetapproval|
|ProposedNOR+expanders catalogoffer|USD45.70|Separatecurrency; noFXassumption, noPCB/assembly/testdelta; NOTcheapestmarketclaim|

FivehistoricalMPNs:TPS63802DLAR2=11.10;REF3425IDBVR2=12.16;TMUX1101DCKR4=38.60;TPS3700DDCR2=17.30;TPS3899DL01DSER2=32.80CNY. Sum111.96. Do notaddtheirDigiKeypricesagain.

Other historical procurement obstacles: BQ24074RGTR smallquantityprice unavailable atdomesticpage(MOQ3000,longlead);PICO-N8R8thenstock0;TPS3899only2left. No live recheck inthisdecisiontask; thesearehistoricalconstraints, notcurrentinventoryassertions.

## Unpriced/unclearedwhole-productitems
|Group|Unresolved|
|---|---|
|Camera/lens/optics|Historical135.6CNYinformation lacks settledownershipquantity/lens/accountingtreatment; newqualifiedcamera/lens/filter/window/holderpriceunknown. Existingpropertymayavoidnewcash butmustnotbezero-valuedtoprovewholeproductcost|
|Electronics|Historical185entities/pen,188ledgerrows inclsharedfixture;300electronicsparts fortwo+3sharedfixtureparts.113singlepenprocurementpositions lackedcompleteMPNs, plus3fixturepositions; latestreconstructionnotrepriced. Do notsumobsoletepickup/gateboardsagain|
|Battery|Noapprovedprotectedpack/current/termination/NTCconstructionprice;10180shapealoneisinsufficient|
|PCB/FPC|Main6layer14x101.5 andpower4layer14x45 cannotdirectlyshareonequalifiedstackuppanel;USB,illumination,contactcarrier andunplacedADC ownership/MOQs remain. Flexconnector orientation/stackup/NRE unpriced|
|Mechanical/refill|Shell,cassetteparts,retention,wire,shims,springs,refillIRcompatibility andminimumorders unresolved|
|Assembly|Paidqualifiedhidden-joint/double-sidedreflow,stencils,feeding,inspection,loss/rework andmanualwork notquoted; userwillingness≠freequalifiedlabor|
|Testing/calibration|Equipmentaccess/fixtures/operatorfees/consumables notknown; nofree-labassumption;5µmuncertaintywasastudygoal,notmandatoryinstrumentpurchase|
|Tax/MOQ/spares|Mustincludeactualoutlayandlossreserve;shippingaloneexcludedbyuser|

## Software/storagechoicewithoutfidelitytrade
|Stage|Storagefacts|Incrementalstorageparts|Decisionboundary|
|---|---|---|---|
|Existingsoftwaredefault|Flashrecordingdisabled;providerNULL;nooperationalofflineclaim|None|Completeexistinggatedintegrationandtestsfirst|
|Existingexplicit8MiBprofile|3.875MiBlog,63,488x64Bslots;17.6356minat60records/sbeforeextraevents/tornslots;32recordedsessionslimit;wholelogreclaimonlyafterALLACKed,safeidle|None|Exactexistingceiling,NOT24hfulfillment oruseracceptance;noautomaticenable/flash|
|Futureinternalexactcodec/segmentreclaim|Couldimprovebutunmeasured;8–16Baveragesillustrate1.18–2.35h,notguarantees|NoexternalstorageIC|Separateimplementation/testplan;keep1µm/64-bitµs,quality/contact/page/faultrecords;doNOTadvertisefuturecompressionnow|
|Later64/128/256expansion|Seealternativesreport:~2.805/5.795/11.709hconditionalconservativeenvelopes|Notbudgetqualified;GPIO/reset redesignrequired|Postponeadoptionuntilcompletecostandphysicalfitclosed|
|Later512MiB|24htargetenvelopepossiblewithoutcompressionwithinexplicitbudget|Nosuitableimmediatetwo-pieceofferqualified|Do notdesignaroundunavailablepart orcalltargethardrequirement|

Do notloweraccuracy,omitfaults/down-up/quality/timing,oroverwriteunACKedbacklogtopurchasecapacity. Shortercapacityisavisibleproducttradeoff,notacodeoptimization.

## Accepted-successor/evidence reconciliation
- OldcostarchiveREADME records15missingreferences; laterverification/hardware_mechanical_stage_20261029/COST_DEPENDENCY_UPDATE.json resolvesall26directhistoricalinputs. Freshread-onlySHA256check:26/26PASS. Thisdoesnotrestoreallrecursivebuilderenvironment orregenerate/pricelatestBOM.
- Accepted_successors_stage_20261029 README explicitlystatesitsstatic/capturebackupdoesnotrepriceorprove380/pen,sizeor30daydelivery.
- Costportablechecker rerun:28frozenfiles,188ledgerrows,5negativecases andconditionalarithmeticPASS. Itdidnotrefreshprices,re-extractnativeBOM orapprovebudget. Rootgitstatusremainedclean.
- ArchivePCreceiver-v2 isintendedintegrationbaseline(exactACK,DELETE+EXTRA,schema/timeoutfixes),notolderrootbridge. ArchivedBLEstorematchesroot,solimitsunchanged.

## What might need a user choice
Not yet ask 'payUSD45.70oraccept17min' asifthesearetheonlymarketoptions. Firstresolvequalifiedcamera/pack,MCUsmallquantityandpaidassembly/PCBfullcostusingavailableevidence/authorizedquotes. Ifnocomplete≤760routewithdesiredretentionemerges, present explicitfirstprototypecapacityvsbudget/schedule alternatives. Usercanacceptashorterofflinefirstprototypewhile24hremainslatergoal;donotassumethatacceptance. Nohardwareadoptionfromthisreport.

## Local inputs
recovery_20261031/docs/research/cost_archive_20261029/{README_ZH.md,prototype_cost_audit_20261029_0044/,prototype_cost_routes_20261029_0112/,metrology_target_erratum_0139/}
recovery_20261031/procurement/{BATTERY_REFILL_COST.md,cost_ledger.csv}
recovery_20261031/verification/hardware_mechanical_stage_20261029/COST_DEPENDENCY_UPDATE.json
recovery_20261031/verification/accepted_successors_stage_20261029/README_ZH.md
Earlierstorage/artifactpricingisdatedobservation,nofurtherwebresearchperformedhere.
