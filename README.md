# Scientific X-ray

## Usage
0. get data from (https://drive.google.com/file/d/1R5Jk5el5fCQ6gp-hAZIY0TxyjNpFqPp_/view?usp=sharing)
1. place corresponding .gml files into [./input/source_gml/](./input/source_gml/)
2. run [gen_intermediate_files.py](./src/gen_intermediate_files.py) to generate intermediate files
3. run [ilf_fitting.py](./src/ilf_fitting.py) to fit ILF
4. run [main.py](./src/main.py) to get publications' x-ray
5. run [vd_statistics.py](./src/vd_statistics.py) to get vaild depth distribution of idea tree and there subtrees
6. run [get_delta_D_for_specific_topic.py](./src/get_delta_D_for_specific_topic.py) to calculate DPI