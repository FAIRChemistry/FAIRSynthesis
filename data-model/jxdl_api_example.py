import jxdl_api as api

jxdl_file_path = "../data/generated/jxdl.json"
jxdl = api.load_jxdl(jxdl_file_path)

example_experiment_id = "KE-232"
example_synthesis = api.get_synthesis_by_experiment_id(jxdl, example_experiment_id)
api.print_synthesis_data(example_synthesis)

example_experiment_id_2 = "KE-010"
example_synthesis_2 = api.get_synthesis_by_experiment_id(jxdl, example_experiment_id_2)
product_2 = api.find_product(example_synthesis_2)
print(f"Experiment ID: {example_experiment_id}")
api.print_product(product_2)