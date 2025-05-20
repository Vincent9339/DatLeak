import nibabel as nib
import os
def fetch_files_(base_path):
    anat, func = list(), list()
    for root, _, files in os.walk(base_path):
        for f in files:
            if f.endswith(".nii.gz") or "_T1w.nii.gz" in f:
                if "/func" in root:
                    func.append(os.path.join(root, f))
                elif "/anat" in root:
                    anat.append(os.path.join(root, f))
                elif f.endswith(".nii.gz") or "_T1w.nii.gz" in f:
                    anat.append(os.path.join(root, f))
                else:
                    print(f"No file found")
    try:
        anat = sorted(anat, key=lambda x: int(os.path.basename(x).split('_')[0].split('-')[1]))
    except ValueError:
        anat = sorted(anat)
    func = sorted(func)
    return anat, func

class nii_reader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.img = None
        self.data = None
        self.orientation = None
        self.dim_orientations = None  # Stores orientation per dimension (e.g., ['R', 'A', 'S'])        
        self.load_nii()
        self._nii_determine_orientation()

    def load_nii(self):
        self.img = nib.load(self.file_path)
        self.data = self.img.get_fdata()
    
    def _nii_determine_orientation(self):
        if self.img is None:
            return
        
        ras_affine = nib.orientations.io_orientation(self.img.affine)
        orientation_codes = nib.orientations.ornt2axcodes(ras_affine)
        
        self.dim_orientations = orientation_codes
        self.orientation = self._interpret_primary_orientation(orientation_codes)
    
    def _interpret_primary_orientation(self, codes):
        if 'S' in codes[2]: 
            return "axial"
        elif 'A' in codes[2]:  
            return "coronal"
        elif 'L' in codes[2] or 'R' in codes[2]:  
            return "sagittal"
        else:
            return "unknown"
    
    def get_data(self):
        return self.data
    
    def get_orientation(self):
        return self.orientation
    
    def get_dimension_orientations(self):
        return self.dim_orientations

