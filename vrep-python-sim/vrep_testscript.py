import vrep 
import numpy as np

count =0.0
track_target = []
p = 0.0
# close any open connections
vrep.simxFinish(-1)
# Connect to the V-REP continuous server
clientID = vrep.simxStart('127.0.0.1', 19997, True, True, 500, 5) 
 
if clientID != -1: # if we connected successfully
    print ('Connected to remote API server')

# --------------------- Setup the simulation 
vrep.simxSynchronous(clientID,True)

joint_names = ['PhantomXPincher_joint1', 'PhantomXPincher_joint2', 'PhantomXPincher_joint3', 'PhantomXPincher_joint4', 'PhantomXPincher_gripperCenter_joint', 'PhantomXPincher_gripperClose_joint']
# joint target velocities discussed below
joint_target_velocities = np.ones(len(joint_names)) * 10000.0
 
# get the handles for each joint and set up streaming
joint_handles = [vrep.simxGetObjectHandle(clientID,name, vrep.simx_opmode_blocking)[1] for name in joint_names]
 
# get handle for target and set up streaming
_, target_handle = vrep.simxGetObjectHandle(clientID,'target', vrep.simx_opmode_blocking)

dt = 0.02
vrep.simxSetFloatingParameter(clientID,vrep.sim_floatparam_simulation_time_step,dt, vrep.simx_opmode_oneshot) # specify a simulation time step
 
# --------------------- Start the simulation
 
# start our simulation in lockstep with our code
vrep.simxStartSimulation(clientID,vrep.simx_opmode_blocking)
vrep.simxSetJointTargetPosition(clientID,joint_handles[1],1.57, vrep.simx_opmode_oneshot)
        

while count < 1: # run for 1 simulated second
 
    # get the (x,y,z) position of the target
    _, target_xyz = vrep.simxGetObjectPosition(clientID,target_handle,-1, vrep.simx_opmode_blocking) # retrieve absolute, not relative, position
    if _ !=0 : raise Exception()
    track_target.append(np.copy(target_xyz)) # store for plotting
    target_xyz = np.asarray(target_xyz)
 
    q = np.zeros(len(joint_handles))
    dq = np.zeros(len(joint_handles))
    pos = np.zeros(len(joint_handles))

    print ("t= %f" %(count))
    for ii,joint_handle in enumerate(joint_handles):
        
        # get the joint angles
        _, q[ii] = vrep.simxGetJointPosition(clientID,joint_handle,vrep.simx_opmode_blocking)
        if _ !=0 : raise Exception()

        # get the joint velocity
        _, dq[ii] = vrep.simxGetObjectFloatParameter(clientID,joint_handle,2012,vrep.simx_opmode_blocking)  # ID for angular velocity of the joint
        if _ !=0 : raise Exception()

        # vrep.simxSetJointTargetPosition(clientID,joint_handle,p, vrep.simx_opmode_oneshot)
    vrep.simxSetJointTargetPosition(clientID,joint_handles[0],p, vrep.simx_opmode_oneshot)
                
    print ("Joint Positions in ", q*(180/3.14))
    count = count + dt
    print (count) 
    print ("\n \n \n")
    p = p + (3.14/180)*5
    print ("p is %f" %(p))

    vrep.simxSynchronousTrigger(clientID)

# stop our simulation 
print ("simulation shutting down")
vrep.simxStopSimulation(clientID,vrep.simx_opmode_blocking)

