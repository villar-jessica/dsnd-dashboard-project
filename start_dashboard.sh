#!/bin/bash
set -e
echo "=== Starting DSND Employee Dashboard ==="
echo "Python: $(python3 --version)"
echo "Working dir: $(pwd)"
echo "PORT: ${PORT:-8080}"

# Change to report directory
cd "$(dirname "$0")/report"
echo "Changed to: $(pwd)"

# Add paths
export PYTHONPATH="$(dirname "$0")/python-package:$(pwd):${PYTHONPATH:-}"

# Run the dashboard
exec python3 -c "
import os, sys, warnings
warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg')
import uvicorn
from dashboard import app
port = int(os.environ.get('PORT', 8080))
print(f'Listening on 0.0.0.0:{port}', flush=True)
uvicorn.run(app, host='0.0.0.0', port=port, reload=False)
"
