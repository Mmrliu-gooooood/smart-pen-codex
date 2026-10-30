# Primary references and local pin

No SDK dependency was downloaded for this candidate. The installed official ESP-IDF v5.4 commit is
`67c1de1eebe095d554d281952fde63c16ee2dca0`; its bundled NimBLE API and implementation were inspected.
This is a reproducibility pin, not a claim that this old tag is the supported security release to ship today.

- [ESP-IDF v5.4 NimBLE threading, NVS initialization and API](https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32s3/api-reference/bluetooth/nimble/index.html)
- [Official v5.4 bleprph example](https://github.com/espressif/esp-idf/blob/v5.4/examples/bluetooth/nimble/bleprph/main/main.c)
  — used for API signatures only; deliberately **not** its fixed passkey, automatic NVS erase or bond deletion.
- [Apache NimBLE GATT server API](https://mynewt.apache.org/latest/network/ble_hs/ble_gatts.html)
- [Apple Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [Android BLE overview](https://developer.android.com/develop/connectivity/bluetooth/ble/ble-overview)

Relevant pinned local paths under `esp-idf/`:

- `components/bt/host/nimble/nimble/nimble/host/include/host/ble_gatt.h`: notify_custom consumes mbuf on every outcome.
- `.../host/src/ble_gattc.c`: notify can synchronously invoke GAP NOTIFY_TX.
- `.../host/include/host/ble_gap.h`: connection sec_state has no SC flag; check stored security object's SC bit too.
- `.../host/src/ble_sm.c`: persistence callback failures are not sufficient to clear bonded flag; wrapper must latch failures.
- `.../host/src/ble_hs_pvcy.c`: first boot generates/stores LOCAL_IRK before any peer pairing.
- `.../host/store/config/src/ble_store_nvs.c`: real NVS set_blob/commit in device-enabled runtime.
- `components/bt/host/nimble/nimble/porting/npl/freertos/src/npl_os_freertos.c` and bundled FreeRTOS NPL callout implementation:
  stopping a timer does not itself remove an already queued host event; deadline/generation state must reject stale callbacks.
- `components/bt/host/nimble/Kconfig.in`: SC, legacy, debug keys, security level, persistent bond and single connection gates.

Compilation is not device interoperability, timing, radio, NVS physical power-cut, current-consumption or product safety evidence.
