"""Conservative NDJSON seam, NOT a drawing/scoring renderer.

Frozen DEV_USB/NO_SENSOR has no physically qualified coordinate source. Even
wire VALID remains a claim: no production POINT event is emitted by this build.
"""
from .protocol import CONTACT, GAP, VALID
from .identity import source_namespace, record_digest


def record_events(records, metadata):
    namespace = metadata.get("source_namespace")
    if namespace != source_namespace(metadata["binding"]):
        raise ValueError("missing/mismatched v2 source namespace")
    previous = None
    active = False
    for record in records:
        record.validate()
        identity = {"source_namespace": namespace, "record_sha256": record_digest(record),
                    "peer_scope": metadata["binding"]["peer_scope"], "device": record.device,
                    "session": str(record.session), "seq": record.seq, "page": record.page,
                    "timestamp_us": str(record.timestamp_us)}
        common = {"schema": "pen-coordinate-source/2", **identity, "UI_allowed": False,
                  "source": "dev_usb_no_sensor", "host_security_attested": False}
        discontinuity = previous is not None and (
            record.session != previous.session or record.device != previous.device
            or record.seq != previous.seq+1 or record.timestamp_us <= previous.timestamp_us
            or record.page != previous.page or bool(record.flags & GAP))
        if active and (discontinuity or not record.flags & CONTACT):
            yield {**common, "type": "END", "reason": "discontinuity" if discontinuity else "contact_up",
                   "boundary_derived": True, "coordinate": None}
            active = False
        if record.flags & CONTACT and not active:
            yield {**common, "type": "BEGIN", "boundary_derived": True, "coordinate": None}
            active = True
        classification = "wire_valid_unqualified" if record.flags & VALID else "invalid_or_control"
        yield {**common, "type": "DIAGNOSTIC", "classification": classification,
               "reason": "frozen_INFO_NO_SENSOR_no_physical_tip_qualification",
               "flags": record.flags, "contact": bool(record.flags & CONTACT),
               "wire_VALID": bool(record.flags & VALID), "gap": bool(record.flags & GAP),
               "raw_x_um": record.x_um, "raw_y_um": record.y_um,
               "confidence": record.confidence, "coordinate": None,
               "window": None, "calibrated_physical_tip_VALID": False}
        previous = record
    if active:
        yield {**common, "type": "END", "reason": "end_of_replay", "boundary_derived": True,
               "coordinate": None}
