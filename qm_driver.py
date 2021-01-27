# Global (python) modules

import copy

# Local modules

import helpers
import vasp_driver
import gauss_driver


def cleanup_and_setup(bulk_qm_method, igas_qm_method, *argv, **kwargs):

	""" 
	
	Removes QM-X folders, if they exist in the build_dir.
	
	Usage: cleanup_and_setup(bulk_qm_method, igas_qm_method, qm_job_type, <arguments>)
	
	Notes: See function definition in helpers.py for a full list of options. 
	       Expects to be run from ALC-X folder
	       Should only be run once per ALC
	       	
	"""
	
	### ...argv

	args_targets   = argv[0] # This is a pointer!
	args_this_case = -1
	
	if len(argv) == 2:
		args_this_case = argv[1]

	### ...kwargs
	
	default_keys   = [""]*1        ; default_values = [""]*1
	default_keys[0 ] = "build_dir" ; default_values[0 ] = "."

	args = dict(zip(default_keys, default_values))
	args.update(kwargs)		
	
	is_just_bulk = False
	
	if (len(args_targets) == 1) and (args_targets[-1] == "20"):
		is_just_bulk = True

	if (bulk_qm_method == igas_qm_method) or is_just_bulk: # Then it's all VASP, just submit as normal
		if bulk_qm_method == "VASP":
			vasp_driver.cleanup_and_setup(*argv, **kwargs)
		else:
			print "ERROR: Unknown bulk/igas_qm_method in qm_driver.cleanup_and_setup:", bulk_qm_method
	
	else: # Need to submit each differently 
		for i in args_targets:
		
			tmp_args    = list(copy.deepcopy(argv))
			tmp_args[0] = [i]

			if i == "20":
				if bulk_qm_method == "VASP":
					vasp_driver.cleanup_and_setup(*tmp_args, build_dir = args["build_dir"])
				else:
					print "ERROR: Unknown bulk_qm_method in qm_driver.cleanup_and_setup:", bulk_qm_method
			else:
				if igas_qm_method == "VASP":
					vasp_driver.cleanup_and_setup(*tmp_args, **kwargs)
				elif igas_qm_method == "Gaussian":

					gauss_driver.cleanup_and_setup(*tmp_args, **kwargs)
				else:
					print "ERROR: Unknown igas_qm_method in qm_driver.cleanup_and_setup:", igas_qm_method

def setup_qm(my_ALC, bulk_qm_method, igas_qm_method, *argv, **kwargs):

	""" 
	
	Sets up and launches QM single point calculations
	
	Usage: setup_qm(1, <arguments>)
	
	Notes: See function definition in qm_driver.py for a full list of options. 
	       Expects to be run from teh ALC-X folder.
	       Expects the "all" file in the ALC-X folder.
	       Expects the "20" file in the ALC-X/INDEP_X folder.
	       Requries a list of atom types.
	       For VASP jobs:
	         - Expects a POSCAR file for all atom types, named like: X.POSCAR
	         - All other input files (INCAR, KPOINTS, etc) are taken from config.VASP_FILES.
	       Returns a SLURM jobid
	       See setup_vasp functions in <qm_code>_driver.py for additional details

	WARNING: Largely only intended for liquids, so far.	
	      	
	"""	
	
	### ...kwargs
	
	default_keys   = [""]*18
	default_values = [""]*18


	# VASP specific controls
	
	default_keys[0 ] = "basefile_dir"  ; default_values[0 ] = "../VASP_BASEFILES/"		# POTCAR, KPOINTS, and INCAR
	default_keys[1 ] = "VASP_exe" 	   ; default_values[1 ] = ""				# Path to VASP executable
	default_keys[2 ] = "VASP_nodes"    ; default_values[2 ] = "4" 				# Requested VASP  job nodes
	default_keys[3 ] = "VASP_time" 	   ; default_values[3 ] = "00:30:00"			# Requested max walltime for VASP job
	default_keys[4 ] = "VASP_queue"    ; default_values[4 ] = "pdebug"			# Requested VASP job queue
	
	# Gaussian specific controls
	
	default_keys[5 ] = "Gaussian_exe"  ; default_values[5 ] = ""				# Path to Gaussian executable
	default_keys[6 ] = "Gaussian_nodes"; default_values[6 ] = "1"				# Requested Gaussian  job nodes
	default_keys[7 ] = "Gaussian_time" ; default_values[7 ] = "00:30:00"			# Requested max walltime for Gaussian job
	default_keys[8 ] = "Gaussian_queue"; default_values[8 ] = "pdebug"			# Requested Gaussian job queue
	default_keys[9 ] = "Gaussian_scr  "; default_values[9 ] = ""				# Requested Gaussian scratch directory
	
	default_keys[10] = "tight_crit"  ; default_values[10] = "../../../../tight_bond_crit.dat"			      # File with tight bonding criteria for clustering
	default_keys[11] = "loose_crit"  ; default_values[11] = "../../../../loose_bond_crit.dat"			      # File with loose bonding criteria for clustering
	default_keys[12] = "clu_code"	 ; default_values[12] = "/p/lscratchrza/rlindsey/RC4B_RAG/11-12-18/new_ts_clu.cpp"	# Clustering code	
	default_keys[13] = "compilation" ; default_values[13] = "g++ -std=c++11 -O3"

	# Overall job controls	
	
	default_keys[14] = "job_ppn"	  ; default_values[14] = "36"			     # Number of processors per node for ChIMES md job
	default_keys[15] = "job_account"  ; default_values[15] = "pbronze"		     # Account for ChIMES md job
	default_keys[16] = "job_system"   ; default_values[16] = "slurm"		     # slurm or torque       
	default_keys[17] = "job_email"	  ; default_values[17] = True			     # Send slurm emails?
	
	args = dict(zip(default_keys, default_values))
	args.update(kwargs)	
	
	args_targets   = argv[0]
	
	
	run_qm_jobids = []
	
	is_just_bulk = False
	
	if (len(args_targets) == 1) and (args_targets[-1] == "20"):
		is_just_bulk = True

	if (bulk_qm_method == igas_qm_method) or is_just_bulk: # Then it's all VASP, just submit as normal

		if bulk_qm_method == "VASP":
			run_qm_jobid.append(vasp_driver.setup_vasp(my_ALC, *argv,
				first_run      = True,		     
				basefile_dir   = args  ["basefile_dir"],
				job_executable = args  ["VASP_exe"],
				job_email      = config.HPC_EMAIL,
				job_nodes      = args  ["VASP_nodes"],
				job_ppn        = config.HPC_PPN,
				job_walltime   = args  ["VASP_time"],
				job_queue      = args  ["VASP_queue"],
				job_account    = config.HPC_ACCOUNT, 
				job_system     = config.HPC_SYSTEM))
		else:
			print "ERROR: Unknown bulk/igas_qm_method in qm_driver.setup_qm:", bulk_qm_method
	
	else: # Need to submit each differently 

		for i in args_targets:
		
			tmp_args    = list(copy.deepcopy(argv))
			tmp_args[0] = [i] 

			if i == "20":

				if bulk_qm_method == "VASP":
					run_qm_jobids += vasp_driver.setup_vasp(my_ALC, *tmp_args,
						first_run      = True,		     
						basefile_dir   = args  ["basefile_dir"],
						job_executable = args  ["VASP_exe"],
						job_email      = args  ["job_email"],
						job_nodes      = args  ["VASP_nodes"],
						job_ppn        = args  ["job_ppn"],
						job_walltime   = args  ["VASP_time"],
						job_queue      = args  ["VASP_queue"],
						job_account    = args  ["job_account"],
						job_system     = args  ["job_system"])
				else:
					print "ERROR: Unknown bulk_qm_method in qm_driver.setup_qm:", bulk_qm_method
			else:
			
				if igas_qm_method == "VASP":

					run_qm_jobids += vasp_driver.setup_vasp(my_ALC, *tmp_args,
						first_run      = True,		     
						basefile_dir   = args  ["basefile_dir"],
						job_executable = args  ["VASP_exe"],
						job_email      = args  ["job_email"],
						job_nodes      = args  ["VASP_nodes"],
						job_ppn        = args  ["job_ppn"],
						job_walltime   = args  ["VASP_time"],
						job_queue      = args  ["VASP_queue"],
						job_account    = args  ["job_account"],
						job_system     = args  ["job_system"])
						
				elif igas_qm_method == "Gaussian":
				
					run_qm_jobids += gauss_driver.setup_gaus(my_ALC, *tmp_args,
						first_run      = True,		     
						basefile_dir   = args  ["basefile_dir"],
						job_executable = args  ["Gaussian_exe"],
						scratch_dir    = args  ["Gaussian_scr"],
						job_email      = args  ["job_email"],
						job_nodes      = args  ["Gaussian_nodes"],
						job_ppn        = args  ["job_ppn"],
						job_walltime   = args  ["Gaussian_time"],
						job_queue      = args  ["Gaussian_queue"],
						job_account    = args  ["job_account"],
						job_system     = args  ["job_system"],
						tight_crit     = args  ["tight_crit"],
						loose_crit     = args  ["loose_crit"], 
						clu_code       = args  ["clu_code"],   
						compilation    = args  ["compilation"])
				else:
					print "ERROR: Unknown igas_qm_method in qm_driver.setup_qm:", igas_qm_method

	return run_qm_jobids

def continue_job(bulk_qm_method, igas_qm_method, *argv, **kwargs):

	""" 
	
	Checks whether all QM single point calculations ran, resubmits if needed.
	
	Usage: continue_job(<arguments>)
	
	Notes: See function definition in qm_driver.py for a full list of options. 
	       Returns a SLURM jobid list
	       	
	"""

	job_types = argv[0]
	active_jobs = []
	
	
	found_match = 0
	
	tmp_args    = list(copy.deepcopy(argv))		
	
	any_VASP     = []
	any_Gaussian = []
	

	if ((bulk_qm_method == "VASP") and ("20"  in job_types)):
		any_VASP.append("20")
	if ((igas_qm_method == "VASP") and ("all" in job_types)):
		any_VASP.append("all")
		
	if len(any_VASP) > 0:
	
		tmp_args[0] = any_VASP
	
		active_jobs += vasp_driver.continue_job(*tmp_args, **kwargs)
		
		found_match += 1

	if ((bulk_qm_method == "Gaussian") and ("20"  in job_types)):
		print "ERROR: Continue requested condensed phase job for Gaussian"
		exit()
	if ((igas_qm_method == "Gaussian") and ("all" in job_types)):
		any_Gaussian.append("all")	
	
	if len(any_Gaussian) > 0:
	
		tmp_args[0] = any_Gaussian
		
		active_jobs += gauss_driver.continue_job(*tmp_args, **kwargs)
		
		found_match += 1
	
	if found_match == 0:
		print "WARNING: No known qm methods found in qm_driver.continue_job: call", bulk_qm_method, igas_qm_method

	return active_jobs
		

def check_convergence(my_ALC, bulk_qm_method, igas_qm_method, *argv, **kwargs):

	"""
	
	Checks whether qm jobs have completed within their requested number of SCF steps
	
	Usage: check_convergence(my_ALC, no. cases, QM_job_types)
	
	Notes: QM_job_types can be ["all"], ["all","20"] or ["20"]
	       
	WARNING: Deletes output files, modifies input files
	
	"""		
	
	
	### ...argv

	args_cases   = argv[0]	
	args_targets = argv[1] # ... all ... 20

	total_failed = 0
		
	is_just_bulk = False
	
	if (len(args_targets) == 1) and (args_targets[-1] == "20"):
		is_just_bulk = True
	
	if (bulk_qm_method == igas_qm_method) or is_just_bulk: # Then it's all VASP, just submit as normal
		if bulk_qm_method == "VASP":
			total_failed += vasp_driver.check_convergence(my_ALC, *argv, **kwargs)
		else:
			print "ERROR: Unknown bulk/igas_qm_method in qm_driver.check_convergence:", bulk_qm_method
	
	else: # Need to submit each differently 
		for i in args_targets:
			if i == "20":
				if bulk_qm_method == "VASP":
					total_failed += vasp_driver.check_convergence(my_ALC, args_cases,["20"])
				else:
					print "ERROR: Unknown bulk_qm_method in qm_driver.check_convergence:", bulk_qm_method
			else:
				if igas_qm_method == "VASP":
					total_failed += vasp_driver.check_convergence(my_ALC, args_cases,["all"])
				elif igas_qm_method == "Gaussian":
					total_failed += gauss_driver.check_convergence(my_ALC, args_cases,["all"])
				else:
					print "ERROR: Unknown igas_qm_method in qm_driver.check_convergence:", igas_qm_method

	return total_failed

def post_process(bulk_qm_method, igas_qm_method, *argv, **kwargs):

	""" 
	
	Converts a converts a qm output file to .xyzf file
	
	Usage: post_process(<arguments>)
	
	Notes: See function definition in qm_driver.py for a full list of options. 
	       	
	"""	
	
	default_keys   = [""]*2
	default_values = [""]*2


	# VASP specific controls
	
	default_keys[0 ] = "vasp_postproc"  ; default_values[0 ] = "" # Python file for post-processing VASP output
	
	# Gaussian specific controls
	
	default_keys[1 ] = "gaus_postproc"  ; default_values[1 ] = "" # Python file for post-processing Gausian output
	

	args = dict(zip(default_keys, default_values))
	args.update(kwargs)
	
	
	
	
		
	
	is_just_bulk = False
	
	if (len(argv[0]) == 1) and (argv[0][-1] == "20"):
		is_just_bulk = True
	
	if (bulk_qm_method == igas_qm_method) or is_just_bulk: # Then it's all VASP, just submit as normal
		if bulk_qm_method == "VASP":
			vasp_driver.post_process(*argv, vasp_postproc = args["vasp_postproc"])
		else:
			print "ERROR: Unknown bulk/igas_qm_method in qm_driver.post_process:", bulk_qm_method
		
	
	
	else: # Need to submit each differently 
		for i in argv[0]:
		
			tmp_args    = list(copy.deepcopy(argv))
			tmp_args[0] = [i] 	
		
			if i == "20":
				if bulk_qm_method == "VASP":
					vasp_driver.post_process(*tmp_args, vasp_postproc = args["vasp_postproc"])
				else:
					print "ERROR: Unknown bulk_qm_method in qm_driver.post_process:", bulk_qm_method
			else:
				if igas_qm_method == "VASP":
					vasp_driver.post_process(*tmp_args, vasp_postproc = args["vasp_postproc"])
				elif igas_qm_method == "Gaussian":
					gauss_driver.post_process(*tmp_args, gaus_postproc = args["gaus_postproc"])
				else:
					print "ERROR: Unknown igas_qm_method in qm_driver.post_process:", igas_qm_method	