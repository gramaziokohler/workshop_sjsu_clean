import os
import compas
from compas.robots import LocalPackageMeshLoader
from compas.robots import RobotModel
from compas.datastructures import Mesh

from compas_fab.robots import Tool
from compas_fab.robots import RobotSemantics
from compas_fab.robots import PlanningScene
from compas_fab.robots import CollisionMesh
from compas_fab.robots import Robot

from workshop_sjsu import DATA
from workshop_sjsu.ur.kinematics.analytical_inverse_kinematics import UR5AnalyticalIK
from workshop_sjsu.ur.kinematics.analytical_inverse_kinematics import UR5eAnalyticalIK

urdf_filename = os.path.join(DATA, "ur_e_description", "urdf", "ur5e_robot.urdf")
srdf_filename = os.path.join(DATA, "ur5_e_moveit_config", "config", "ur5e.srdf")


def UR5e():

    model = RobotModel.from_urdf_file(urdf_filename)
    semantics = RobotSemantics.from_srdf_file(srdf_filename, model)

    loader = LocalPackageMeshLoader(DATA, 'ur_e_description')
    model.load_geometry(loader)

    robot = Robot(model, semantics=semantics)
    return robot


def sjsu_setup(client, camera=True):
    tool = Tool.from_json(os.path.join(DATA, "tool.json"))

    # TODO: convert to pybullet convex meshes?

    # Load UR5
    robot = client.load_robot(urdf_filename)
    robot.semantics = RobotSemantics.from_srdf_file(srdf_filename, robot.model)

    # Update disabled collisions
    client.disabled_collisions = robot.semantics.disabled_collisions

    # Attach tool and convert frames
    robot.attach_tool(tool)
    scene = PlanningScene(robot)

    if camera:
        camera_mesh = Mesh.from_json(os.path.join(DATA, "camera_in_position.json"))
        cm = CollisionMesh(camera_mesh, 'camera')
        scene.add_collision_mesh(cm)

    return robot, scene


if not compas.IPY:

    from compas_fab.backends import PyBulletClient

    class Client(PyBulletClient):
        def inverse_kinematics(self, *args, **kwargs):
            return UR5eAnalyticalIK(self)(*args, **kwargs)
