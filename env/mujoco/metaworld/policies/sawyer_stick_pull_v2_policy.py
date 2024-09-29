import numpy as np

from metaworld.policies.action import Action
from metaworld.policies.policy import Policy, assert_fully_parsed, move


class SawyerStickPullV2Policy(Policy):
    @staticmethod
    @assert_fully_parsed
    def _parse_obs(obs):
        return {
            "hand_pos": obs[:3],
            "unused_1": obs[3],
            "stick_pos": obs[4:7],
            "unused_2": obs[7:11],
            "obj_pos": obs[11:14],
            "unused_3": obs[14:-3],
            "goal_pos": obs[-3:],
        }

    def get_action(self, obs):
        o_d = self._parse_obs(obs)

        action = Action({"delta_pos": np.arange(3), "grab_pow": 3})

        action["delta_pos"] = move(o_d["hand_pos"], to_xyz=self._desired_xyz(o_d), p=25.0)
        action["grab_pow"] = self._grab_pow(o_d)

        return action.array

    @staticmethod
    def _desired_xyz(o_d):
        hand_pos = o_d["hand_pos"]
        stick_pos = o_d["stick_pos"] + np.array([-0.015, 0.0, 0.03])
        thermos_pos = o_d["obj_pos"] + np.array([-0.015, 0.0, 0.03])
        goal_pos = o_d["goal_pos"] + np.array([-0.05, 0.0, 0.0])

        if abs(stick_pos[0] - thermos_pos[0]) > 0.04:
            if np.linalg.norm(hand_pos[:2] - stick_pos[:2]) > 0.02:
                return stick_pos + np.array([0.0, 0.0, 0.1])
            elif abs(hand_pos[2] - stick_pos[2]) > 0.02:
                return stick_pos
            elif abs(stick_pos[1] - thermos_pos[1]) > 0.02:
                return np.array([stick_pos[0], thermos_pos[1], stick_pos[2]])
            elif abs(stick_pos[2] - thermos_pos[2]) > 0.02:
                return np.array([stick_pos[0], *thermos_pos[1:]])
            else:
                return thermos_pos
        else:
            return goal_pos

    @staticmethod
    def _grab_pow(o_d):
        hand_pos = o_d["hand_pos"]
        stick_pos = o_d["stick_pos"] + np.array([-0.015, 0.0, 0.03])

        if np.linalg.norm(hand_pos[:2] - stick_pos[:2]) > 0.02 or abs(hand_pos[2] - stick_pos[2]) > 0.1:
            return -1.0
        else:
            return +0.7
