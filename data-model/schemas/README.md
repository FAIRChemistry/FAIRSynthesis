# Schemas

This folder contains the JSON Schemas for this project.


## Sciformation ELN Cleaned Schema

This is the schema of an intermediate step of our chain: the schema for a Sciformation ELN Export that has been cleaned up.
Data in this format is then used in a next step to export to JXDL.

Explore or edit the schema [here](https://metaconfigurator.github.io/meta-configurator/?schema=https://github.com/FAIRChemistry/FAIRSynthesis/blob/main/data-model/schemas/sciformation_eln_cleaned.schema.json).
After clicking the link, navigate to the `Schema Editor` tab in the top left menu bar.


## JXDL

JSON XDL (JXDL) is the JSON version for [XDL](https://croningroup.gitlab.io/chemputer/xdl/standard/index.html) developed by the Cronin Group.
XDL itself is in the XML format.
Currently, our JXDL schema in this folder contains only the subset of the properties of XDL relevant for our use-case, but it could be easily extended by any other properties from XDL.

Explore or edit the schema [here](https://metaconfigurator.github.io/meta-configurator/?schema=https://github.com/FAIRChemistry/FAIRSynthesis/blob/main/data-model/schemas/jxdl.schema.json).
After clicking the link, navigate to the `Schema Editor` tab in the top left menu bar.
