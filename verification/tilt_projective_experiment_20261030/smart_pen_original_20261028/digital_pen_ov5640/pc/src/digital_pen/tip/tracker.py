"""Tip tracking and ROI scheduling for the TRACK stream (Task 10).

The tracker filters tip detections (sensor pixels) with a constant-velocity
Kalman filter and decides where the next ROI goes:

- ``track``: the last frame had an accepted detection; the next ROI is
  centred a little behind the predicted tip along the pen, so the cone and
  part of the hand stay in view for the detector, and the prediction is
  passed to the detector as a hint.
- ``coast``: up to ``lost_after`` frames without a detection; the filter
  predicts and the ROI follows the prediction.
- ``lost``: the caller should search the overview (``detect_in_overview``)
  and hand the result to ``reacquire``; the ROI stays where it was.

A detection far outside the prediction gate is not accepted at once (one
bad frame cannot pull the ROI away), but two consecutive far detections that
agree re-initialise the track (pen lifted and moved quickly).
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from digital_pen.tip.detector import TipDetection, TipDetector


@dataclass(frozen=True)
class TrackerConfig:
    roi_size: tuple[int, int] = (160, 160)
    sensor_size: tuple[int, int] = (800, 600)
    # ROI centre distance behind the tip along the pen axis.
    behind_px: float = 24.0
    # White-acceleration process noise; handwriting peaks at a few m/s^2,
    # i.e. roughly 1e4 px/s^2 at 2.6 px/mm.
    accel_px_s2: float = 1.5e4
    measurement_px: float = 1.5
    # Innovation gate: accept within gate_sigma standard deviations, but at
    # least min_gate_px.
    gate_sigma: float = 4.0
    min_gate_px: float = 12.0
    # Two consecutive far detections closer than this re-initialise.
    jump_agree_px: float = 10.0
    lost_after: int = 4
    # The ROI is moved only when its target moved at least this far.
    roi_step_px: int = 4
    max_dt_s: float = 0.25
    # A track that stays within still_px for still_s is "still": a pen held
    # still, or a mark on the paper taken for the tip (see TipPipeline).
    still_px: float = 4.0
    still_s: float = 2.0


@dataclass(frozen=True)
class TrackState:
    status: str  # "track" | "coast" | "lost"
    x: float
    y: float
    theta: float
    vx: float
    vy: float
    misses: int
    accepted: bool


class TipTracker:
    def __init__(self, config: TrackerConfig | None = None):
        self.config = config or TrackerConfig()
        self.reset()

    def reset(self) -> None:
        self.x = None  # state (x, y, vx, vy)
        self.p = None
        self.t = None
        self.theta = 0.0
        self.misses = 0
        self.status = "lost"
        self._pending = None
        self.roi = None
        self._still = None  # (x, y, since) of the current still stretch

    # -- filter ------------------------------------------------------------------

    def _init(self, t, det: TipDetection) -> None:
        self.x = np.array((det.x, det.y, 0.0, 0.0))
        r = self.config.measurement_px**2
        self.p = np.diag((r, r, 400.0**2, 400.0**2))
        self.t = t
        self.theta = det.theta
        self.misses = 0
        self.status = "track"
        self._pending = None
        self._still = (det.x, det.y, t)

    def _note_still(self, t: float) -> None:
        x, y = float(self.x[0]), float(self.x[1])
        if self._still is None or np.hypot(x - self._still[0], y - self._still[1]) > (
            self.config.still_px
        ):
            self._still = (x, y, t)

    def still_for(self, t: float) -> float:
        """Seconds the track has stayed on one spot (0 unless tracking)."""
        if self.status != "track" or self._still is None:
            return 0.0
        return max(0.0, t - self._still[2])

    def _predicted(self, t):
        dt = float(np.clip(t - self.t, 0.0, self.config.max_dt_s))
        f = np.eye(4)
        f[0, 2] = f[1, 3] = dt
        q = self.config.accel_px_s2**2
        g = np.array(((dt**4 / 4, dt**3 / 2), (dt**3 / 2, dt**2)))
        qm = np.zeros((4, 4))
        qm[np.ix_((0, 2), (0, 2))] = g * q
        qm[np.ix_((1, 3), (1, 3))] = g * q
        return f @ self.x, f @ self.p @ f.T + qm

    def predict(self, t: float) -> tuple[float, float] | None:
        if self.x is None:
            return None
        x, _ = self._predicted(t)
        return float(x[0]), float(x[1])

    def update(self, t: float, det: TipDetection | None) -> TrackState:
        """Feed one frame's detection (sensor pixels, or None / not found)."""
        c = self.config
        found = det is not None and det.found
        accepted = False
        if self.x is None or self.status == "lost":
            if found:
                self._init(t, det)
                accepted = True
            else:
                self.misses += 1
        else:
            if self.t is not None and t - self.t > c.max_dt_s:
                # A long gap: keep the position, forget the velocity.
                self.x[2:] = 0
                self.p[2:, 2:] = np.diag((400.0**2, 400.0**2))
            x, p = self._predicted(t)
            self.x, self.p, self.t = x, p, t
            if found:
                h = np.zeros((2, 4))
                h[0, 0] = h[1, 1] = 1
                innovation = np.array((det.x, det.y)) - x[:2]
                s = p[:2, :2] + np.eye(2) * c.measurement_px**2
                distance = float(np.hypot(*innovation))
                gate = max(
                    c.min_gate_px, c.gate_sigma * float(np.sqrt(np.trace(s) / 2))
                )
                if distance <= gate:
                    k = p @ h.T @ np.linalg.inv(s)
                    self.x = x + k @ innovation
                    self.p = (np.eye(4) - k @ h) @ p
                    self.theta = _blend_angle(self.theta, det.theta, 0.5)
                    self.misses = 0
                    self.status = "track"
                    self._pending = None
                    self._note_still(t)
                    accepted = True
                elif self._pending is not None and (
                    np.hypot(det.x - self._pending.x, det.y - self._pending.y)
                    <= c.jump_agree_px
                ):
                    self._init(t, det)
                    accepted = True
                else:
                    self._pending = det
            if not accepted:
                if not found:
                    self._pending = None
                self.misses += 1
                self.status = "coast" if self.misses < c.lost_after else "lost"
        return self.state(accepted)

    def reacquire(self, t: float, det: TipDetection) -> TrackState:
        """Start a track from an overview detection (sensor pixels)."""
        if not det.found:
            return self.state(False)
        self._init(t, det)
        # Overview positions are coarse: widen the position uncertainty.
        self.p[0, 0] = self.p[1, 1] = 8.0**2
        return self.state(True)

    def state(self, accepted: bool = False) -> TrackState:
        if self.x is None:
            nan = float("nan")
            return TrackState("lost", nan, nan, nan, 0.0, 0.0, self.misses, accepted)
        return TrackState(
            self.status,
            float(self.x[0]),
            float(self.x[1]),
            float(self.theta),
            float(self.x[2]),
            float(self.x[3]),
            self.misses,
            accepted,
        )

    # -- ROI scheduling ------------------------------------------------------------

    def hint(self, t: float, origin: tuple[float, float]):
        """(x, y, theta) detector hint in the frame whose top-left is ``origin``."""
        if self.x is None or self.status == "lost":
            return ()
        px, py = self.predict(t)
        return ((px - origin[0], py - origin[1], self.theta),)

    def next_roi(self, t: float) -> tuple[int, int, int, int] | None:
        """ROI (x, y, w, h) for the frame at ``t``; None while lost and unplaced."""
        c = self.config
        if self.x is None or self.status == "lost":
            return self.roi
        px, py = self.predict(t)
        w, h = c.roi_size
        cx = px - c.behind_px * np.cos(self.theta)
        cy = py - c.behind_px * np.sin(self.theta)
        x0 = int(np.clip(round(cx - w / 2), 0, c.sensor_size[0] - w))
        y0 = int(np.clip(round(cy - h / 2), 0, c.sensor_size[1] - h))
        if (
            self.roi is None
            or max(abs(x0 - self.roi[0]), abs(y0 - self.roi[1])) >= c.roi_step_px
        ):
            self.roi = (x0, y0, w, h)
        return self.roi


def _blend_angle(a: float, b: float, weight: float) -> float:
    d = (b - a + np.pi) % (2 * np.pi) - np.pi
    return float(a + weight * d)


def detect_in_overview(
    detector: TipDetector, overview: np.ndarray, scale: float, region=None
) -> TipDetection:
    """Coarse tip search in a box-averaged overview; result in sensor pixels.

    The overview is upsampled back to sensor scale so the detector sees the pen
    at its usual size (blurred); good enough to place an ROI on it.
    """
    up = cv2.resize(overview, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    det = detector.detect(up, region=region)
    # Box average: overview pixel k covers sensor pixels [k*s, (k+1)*s); the
    # linear resize maps its centre to (k + 0.5) * s - 0.5 as well.
    return det
