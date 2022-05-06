import math
from compas.utilities import color_to_rgb


def map_range(value, from_min, from_max, to_min, to_max):
    """Performs a linear interpolation of a value within the range of [from_min,
        from_max] to another range of [to_min, to_max].
    """
    from_range = from_max - from_min
    to_range = to_max - to_min
    value_scaled = (value - from_min) / float(from_range)
    return to_min + (value_scaled * to_range)


def cartesian_to_polar(x, y):
    rho = math.sqrt(x**2 + y**2)
    phi = math.atan2(y, x)
    return(rho, phi)


def map2sphere(sphere, circle, points2d, scale):
    points3d = []
    for pt2d in points2d:
        rho, phi = cartesian_to_polar(pt2d.X, pt2d.Y)
        crv = sphere.IsoCurve(1, phi)
        rho_mapped = map_range(rho, 0, circle.Radius, -
                               math.pi/2, math.pi/2 - scale)
        pt3d = crv.PointAt(rho_mapped)
        points3d.append(pt3d)
    return points3d


def format_data_for_export(points3d, gradients, colors):

    gradients_list = []
    for i in range(gradients.BranchCount):
        path = gradients.Path(i)
        alist = list(gradients.Branch(path))
        gradients_list.append(list(alist))

    colors_list = []
    for i in range(colors.BranchCount):
        path = colors.Path(i)
        alist = list(colors.Branch(path))
        colors_list.append(
            [color_to_rgb([c.R, c.G, c.B], normalize=True) for c in alist])

    points3d_list = []
    for i in range(points3d.BranchCount):
        path = points3d.Path(i)
        alist = list(points3d.Branch(path))
        points3d_list.append([[p.X, p.Y, p.Z] for p in alist])

    for g, p, c in zip(gradients_list, points3d_list, colors_list):
        assert(len(g) == len(p))
        assert(len(g) == len(c))

    data = {}
    data['points3d'] = points3d_list
    data['gradients'] = gradients_list
    data['colors'] = colors_list

    return data
