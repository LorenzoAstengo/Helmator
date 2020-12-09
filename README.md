# Helmator

Helmator is a Python script useful to generate, from a kubernetes backup, an helm chart ready to go.
To run helmator we will need an export of the kubernetes namespace that can be generated through this script: https://github.com/LorenzoAstengo/k8s-backup. 
**Pay attention you need to run k8s-backup script with --clean and --cmyaml options enabled!!**
K8s-backup will generate a backup of your desired namespace, you just have to pass the backup path to helmator and it will generate your parameterized chart.

What does it parameterize?

- Namespaces for all resources
- PersistentVolumes 
  - nfs paths
- Deployments:
  - replicas
  - image Version
  - imagePath