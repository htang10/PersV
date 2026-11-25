#!/bin/sh
set -e  # Exit immediately if any command fails

if [ "$ENVIRONMENT" = "staging" ]; then
    pnpm build --mode staging
    exec pnpm exec wrangler dev --ip 0.0.0.0 # port 8787
else
    exec pnpm dev --host 0.0.0.0 # port 5173
fi