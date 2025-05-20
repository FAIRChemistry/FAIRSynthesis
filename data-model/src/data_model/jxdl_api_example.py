import jxdl_api as api
from .generated.jxdl_data_structure import JXDLSchema, Synthesis

jxdl_file_path = "../data/generated/jxdl.json"
# Load JXDL file into our JXDLSchema class structure
jxdl: JXDLSchema = api.load_jxdl(jxdl_file_path)

# Access an individual experiment by id
example_experiment_id = "KE-232"
example_synthesis = api.get_synthesis_by_experiment_id(jxdl, example_experiment_id)
api.print_synthesis_data(example_synthesis)

# Access the product of an individual experiment
example_experiment_id_2 = "KE-010"
example_synthesis_2 = api.get_synthesis_by_experiment_id(jxdl, example_experiment_id_2)
product_2 = api.find_product(example_synthesis_2)
print(f"Experiment ID: {example_experiment_id}")
api.print_product(product_2)

# Access and count all experiments
synthesis_list = api.get_synthesis_list(jxdl)
print(f"Total number of experiments: {len(synthesis_list)}")

# Compute the average number of PXRD files per experiment
pxrd_files_per_experiment = []
for synthesis in synthesis_list:
    pxrd_files = api.find_corresponding_pxrd_files(synthesis)
    pxrd_files_per_experiment.append(len(pxrd_files))
average_pxrd_files = sum(pxrd_files_per_experiment) / len(pxrd_files_per_experiment)
print(f"Average number of PXRD files per experiment: {average_pxrd_files:.2f}")
