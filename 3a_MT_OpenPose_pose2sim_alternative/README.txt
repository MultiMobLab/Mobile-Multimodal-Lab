To get OpenPose and Pose2sim running, follow instructions here: https://envisionbox.org/embedded_openpose_to_pose2sim_tracking.html

Once folders openpose and Pose2sim are filled in with necessary stuff, move the folder Empty_project_ENVISION_settings into folder Pose2sim

If you need, prepare videos (cut set of three cams into 3 individuals), use the scripts in videoPrep folder. There are two separate scripts, one for trial videos, one for calibrations.

The trial videos will be saved in folders that you can directly copy to folder projectdata, calibration videos will be cutted to folder calibration. If you are using pose2sim default calibration, you can copy this folder into the session folder where it belongs (eg T1_P1). If you are using anipose, just create folder calibration at session folder, and copy the calibration_anipose.toml file there (note that the script expects that it will be named exactly like this)

Then you run first script openpose, when this is done, run pose2sim

