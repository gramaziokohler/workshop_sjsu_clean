from compas.data import Data
from compas.geometry import Frame
from compas.robots import Configuration


class ReachabilityMap(Data):

    def __init__(self):
        super(ReachabilityMap, self).__init__()
        self.frames = []
        self.configurations = []  # or dict

    @property
    def data(self):
        data = {}
        data['frames'] = [[frame.data for frame in frames_per_point]
                          for frames_per_point in self.frames]
        data['joint_values'] = [[[c.joint_values if c else None for c in configs]
                                 for configs in configurations_per_point] for configurations_per_point in self.configurations]

        for configurations_per_point in self.configurations:
            for configs in configurations_per_point:
                for c in configs:
                    if c:
                        data['joint_names'] = c.joint_names
                        data['joint_types'] = c.joint_types
                        break

        return data

    @data.setter
    def data(self, data):
        self.frames = [[Frame.from_data(d) for d in frames_per_point]
                       for frames_per_point in data['frames']]
        types = data['joint_types']
        names = data['joint_names']
        self.configurations = [[[Configuration(values, types, joint_names=names) if values else None for values in configs]
                               for configs in configurations_per_point]
                               for configurations_per_point in data['joint_values']]


if __name__ == "__main__":

    import os
    import glob
    import compas

    from compas.geometry import Plane
    from compas.datastructures import Mesh

    import compas_fab
    from compas_fab.robots import Tool
    from compas_fab.robots import RobotSemantics
    from compas_fab.backends import PyBulletClient

    from workshop_sjsu import DATA
    from workshop_sjsu.ur.kinematics.analytical_inverse_kinematics import UR5AnalyticalIK

    points = compas.json_load(os.path.join(DATA, "reachability_points.json"))
    vectors = compas.json_load(os.path.join(DATA, "reachability_vectors.json"))

    start_at = 0
    for i, file in enumerate(glob.glob(os.path.join(DATA, "reachability_map_*.json"))):
        map = ReachabilityMap.from_json(file)
        print(len(map.frames))
        start_at += len(map.frames)
    new_filename = os.path.join(DATA, "reachability_map_%02d.json" % (i+2))
    print(new_filename)
    points = points[start_at:(start_at+2000)]
    print(start_at)

    class Client(PyBulletClient):
        def inverse_kinematics(self, *args, **kwargs):
            return UR5AnalyticalIK(self)(*args, **kwargs)

    tool = Tool.from_json(os.path.join(DATA, "tool.json"))
    camera_mesh = Mesh.from_obj(os.path.join(DATA, "camera.obj"))

    with Client(connection_type='direct') as client:
        urdf_filename = compas_fab.get(
            'universal_robot/ur_description/urdf/ur5.urdf')
        srdf_filename = compas_fab.get(
            'universal_robot/ur5_moveit_config/config/ur5.srdf')

        # Load UR5
        robot = client.load_robot(urdf_filename)
        robot.semantics = RobotSemantics.from_srdf_file(
            srdf_filename, robot.model)

        # Update disabled collisions
        client.disabled_collisions = robot.semantics.disabled_collisions

        # Attach tool and convert frames
        robot.attach_tool(tool)

        map = ReachabilityMap()

        # scene = PlanningScene(robot)
        # cm = CollisionMesh(camera_mesh, 'camera')
        # scene.add_collision_mesh(cm)

        for i, pt in enumerate(points):

            print("Point %i of %i ===============" % (i+1, len(points)))

            frames_per_point = []
            configurations_per_point = []

            for v in vectors:
                frame_tcf = Frame.from_plane(Plane(pt, v))
                frame0_t0cf = robot.attached_tool.from_tcf_to_t0cf([frame_tcf])[0]
                try:
                    options = {"check_collision": True, "cull": True}
                    configurations = client.inverse_kinematics(robot,
                                                               frame0_t0cf,
                                                               options=options)
                    if len(configurations):
                        frames_per_point.append(frame0_t0cf)
                        configurations_per_point.append(configurations)
                except ValueError:
                    continue

            map.frames.append(frames_per_point)
            map.configurations.append(configurations_per_point)
            print(len(frames_per_point))
            print(len(configurations_per_point))
            if i % 100 == 0 and i != 0:
                map.to_json(new_filename)

    print(len(map.frames))
