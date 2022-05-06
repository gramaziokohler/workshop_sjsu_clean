import os
import logging
import compas
import math

from compas.robots import Configuration
from compas_fab.backends.pybullet import LOG

from workshop_sjsu.planning.setup import Client
from workshop_sjsu.planning.setup import sjsu_setup
from workshop_sjsu.planning import IK_IDX
from workshop_sjsu import DATA

LOG.setLevel(logging.ERROR)


def reduce_to_reachable(frames, connection_type='gui'):

    configurations = []
    indices2keep = []

    with Client(connection_type=connection_type) as client:

        robot, _ = sjsu_setup(client)

        num_frames = len(frames)

        configurations = []
        frames_reachable = []
        frames_not_reachable = []

        for frame_tcf in frames:
            frame0_t0cf = robot.attached_tool.from_tcf_to_t0cf([frame_tcf])[0]
            try:
                configs = client.inverse_kinematics(robot, frame0_t0cf, options={
                                                    "check_collision": True, "cull": False})
                solution = configs[IK_IDX]
            except ValueError:
                solution = None
            if solution:
                configurations.append(solution)
                frames_reachable.append(frame_tcf)
            else:
                frames_not_reachable.append(frame_tcf)
                
        num_configurations = len(configurations)
        print("Removing %i of %i frames, since they are not reachable." % (num_frames - num_configurations, num_frames))

    return configurations, frames_reachable, frames_not_reachable


def make_configurations_smooth(configurations):

    new_joint_values = []

    for i in range(len(configurations)):
        if i == 0:
            prev = configurations[i].joint_values
        else:
            curr = configurations[i].joint_values
            new = []
            for p, c1 in zip(prev, curr):
                c2 = c1 - 2 * math.pi
                c3 = c1 + 2 * math.pi
                values = [c1, c2, c3]
                diffs = [math.fabs(p - c) for c in values]
                idx = diffs.index(min(diffs))
                new.append(values[idx])
            configurations[i].joint_values = new
            prev = configurations[i].joint_values
        configurations[i].joint_values[-1] = 0
        new_joint_values.append(configurations[i].joint_values)

    # now try if we can bring all of them down
    for i, j in enumerate(zip(*new_joint_values)):
        v1 = min(j) + max(j)
        v2 = v1 - 2 * math.pi
        v3 = v1 + 2 * math.pi
        values = [math.fabs(v) for v in [v1, v2, v3]]
        idx = values.index(min(values))
        if idx == 1:
            for k in range(len(new_joint_values)):
                new_joint_values[k][i] -= 2 * math.pi
        elif idx == 2:
            for k in range(len(new_joint_values)):
                new_joint_values[k][i] -= 2 * math.pi

    new_configurations = [Configuration.from_revolute_values(j) for j in new_joint_values]

    return new_configurations


if __name__ == "__main__":

    NAME = "frames_reachable_in"

    filepath = os.path.join(DATA, "%s.json" % NAME)

    frames = compas.json_load(filepath)

    # 2. Reduce to only use buildable paths
    ct = 'gui'
    #ct = 'direct'
    configurations, frames_reachable, frames_not_reachable = reduce_to_reachable(frames, connection_type=ct)

    J = make_configurations_smooth(configurations)

    data = {}
    data['frames'] = frames_reachable
    data['frames_not_reachable'] = frames_not_reachable
    data['configurations'] = J

    filepath = os.path.join(DATA, "%s_out.json" % NAME)
    compas.json_dump(data, filepath)
