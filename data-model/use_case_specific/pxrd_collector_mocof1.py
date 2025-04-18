def process_pxrd_file_use_case_specific(pxrd_file):
    pxrd_file.sample_holder_shape = pxrd_file.sample_holder_shape.replace("film", "KAPTON_FILMS").replace("capillary",
                                                                          "HILGENBERG_GLASS_NO_14_CAPILLARY")