# APvCT
Anatomy preserving virtual/synthetic CTs for treatment sites with large deformation of ROIs.

This Python script is intended for use with scripting module of the RayStation treatment planning system version 12A DTK to generate various daily CT images from daily CBCTs. Therefore, the script might not work with other versions of RayStation.
The script was developed for the following published article: [Generation and evaluation of anatomy-preserving virtual CT for online adaptive proton therapy.](https://aapm.onlinelibrary.wiley.com/doi/10.1002/mp.16941)

The study was carried out on patients with prostate cancer, but the script can be adapted for other treatment sites. 

Clinical and imaging data:
1. Clinical target volume (CTV) includes prostate gland and seminal vesicles.
2. Endorectal balloons were used to immobilize the prostate in all patients.
3. CBCT images were taken on the Proteus-PLUS proton therapy system.

Conditions to verify before running the script: 
1. A planning CT with CTV and OARs, and assigned to an imaging system (CT modality). 
2. A CBCT image assigned to an imaging system (CBCT modality).
3. Planning CT must have an external roi contoured.

Important points to remember:
1. The ROIs generated using DLS on cCBCT may not be accurate. Therefore, it is recommended to verify the DLS generated ROIs and manually corrected if required before generating APvCT.
2. Following contours were used as controlling ROIs: Bladder, Rectum, Femoral head left and Femoral head right.

You can cite the work as:
Kaushik S, Ödén J, Sharma DS, Fredriksson A, Toma-Dasu I. Generation and evaluation of anatomy-preserving virtual CT for online adaptive proton therapy. Med Phys. 2024;51(3):1536-1546. doi:10.1002/mp.16941

BibTex
@article{kaushik2024generation,
  title={Generation and evaluation of anatomy-preserving virtual CT for online adaptive proton therapy},
  author={Kaushik, Suryakant and {\"O}d{\'e}n, Jakob and Sharma, Dayananda Shamurailatpam and Fredriksson, Albin and Toma-Dasu, Iuliana},
  journal={Medical Physics},
  volume={51},
  number={3},
  pages={1536-1546},
  year={2024},
  publisher={Wiley Online Library}
}