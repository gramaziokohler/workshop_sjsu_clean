from compas.geometry import Frame
from compas.robots import Configuration
from compas_fab.backends.exceptions import BackendError
from compas_fab.backends.interfaces import InverseKinematics
from .utils import fit_within_bounds
from .offset_wrist_kinematics import UR5
from .offset_wrist_kinematics import UR5e

class AnalyticalInverseKinematics(InverseKinematics):
    """Create a custom InverseKinematicsSolver for a robot.

    The ik for 6 axes industrial robots returns by default 8 possible solutions.
    Those solutions are also sorted. That means, the if you call ik
    on 2 frames that are close to each other, and compare the 8
    configurations of the first one with the 8 of the second one at
    their respective indices, then these configurations are 'close' to
    each other. That is why for certain use cases, e.g. custom cartesian
    path planning it makes sense to keep the sorting and set the ones
    that are out of joint limits or in collison to `None`.

    Examples
    --------

    >>> ik_solver = AnalyticalInverseKinematics()
    """

    def __init__(self, client=None):
        self.client = client

    def inverse_kinematics(self, robot, frame_RCF, start_configuration=None, group=None, options=None):

        solutions = self._inverse_kinematics(frame_RCF)

        # get smallest in numpy
        # new = []
        # for c1 in configuration.joint_values:
        # c2 = c1 - 2 * math.pi
        # c3 = c1 + 2 * math.pi
        # values = [c1, c2, c3]
        # absv = [abs(v) for v in values]
        # idx = absv.index(min(absv))
        # new.append(values[idx])

        configurations = self.joint_angles_to_configurations(robot, solutions)

        # check collisions for all configurations (sets those to `None` that are not working)
        if options and "check_collision" in options and options["check_collision"] is True:
            for i, config in enumerate(configurations):
                try:
                    self.client.check_collisions(robot, config)
                except BackendError:
                    configurations[i] = None

        # fit configurations within joint bounds
        #configurations = self.try_to_fit_configurations_between_bounds(robot, configurations)

        # removes the `None` ones
        if options and "cull" in options and options["cull"] is True:
            configurations = [c for c in configurations if c is not None]

        return configurations

    def _inverse_kinematics(self, frame):
        raise NotImplementedError

    def joint_angles_to_configurations(self, robot, solutions):
        joint_names = robot.get_configurable_joint_names()
        return [Configuration.from_revolute_values(q, joint_names=joint_names) if q else None for q in solutions]

    def try_to_fit_configurations_between_bounds(self, robot, configurations):
        """
        """
        j1, j2, j3, j4, j5, j6 = robot.get_configurable_joints()
        for i, c in enumerate(configurations):
            if c is None:
                continue
            a1, a2, a3, a4, a5, a6 = c.values()
            try:
                a1 = fit_within_bounds(a1, j1.limit.lower, j1.limit.upper)
                a2 = fit_within_bounds(a2, j2.limit.lower, j2.limit.upper)
                a3 = fit_within_bounds(a3, j3.limit.lower, j3.limit.upper)
                a4 = fit_within_bounds(a4, j4.limit.lower, j4.limit.upper)
                a5 = fit_within_bounds(a5, j5.limit.lower, j5.limit.upper)
                a6 = fit_within_bounds(a6, j6.limit.lower, j6.limit.upper)
                configurations[i].joint_values = [a1, a2, a3, a4, a5, a6]
            except AssertionError:
                configurations[i] = None
        return configurations


class UR5AnalyticalIK(AnalyticalInverseKinematics):

    def _inverse_kinematics(self, frame):
        return UR5().inverse(frame)

class UR5eAnalyticalIK(AnalyticalInverseKinematics):

    def _inverse_kinematics(self, frame):
        return UR5e().inverse(frame)