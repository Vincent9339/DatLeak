import numpy as np
import warnings, sys, os, tqdm, time, copy
warnings.filterwarnings("ignore")
from numba import njit, prange
import matplotlib.pyplot as plt
import seaborn as sns
from src.report import report
from src.loader import nii_reader, fetch_files_
from src.viz import viz_, viz_report
from src.logging_config import setup_logging
from src.utils import summary, cubeT
from src.leakage_ import *

logger = setup_logging()

def main(original_path, scrambled_path, subject_name,task=None, run_=None, Dim4 = False,r=False):

    original = nii_reader(original_path).get_data()
    scrambled = nii_reader(scrambled_path).get_data()

    #########################################
    #             VIZ                       #
    #########################################
    
    if len(list(original.shape)) == 4:
        viz_(original[...,0], slice_=original.shape[0]//2, png_title= "original.png")
        viz_(scrambled[...,0], slice_=original.shape[0]//2, png_title= "scrambled.png")    
        Dim4 = True
    else:
        viz_(original, slice_=original.shape[0]//2, png_title= "original.png")
        viz_(scrambled, slice_=original.shape[0]//2, png_title= "scrambled.png")

    def result_dict():
        keys = [
            "p_corr_fl", "s_corr_fl", "f_corr_fl",
            "p_corr_pl_avg", "p_corr_pl_min", "p_corr_pl_max",
            "s_corr_pl_avg", "s_corr_pl_min", "s_corr_pl_max",
            "f_corr_pl_avg", "f_corr_pl_min", "f_corr_pl_max"
            ]
        return {key: [] for key in keys}

        
    if Dim4:
        results = {
        "x": result_dict(),
        "y": result_dict(),
        "z": result_dict(),
        "t": result_dict()
        }
        axes = ["x", "y", "z", "t"]
        

    if not Dim4:
        results = {
        "x": result_dict(),
        "y": result_dict(),
        "z": result_dict()
        }
        axes = ["x", "y", "z"]
    
    #########################################
    #             SPATIAL ANALYSIS          #
    #########################################
    print(f" - Spatial Analysis")
    for i, axis in enumerate(axes):
        if Dim4:
            logger.info(f"SpatioTemporal Leakage Analysis on 'func'")
            p_corrs, s_corrs, f_l_corrs = leakage_4D(original, scrambled, axis=i)
        if not Dim4:
            logger.info(f"Spatial Leakage Analysis on 'anat'")
            p_corrs, s_corrs, f_l_corrs = leakage_(original, scrambled, axis=i)
        pfl, avg_p_l, min_p_l, max_p_l = summary(p_corrs)
        sfl, avg_s_l, min_s_l, max_s_l = summary(s_corrs)
        ffl, avg_f_l, min_f_l, max_f_l = summary(f_l_corrs)
    
        result = results[axis]
        result["f_corr_fl"].append(ffl)
        result["f_corr_pl_avg"].append(avg_f_l)
        result["f_corr_pl_min"].append(min_f_l)
        result["f_corr_pl_max"].append(max_f_l)
       
        result["p_corr_fl"].append(pfl)
        result["p_corr_pl_avg"].append(avg_p_l)
        result["p_corr_pl_min"].append(min_p_l)
        result["p_corr_pl_max"].append(max_p_l)

        result["s_corr_fl"].append(sfl)
        result["s_corr_pl_avg"].append(avg_s_l)
        result["s_corr_pl_min"].append(min_s_l)
        result["s_corr_pl_max"].append(max_s_l)
        left = np.concatenate([arr[arr >= 0.99999] for arr in np.nanmax(p_corrs,axis=1)]).shape[0]
        right = p_corrs.shape[0]# - np.isnan(np.nanmax(p_corrs,axis=1)).sum()
        if Dim4:
            print(f"\t - Dimension[{axis.upper()}]: \tFull Leakage: {left}/{right} slices\tPartial Leakage: {round(max_p_l, 2)}\tIdentical: {round(ffl, 2)}%")
        if not Dim4:
            print(f"\t - Dimension[{axis.upper()}]: \tFull Leakage: {left}/{right} slices\tPartial Leakage: {round(max_p_l, 2)}\tIdentical: {round(ffl, 2)}%")
        viz_report(p_corrs, s_corrs, f_l_corrs,loop=i)
       
    #########################################
    #             SPATIOTEMPORAL            #
    #########################################
    print(f" - SpatioTemporal Analysis")
    if Dim4:
        o_p = cubeT(original, cube_size=2, stride=1)
        o_s = cubeT(scrambled, cube_size=2, stride=1)
        print(f"\t - Total cubes: {len(o_p)} \tShape {o_p[0].shape}")
        p_corrs, s_corrs,f_l_corrs = spatiotemp_leakage_(np.array(o_p),np.array(o_s))
        full_leakage = True if np.nanmax(p_corrs) >= 0.99999 else False
        partial_leakage = np.round(np.nanmax(p_corrs),2) 
        identical = (np.argwhere(f_l_corrs >= .99999).shape[0] / f_l_corrs.shape[0]) * 100
        print(f"\t - SpatioTemporal: \tFull Leakage: {np.argwhere(p_corrs >= .99999).shape[0]}/{p_corrs.shape[0]} cubes \tPartial Leakage {partial_leakage}\tIdentical: {identical}%")

    #########################################
    #             FULL LEAKAGE              #
    #########################################
    fl_p = np.nanmean([results["x"]['p_corr_fl'], results["z"]['p_corr_fl'], results["y"]['p_corr_fl']])
    fl_f = np.nanmean([results["x"]['f_corr_fl'], results["z"]['f_corr_fl'], results["y"]['f_corr_fl']])
    if fl_p == 0.0 and fl_f == 0.0:
        fl = False
    else: fl = True
    #########################################
    #             PARTIAL LEAKAGE           #
    #########################################
    pl = np.nanmean([results["x"]['p_corr_pl_max'], results["y"]['p_corr_pl_max'],results["z"]['p_corr_pl_max']])

    #########################################
    #             REPORT                    #
    #########################################
    
    if r:
        report_output = subject_name +"_"+ task +"_"+ run_ if task else subject_name
        report(
            top_image_paths=[
                "img/original.png",
                "img/scrambled.png"
            ],
            bottom_image_paths=[
                "img/correlations dist along dimension 0.png",
                "img/correlations dist along dimension 1.png",
                "img/correlations dist along dimension 2.png"
            ],
            top_titles=[
                "Original image",
                "Scrambled image"
            ],
            bottom_titles=[
                "x dim",
                "y dim",
                "z dim"
            ],
            output_html="report/"+report_output+".html", 
            partial_leakage=round(pl,2) * 100,
            
           p_leakage_x_min=np.mean(results["x"]["p_corr_pl_min"]),
           p_leakage_x_max=np.mean(results["x"]["p_corr_pl_max"]),
           p_leakage_x_avg=np.mean(results["x"]["p_corr_pl_avg"]), 
           p_leakage_y_min=np.mean(results["y"]["p_corr_pl_min"]),
           p_leakage_y_max=np.mean(results["y"]["p_corr_pl_max"]),
           p_leakage_y_avg=np.mean(results["y"]["p_corr_pl_avg"]), 
           p_leakage_z_min=np.mean(results["z"]["p_corr_pl_min"]),
           p_leakage_z_max=np.mean(results["z"]["p_corr_pl_max"]),
           p_leakage_z_avg=np.mean(results["z"]["p_corr_pl_avg"]),
            
           s_leakage_x_min=np.mean(results["x"]["s_corr_pl_min"]),
           s_leakage_x_max=np.mean(results["x"]["s_corr_pl_max"]),
           s_leakage_x_avg=np.mean(results["x"]["s_corr_pl_avg"]), 
           s_leakage_y_min=np.mean(results["y"]["s_corr_pl_min"]),
           s_leakage_y_max=np.mean(results["y"]["s_corr_pl_max"]),
           s_leakage_y_avg=np.mean(results["y"]["s_corr_pl_avg"]), 
           s_leakage_z_min=np.mean(results["z"]["s_corr_pl_min"]),
           s_leakage_z_max=np.mean(results["z"]["s_corr_pl_max"]),
           s_leakage_z_avg=np.mean(results["z"]["s_corr_pl_avg"]),           
           full_leakage=round(fl,2)
        )
      
    return np.round(pl,2),fl

    #########################################
    #             MAIN CALL                 #
    #########################################  
if __name__ == "__main__":
    start_time = time.time()
    try:
        if len(sys.argv) < 3:
            raise ValueError("Insufficient arguments")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    #########################################
    #             TEST SECTION              #
    ######################################### 
    
    def test(pl,fl):
        fl = 1 if fl else 0
        with open(os.path.dirname(os.path.abspath(__file__))+"/test/result.tsv", "a") as f:
            try:
                line = "\t".join(map(str, [pl,fl])) + "\n"
                f.write(line)
            except Exception as e:
                print(f"Error writing data to file {filename}: {str(e)}", file=sys.stderr)
 
    usecase = 2.5
    if usecase == None:
        orig = sys.argv[1]
        scra = sys.argv[2]
    elif usecase == 2.2:
        orig = "/staff/vincentajoubi/Trash/wp15-usecase-2.1_aux/usecase-2.2/input/"
        scra = "/staff/vincentajoubi/Trash/wp15-usecase-2.1_aux/usecase-2.2/custom_output/"
    elif usecase == 2.5:
        orig = "/staff/vincentajoubi/wp15-chrono-T/usecase-2.5/input/"
        scra = "/staff/vincentajoubi/wp15-chrono-T/usecase-2.5/custom_output/"                  
    
    original_anat, original_func = fetch_files_(orig)
    scrambled_anat, scrambled_func = fetch_files_(scra) 
    #for i,j in zip(original_func, scrambled_func):
    #    if i.split("/")[-1] == j.split("/")[-1]: 
    #        print(True)
    #    else: 
    #        print(i, j)
    #        break
    #sys.exit(1)
    #original_func, scrambled_func = None, None
    #########################################
    if original_func:
        file_ = nii_reader(original_func[0]).get_data()
        print(f" - Processing func")
        logger.info("Processing func")
        #print(f" - File shape: {file_.shape}")
        try:
            for o, s in tqdm.tqdm(zip(original_func, scrambled_func), total=len(original_func)):
                try:
                    if o.split("/")[-1] != s.split("/")[-1]:
                        logger.info(f"Original and Scrambled filename did not match: \n\tOriginal: {original.split('/')[-1]}\tScrambled: {scrambled.split('/')[-1]}")
                        print(f" - Warning: Original and Scrambled filename does not match.\n\t - Original: {original.split('/')[-1]}\t - Scrambled: {scrambled.split('/')[-1]}")
                        print(f" - Mentioned subject will be skipped.")
                        pass
                    else:
                        logger.info(f"Comparing files:\nOriginal: {o}\nScrambled: {s}")
                        subject_name = o.split('/')[-1].split('_')[0]#.split('-')[1]
                        task = o.split('/')[-1].split('_')[1].split('-')[1] 
                        run_ = o.split('/')[-1].split('_')[2]
                        logger.info(f"Subject ID: {subject_name}")
                        logger.info(f"Task: {task}")
                        logger.info(f"Run: {run_}")
                        logger.info(f"{'-' * 30}{subject_name}-{task}-{run_}{'-' * 30}")
                        print("#" * 40)
                        print(f" - Subject ID: {subject_name}")
                        print(f" - Task: {task}")
                        print(f" - Run: {run_}")
                        print("#" * 40)
                        
                        pl,fl = main(original_path=o,
                             scrambled_path=s, 
                             subject_name=subject_name,
                             task=task, 
                             run_=run_,
                             r=sys.argv[3]
                             )
                             
                        print(f" - Partial Leakage: {pl}%")
                        print(f" - Full Leakage: {fl}%")
                        if fl == 100.0 or fl > 0.0:
                            print(" - Please consider applying scramble on your dataset again.")
                            break
                            sys.exit(1)
                except Exception as e: print(e)
        except Exception as e:
            print(f"Fatal Error: {e}")
            sys.exit(1)
    if not original_func:
        logger.info("Processing anat")
        print(f" - Processing anat")
        file_ = nii_reader(original_anat[0]).get_data()
        print(f" - File shape: {file_.shape}")
        try:
            for o, s in tqdm.tqdm(zip(original_anat, scrambled_anat), total=len(original_anat)):
                try:
                    if o.split("/")[-1] != s.split("/")[-1]:
                        logger.info(f"Original and Scrambled filename did not match: \n\tOriginal: {original.split('/')[-1]}\tScrambled: {scrambled.split('/')[-1]}")
                        print(f" - Warning: Original and Scrambled filename does not match.\n\t - Original: {original.split('/')[-1]}\t - Scrambled: {scrambled.split('/')[-1]}")
                        print(f" - Mentioned subject will be skipped.")
                        pass
                    else:
                        logger.info(f"Comparing files:\nOriginal: {o}\nScrambled: {s}")
                        subject_name = o.split('/')[-1].split('_')[0]
                        logger.info(f"Subject ID: {subject_name}")
                        logger.info(f"{'-' * 30}{subject_name}{'-' * 30}")
                        print("#" * 40)
                        print(f" - Subject ID: {subject_name}")
                        print("#" * 40)
                
                        pl,fl = main(o,s, subject_name ,r=sys.argv[3])

                        print(f" - Partial Leakage: {pl}")
                        print(f" - Full Leakage: {fl}")
                        if fl == 100.0 or fl > 0.0:
                            print(" - Please consider applying scramble on your dataset again.")
                            break
                            sys.exit(1)    
                except Exception as e: print(e)
                
        except Exception as e:
            print(e)
            sys.exit(1)
    
    print(f"All subjects have been successfully evaluated.")
    total_time = time.time() - start_time
    print(f"\nTotal time taken: {time.strftime('%H:%M:%S', time.gmtime(total_time))}")
		
