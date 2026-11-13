#!/bin/bash
T="$1"
while IFS=$'\t' read -r _ path; do
    echo "path=[$path]"
    [ "$path" = "DATASETS/batch_pipeline_manifest.json" ] && break
done < "$T"
echo "Test completed"
