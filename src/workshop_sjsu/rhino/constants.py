import Rhino.Geometry as rg
import math
from workshop_sjsu.planning.constants import SPHERE_RADIUS
from workshop_sjsu.planning.constants import SPHERE_CENTER

RADIUS = SPHERE_RADIUS
SPHERE_CENTER = rg.Point3d(*list(SPHERE_CENTER))
sphere = rg.Sphere(rg.Point3d(0, 0, 0), RADIUS)
angle = math.pi
T = rg.Transform.Rotation(angle, rg.Vector3d.YAxis, sphere.Center)
sphere.Transform(T)