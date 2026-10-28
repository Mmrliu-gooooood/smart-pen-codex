"""Geometric reference only: supplied camera pose -> rigid calibrated nib point.

Convention: X_camera = R_camera_from_paper @ X_paper + t_camera_from_paper.
All coordinates use mm. Camera +z points forward. Paper z=0 is writing plane.
R and t must come from a separately validated pose solver; this is not one.
"""
import math


def nib_on_paper(rotation, translation, nib_camera, *, contact, plane_tolerance_mm=0.2):
    if not contact:
        raise ValueError('no paper contact; no valid writing coordinate')
    if len(rotation)!=3 or any(len(row)!=3 for row in rotation):
        raise ValueError('rotation must be 3x3')
    if len(translation)!=3 or len(nib_camera)!=3:
        raise ValueError('vectors must have 3 elements')
    values=[v for row in rotation for v in row]+list(translation)+list(nib_camera)+[plane_tolerance_mm]
    if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in values):
        raise ValueError('finite numeric geometry required')
    if plane_tolerance_mm<=0:
        raise ValueError('positive tolerance required')
    for i in range(3):
        for j in range(3):
            dot=sum(rotation[k][i]*rotation[k][j] for k in range(3))
            if abs(dot-(1 if i==j else 0))>1e-5:
                raise ValueError('rotation is not orthonormal')
    r=rotation
    determinant=(r[0][0]*(r[1][1]*r[2][2]-r[1][2]*r[2][1])
                 -r[0][1]*(r[1][0]*r[2][2]-r[1][2]*r[2][0])
                 +r[0][2]*(r[1][0]*r[2][1]-r[1][1]*r[2][0]))
    if abs(determinant-1)>1e-5:
        raise ValueError('reflection is not a camera rotation')
    if nib_camera[2]<=0 or translation[2]<=0:
        raise ValueError('invalid forward depth')
    delta=[nib_camera[i]-translation[i] for i in range(3)]
    paper=[sum(rotation[j][i]*delta[j] for j in range(3)) for i in range(3)]
    if abs(paper[2])>plane_tolerance_mm:
        raise ValueError('nib/plane inconsistency: reject, do not project silently')
    return tuple(paper)


def axis_contact_on_paper(rotation, translation, axis_origin_camera,
                          axis_direction_camera, *, paper_plane_camera,
                          travel_interval_mm, contact, units,
                          min_abs_axis_normal=0.1):
    """Intersect a calibrated sliding nib axis with a validated paper plane.

    PRECONDITION: R,t are an externally validated rigid camera pose, not an
    estimate produced here. X_camera = R @ X_paper + t; paper is z=0.
    All lengths MUST be mm (units='mm'); directions are unit vectors.
    paper_plane_camera=(nx,ny,nz,d) means n dot X_camera + d = 0 and is
    cross-checked against R,t (it is not independent calibration evidence).

    Axis origin is the calibrated zero-travel nib point, not an arbitrary pen
    body point. X_camera(s) = axis_origin_camera + s*axis_direction_camera.
    s is signed mm along that direction; travel_interval_mm=(low,high) is
    inclusive and must be supplied from separate mechanical calibration.
    Returns ((paper_x_mm, paper_y_mm, 0.0), s_mm). Contact must be exactly True.
    The inferred s comes from geometry, NOT from contact-switch measurement.
    No projection/clamping of an out-of-range solution is permitted. Neither
    this function nor a successful result validates pose, axis, or physical
    rigidity; lateral play, flex and curved nib contact remain unmodelled.
    """
    def vector(value, size, name):
        try:
            result = tuple(value)
        except TypeError as exc:
            raise ValueError(name + ' must be a numeric vector') from exc
        if len(result) != size or not all(number(v) for v in result):
            raise ValueError(name + ' has invalid shape or nonfinite values')
        return result

    def number(value):
        try:
            return (isinstance(value, (int, float)) and not isinstance(value, bool)
                    and math.isfinite(value))
        except OverflowError:
            return False

    if contact is not True:
        raise ValueError('confirmed contact=True required')
    if units != 'mm':
        raise ValueError('geometry must be explicitly supplied in mm')
    if not number(min_abs_axis_normal) or not 0 < min_abs_axis_normal <= 1:
        raise ValueError('axis/normal threshold must be in (0,1]')
    try:
        r = tuple(vector(row, 3, 'rotation row') for row in rotation)
    except TypeError as exc:
        raise ValueError('rotation must be 3x3') from exc
    if len(r) != 3:
        raise ValueError('rotation must be 3x3')
    t = vector(translation, 3, 'translation')
    origin = vector(axis_origin_camera, 3, 'axis origin')
    axis = vector(axis_direction_camera, 3, 'axis direction')
    plane = vector(paper_plane_camera, 4, 'paper plane')
    low, high = vector(travel_interval_mm, 2, 'travel interval')
    if low > high:
        raise ValueError('travel interval must be ordered')
    # Do not silently normalize a wrongly scaled direction: s has mm units.
    if abs(math.hypot(*axis) - 1) > 1e-8:
        raise ValueError('axis direction must be unit length')
    if abs(math.hypot(*plane[:3]) - 1) > 1e-8:
        raise ValueError('plane normal must be unit length')
    for i in range(3):
        for j in range(3):
            dot = sum(r[k][i]*r[k][j] for k in range(3))
            if not math.isfinite(dot) or abs(dot - (i == j)) > 1e-8:
                raise ValueError('rotation is not orthonormal')
    determinant = (r[0][0]*(r[1][1]*r[2][2]-r[1][2]*r[2][1])
                   - r[0][1]*(r[1][0]*r[2][2]-r[1][2]*r[2][0])
                   + r[0][2]*(r[1][0]*r[2][1]-r[1][1]*r[2][0]))
    if abs(determinant - 1) > 1e-8:
        raise ValueError('rotation must be proper (no reflection)')
    normal = tuple(r[i][2] for i in range(3))
    offset = -sum(normal[i]*t[i] for i in range(3))
    # Both orientations of the same plane are valid.
    sign = 1 if sum(normal[i]*plane[i] for i in range(3)) >= 0 else -1
    if (not math.isfinite(offset)
            or any(abs(normal[i]-sign*plane[i]) > 1e-8 for i in range(3))
            or abs(offset-sign*plane[3]) > 1e-6):
        raise ValueError('paper plane is inconsistent with camera pose')
    denominator = sum(normal[i]*axis[i] for i in range(3))
    if abs(denominator) < min_abs_axis_normal or denominator == 0:
        raise ValueError('parallel or near-grazing axis/plane intersection')
    displacement = -sum(normal[i]*(origin[i]-t[i]) for i in range(3))/denominator
    if not math.isfinite(displacement) or not low <= displacement <= high:
        raise ValueError('inferred axial displacement outside calibrated travel')
    point = tuple(origin[i]+displacement*axis[i] for i in range(3))
    if not all(math.isfinite(v) for v in point) or point[2] <= 0 or t[2] <= 0:
        raise ValueError('invalid forward depth or nonfinite intersection')
    paper = tuple(sum(r[j][i]*(point[j]-t[j]) for j in range(3)) for i in range(3))
    if not all(math.isfinite(v) for v in paper) or abs(paper[2]) > 1e-7:
        raise ValueError('numerically inconsistent paper intersection')
    return (paper[0], paper[1], 0.0), displacement
