#!/bin/sh
set -e  # Exit immediately if any command fails

if [ "$ENVIRONMENT" = "production" ]; then
    pnpm build
    exec pnpm exec wrangler dev --ip 0.0.0.0 --port 3000
else
    exec pnpm dev --host 0.0.0.0
fi