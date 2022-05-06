from compas.geometry import Point
from compas.geometry import Plane
from compas.geometry import Frame
from compas.geometry import Vector
from compas.geometry import angle_points
from compas.geometry import Rotation
from workshop_sjsu.planning import SPHERE_CENTER
from workshop_sjsu.planning import SPHERE_RADIUS


def translate_and_create_frames(points3d):
    frames = []
    for points_per_path in points3d:
        frames.append([])
        for point in points_per_path:
            point = Point(*point) + Vector(*SPHERE_CENTER)
            normal = point - SPHERE_CENTER
            plane = Plane(point, normal)
            frame = Frame.from_plane(plane)
            frames[-1].append(frame)
    return frames


def create_transition_frames_on_sphere(start_frame, end_frame):
    """
    """
    A = start_frame.point
    B = end_frame.point
    O = Point(*SPHERE_CENTER)
    # create transition
    arc_plane = Plane.from_three_points(O, A, B)
    arc_angle = angle_points(O, A, B)
    arc_length = arc_angle * SPHERE_RADIUS

    max_dist = 0.02  # maximal distance between 2 points on the sphere
    num = int(arc_length/max_dist)

    transition_frames = []
    if num < 2:
        transition_frames.append(start_frame.copy())
        transition_frames.append(end_frame.copy())
    else:
        v = Vector(*list(A - O))
        angle_step = arc_angle/(num - 1)
        for i in range(num):
            T = Rotation.from_axis_and_angle(arc_plane.normal, angle_step * i)
            p = Point(*list(O)) + v.transformed(T)
            normal = p - SPHERE_CENTER
            plane = Plane(p, normal)
            transition_frames.append(Frame.from_plane(plane))
    return transition_frames
