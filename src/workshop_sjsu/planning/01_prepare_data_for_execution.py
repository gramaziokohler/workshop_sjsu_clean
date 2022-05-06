import os
import logging
import compas
import math

from compas.robots import Configuration
from compas_fab.backends.pybullet import LOG

from workshop_sjsu.planning.setup import Client
from workshop_sjsu.planning.setup import sjsu_setup
from workshop_sjsu.planning.utilities import translate_and_create_frames
from workshop_sjsu.planning.utilities import create_transition_frames_on_sphere
from workshop_sjsu.planning import IK_IDX
from workshop_sjsu import DATA

LOG.setLevel(logging.ERROR)


def reduce_to_reachable(frames, connection_type='gui'):

    configurations = []
    indices2keep = []

    with Client(connection_type=connection_type) as client:

        robot, _ = sjsu_setup(client)

        num_frames = sum([len(frames_per_path) for frames_per_path in frames])

        for i, frames_per_path in enumerate(frames):
            configurations_per_path = []
            for frame_tcf in frames_per_path:
                frame0_t0cf = robot.attached_tool.from_tcf_to_t0cf([frame_tcf])[0]
                try:
                    configs = client.inverse_kinematics(robot, frame0_t0cf, options={
                                                        "check_collision": True, "cull": False})
                    solution = configs[IK_IDX]
                except ValueError:
                    solution = None
                if not solution:
                    break
                else:
                    configurations_per_path.append(solution)
            else:
                configurations.append(configurations_per_path)
                indices2keep.append(i)

        num_configurations = sum([len(configurations_per_path)
                                 for configurations_per_path in configurations])
        print("Removing %i of %i frames, since they are not reachable." %
              (num_frames - num_configurations, num_frames))

    return configurations, indices2keep


def add_transition_between_paths_and_flatten(frames, gradients, colors, configurations, connection_type='gui'):

    frames_flattened = []
    gradients_flattened = []
    colors_flattened = []
    configurations_flattened = []
    startends = [] # here we set start and end points to 1, rest is 0

    print(len(frames))

    def create_startend(num):
        array = [0 for _ in range(num)]
        array[0] = 1
        array[-1] = 1
        return array


    with Client(connection_type=connection_type) as client:
        robot, _ = sjsu_setup(client)

        if len(frames) == 1:  # one path
            frames_flattened = frames[0]
            gradients_flattened = gradients[0]
            colors_flattened = colors[0]
            configurations_flattened = configurations[0]

            startends = create_startend(len(frames_flattened))

        else:
            for i, (path1, path2) in enumerate(zip(frames[:-1], frames[1:])):

                start_frame = path1[-1]
                end_frame = path2[0]
                transition_frames = create_transition_frames_on_sphere(start_frame, end_frame)

                # add another 2
                # TODO: this can be improved by moving along the sphere to the point
                #point_s = closest_point_on_plane(path1[-1].point, UP_PLANE)
                #frame_s = Frame(point_s, path1[-1].xaxis, path1[-1].yaxis)

                #point_e = closest_point_on_plane(path2[0].point, UP_PLANE)
                #frame_e = Frame(point_e, path2[-1].xaxis, path2[-1].yaxis)

                if i == 0:
                    frames_flattened += path1
                    gradients_flattened += gradients[i]
                    colors_flattened += colors[i]
                    configurations_flattened += configurations[i]
                    startends += create_startend(len(path1))

                # transition
                frames_flattened += transition_frames  # [frame_s, frame_e]
                gradients_flattened += [0 for _ in range(len(transition_frames))]
                colors_flattened += [(0, 0, 0) for _ in range(len(transition_frames))]
                startends += create_startend(len(transition_frames))

                # configurations_flattened
                for frame_tcf in transition_frames:
                    frame0_t0cf = robot.attached_tool.from_tcf_to_t0cf([frame_tcf])[0]
                    configs = client.inverse_kinematics(robot, frame0_t0cf,
                                                        options={
                                                            "check_collision": True,
                                                            "cull": False}
                                                        )
                    solution = configs[IK_IDX]
                    if not solution:
                        raise ValueError("No solution for transition")
                    configurations_flattened.append(solution)

                # path2
                frames_flattened += path2
                gradients_flattened += gradients[i + 1]
                colors_flattened += colors[i + 1]
                configurations_flattened += configurations[i + 1]
                startends += create_startend(len(path2))

    print("Now %d frames with transitions" % len(frames_flattened))

    # add offs to start and end
    def add_offs(array_flattened, off=None, num=2):
        if off is None:
            s = array_flattened[0]
            e = array_flattened[-1]
        else:
            s = off
            e = off

        start = [s for _ in range(num)]
        end = [e for _ in range(num)]
        return start + array_flattened + end

    num = 2
    frames_flattened = add_offs(frames_flattened, off=None, num=num)
    gradients_flattened = add_offs(gradients_flattened, off=0, num=num)
    colors_flattened = add_offs(colors_flattened, off=(0, 0, 0), num=num)
    configurations_flattened = add_offs(configurations_flattened, off=None, num=num)
    startends = add_offs(startends, off=0, num=num)

    return frames_flattened, gradients_flattened, colors_flattened, configurations_flattened, startends


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
        v2 = min(j) - 2 * math.pi + max(j) - 2 * math.pi
        v3 = min(j) + 2 * math.pi + max(j) + 2 * math.pi
        values = [math.fabs(v) for v in [v1, v2, v3]]
        idx = values.index(min(values))
        if idx == 1:
            for k in range(len(new_joint_values)):
                new_joint_values[k][i] -= 2 * math.pi
        elif idx == 2:
            for k in range(len(new_joint_values)):
                new_joint_values[k][i] -= 2 * math.pi

    new_configurations = [Configuration.from_revolute_values(
        j) for j in new_joint_values]

    return new_configurations


if __name__ == "__main__":

    #NAME = "example03"
    NAME = "example04"
    NAME = "Juan Zavala Path"
    NAME = "Juan_2"
    NAME = "Milvia"
    NAME = "Sharleen"



    filepath = os.path.join(DATA, 'current_file.txt')
    with open(filepath, 'r') as f:
        current = f.read()

    basename = os.path.basename(current)
    name, ending = os.path.splitext(basename)
    name = name[:-len("_execution")]

    filepath = os.path.join(os.path.dirname(current), name + ending)


    #filepath = os.path.join(DATA, "%s.json" % NAME)

    data = compas.json_load(filepath)

    gradients = data['gradients']
    points3d = data['points3d']
    colors = data['colors']

    # 1. Move points to defined sphere center (in RCF) and make frames
    frames = translate_and_create_frames(points3d)

    # 2. Reduce to only use buildable paths
    ct = 'gui'
    #ct = 'direct'
    configurations, indices2keep = reduce_to_reachable(
        frames, connection_type=ct)
    
    for J in configurations:
        for c in J:
            if c is None:
                print("1 here")


    # remove also from frames, gradients and colors
    frames = [frames[i] for i in indices2keep]
    gradients = [gradients[i] for i in indices2keep]
    colors = [colors[i] for i in indices2keep]

    F, G, C, J, S = add_transition_between_paths_and_flatten(frames, gradients, colors, configurations, connection_type=ct)
    
    for c in J:
        if c is None:
            print("here")

    J = make_configurations_smooth(J)

    data = {}
    data['frames'] = F
    data['gradients'] = G
    data['colors'] = C
    data['configurations'] = J
    data['startends'] = S

    #filepath = os.path.join(DATA, "%s_execution.json" % NAME)
    compas.json_dump(data, current)
    print(current)
