## Rules for handling logs
1. Node application standard output (stdout)
  - Entries → UI log only (e.g. /data/<name>.log)
  - Does not go to HA addon logs
2. Node application errors (stderr)
  - Entries → UI log + HA addon logs (echo)
  - For example, if node crash or throw
3. Addon's own logs
  - All entries → HA addon logs (echo)
  - For example, "Starting app", "Force stopping PID", etc.
4. Total UI logs
  - Node stdout + Node stderr + crash info
  - Shown individually for each application