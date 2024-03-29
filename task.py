import numpy as np
import math
from physics_sim import PhysicsSim

class Task():
    """Task (environment) that defines the goal and provides feedback to the agent."""
    def __init__(self, init_pose=None, init_velocities=None, 
        init_angle_velocities=None, runtime=5., target_pos=None):
        """Initialize a Task object.
        Params
        ======
            init_pose: initial position of the quadcopter in (x,y,z) dimensions and the Euler angles
            init_velocities: initial velocity of the quadcopter in (x,y,z) dimensions
            init_angle_velocities: initial radians/second for each of the three Euler angles
            runtime: time limit for each episode
            target_pos: target/goal (x,y,z) position for the agent
        """
        # Simulation
        self.sim = PhysicsSim(init_pose, init_velocities, init_angle_velocities, runtime) 
        self.action_repeat = 3

        self.state_size = self.action_repeat * 6
        self.action_low = 0
        self.action_high = 900
        self.action_size = 4

        # Goal
        self.target_pos = target_pos if target_pos is not None else np.array([0., 0., 10.]) 

    def get_reward(self):
        """Uses current pose of sim to return reward."""
       
        #reward = 1
        #reward += 1.-.2*(abs(self.sim.pose[2] - self.target_pos[2]))
        #reward -= .05*(abs(self.sim.pose[:2] - self.target_pos[:2])).sum()
        #reward -= abs(abs(self.sim.pose[:3] - self.target_pos).sum() - abs(self.sim.v).sum())
        bounds = np.array([20.,  20.,  20.])
        distance = abs(self.sim.pose[:3] - self.target_pos).sum()
        #dist_reward = 1 -(dist_to_goal / bounds).sum()**0.4
        reward = 1. -(distance / bounds.sum())**0.4
        
        if abs(self.sim.pose[2] - self.target_pos[2]) < 1.:
            reward += 10.
        
        
        #print (reward)
        
        #abs_vel = abs(self.sim.v).sum()
        #vel_discount = (1-max(abs_vel, 0.1))**(1/max(dist_to_goal.sum(), 0.1))
        #reward = (dist_reward * vel_discount)
        return reward
        

    def step(self, rotor_speeds):
        """Uses action to obtain next state, reward, done."""
        reward = 0
        pose_all = []
        for _ in range(self.action_repeat):
            done = self.sim.next_timestep(rotor_speeds) # update the sim pose and velocities
            reward += self.get_reward() 
            pose_all.append(self.sim.pose)
        next_state = np.concatenate(pose_all)
        
        if done and self.sim.time < self.sim.runtime: 
            reward += -200.
        
        reward = 1 / (1 + np.exp(-reward))

        
        return next_state, reward, done

    def reset(self):
        """Reset the sim to start a new episode."""
        self.sim.reset()
        state = np.concatenate([self.sim.pose] * self.action_repeat) 
        return state