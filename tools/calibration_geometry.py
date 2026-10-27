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
