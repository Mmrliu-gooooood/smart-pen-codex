#!/bin/sh
set -eu
cd "$(dirname "$0")"
export XDG_CONFIG_HOME=/tmp/rebuild-kicad/config XDG_CACHE_HOME=/tmp/rebuild-kicad/cache XDG_DATA_HOME=/tmp/rebuild-kicad/data
kicad-cli version
kicad-cli sch export netlist --format kicadxml --output usb_tail_revA.xml usb_tail_revA.kicad_sch
kicad-cli sch erc --output erc.rpt usb_tail_revA.kicad_sch
kicad-cli pcb drc --schematic-parity --output drc.rpt usb_tail_revA.kicad_pcb
/usr/bin/python3 tools/verify.py
kicad-cli sch export pdf --output review.pdf usb_tail_revA.kicad_sch
mkdir -p preview
kicad-cli pcb export svg --mode-single --page-size-mode 2 --exclude-drawing-sheet --layers F.Cu,F.Fab,F.Silkscreen,Edge.Cuts --output preview/board.svg usb_tail_revA.kicad_pcb

kicad-cli pcb export svg --mode-single --page-size-mode 2 --exclude-drawing-sheet --layers B.Cu,Edge.Cuts --output preview/back.svg usb_tail_revA.kicad_pcb
