# Created on Thu Nov 02 13:15:01 2017
# Author: Chaitanya Reddy

import vrep
import numpy as np

# Close any open connections
vrep.simxFinish(-1)

# Connect to V-REP continuous server
clientID = vrep.simxStart('127.0.0.1', 19997, True, True, 500, 5)

# If connected successfully, print status
if clientID != -1:
    print 'Connected to remote API server'

# Setup V-REP simulation in synchronous mode
vrep.simxSynchronous(clientID, True)

joint_names = ['redundantRob_joint1', 'redundantRob_joint2', 'redundantRob_joint3', 
               'redundantRob_joint4', 'redundantRob_joint5', 'redundantRob_joint6', 
               'redundantRob_joint7']
joint_target_velocities = np.ones(len(joint_names)) * 10000.0

# Get the handles for joints and target and set up streaming
joint_handles = [vrep.simxGetObjectHandle(clientID, name, vrep.simx_opmode_blocking)[1] for name in joint_names]
_, target_handle = vrep.simxGetObjectHandle(clientID, 'target', vrep.simx_opmode_blocking)

# Set timestep to 1 ms
dt = 0.01
vrep.simxSetFloatingParameter(clientID, vrep.sim_floatparam_simulation_time_step, dt, vrep.simx_opmode_oneshot)

# Start simulation
vrep.simxStartSimulation(clientID, vrep.simx_opmode_blocking)

count = 0
track_target = []

# Run for 1 simulated second
while count < 1:
    
    print 't =', count    
    
    # Get position of target
    _, target_xyz = vrep.simxGetObjectPosition(clientID, target_handle, -1, vrep.simx_opmode_blocking)
    if _ != 0: raise Exception()
    
    # Storing data for plotting
    track_target.append(np.copy(target_xyz))
    target_xyz = np.asarray(target_xyz)
    
    q = np.zeros(len(joint_handles))
    dq = np.zeros(len(joint_handles))
    for ii, joint_handle in enumerate(joint_handles):
        
        # Get joint angles
        _, q[ii] = vrep.simxGetJointPosition(clientID, joint_handle, vrep.simx_opmode_blocking)
        if _ != 0: raise Exception()
        
        # Get joint velocities        
        _, dq[ii] = vrep.simxGetObjectFloatParameter(clientID, joint_handle, 2012, vrep.simx_opmode_blocking)
        if _ != 0: raise Exception()
    
    count += dt
    
    # Move simulation ahead one time step
    vrep.simxSynchronousTrigger(clientID)

# Stop the simulation
vrep.simxStopSimulation(clientID, vrep.simx_opmode_blocking)

# Make sure the last command sent out had time to arrive
vrep.simxGetPingTime(clientID)

# Close the connection to V-REP
vrep.simxFinish(clientID)
print 'Connection closed'

# Notes

# Opmode: Blocking returns current values, Buffer could lag by a timestep
# GetObjectVelocity returns rotational velocity of joint w.r.t world frame
# GetObjectFloatParameter returns the angular velocity of joint w.r.t itself

# To control joints, set target velocity to high value and modulate maximum force
