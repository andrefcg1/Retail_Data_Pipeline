def check(scan_name, checks_subpath=None, data_source='retail', project_root='include'):
    """Run Soda Core scans via CLI against one or more check files.

    This replaces the previous Scan() API usage to ensure Soda Core compatibility.
    """
    import os
    import subprocess

    print('Running Soda Core scan ...')
    # Allow overriding config via env, and prefer a local config if present to avoid Soda Cloud
    config_override = os.environ.get('SODA_CONFIG')
    default_config = f'{project_root}/soda/configuration.yml'
    local_config = f'{project_root}/soda/configuration.local.yml'
    config_file = config_override or (local_config if os.path.exists(local_config) else default_config)
    checks_dir = f'{project_root}/soda/checks'

    if checks_subpath:
        checks_dir = f"{checks_dir}/{checks_subpath}"

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Soda configuration not found: {config_file}")
    if not os.path.isdir(checks_dir):
        raise FileNotFoundError(f"Soda checks directory not found: {checks_dir}")

    # Collect all .yml check files in the checks directory
    check_files = [
        os.path.join(checks_dir, name)
        for name in sorted(os.listdir(checks_dir))
        if name.endswith('.yml') or name.endswith('.yaml')
    ]

    if not check_files:
        raise FileNotFoundError(f"No Soda check files found in: {checks_dir}")

    soda_bin = os.environ.get('SODA_BIN', '/usr/local/airflow/soda_venv/bin/soda')
    if not os.path.exists(soda_bin):
        raise FileNotFoundError(
            f"Soda binary not found at '{soda_bin}'. Set SODA_BIN env var if installed elsewhere."
        )

    failed = False
    for check_file in check_files:
        cmd = [
            soda_bin, 'scan',
            '-d', data_source,
            '-c', config_file,
            check_file,
        ]
        print(f"Executing: {' '.join(cmd)}")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        print(proc.stdout)
        if proc.returncode != 0:
            failed = True
            print(proc.stderr)

    if failed:
        raise ValueError('One or more Soda Core scans failed')

    return 0