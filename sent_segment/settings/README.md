## Rosetta Settings

All settings used by different Rosetta modules are defined under this package. 
Try maintaining any additional settings here.

- `common`: settings common across deployment environment
- `dev`: your dev environment (your local machine typically)
- `stag`: the staging environment
- `prod`: the production environment
- `local`: the _local_ environment wherever Rosetta is deployed (dev/stag/prod).
Based on what that is, import the appropriate file inside `local`.
It imports all necessary settings. All other modules `import local` such that they don't
have to care about the deployment environment.
- `entity_tagging`: settings and various mappings used by the `preprocessor`
- `indic_settings`: settings related to Indian languages (scripts, unicode blocks etc.)
