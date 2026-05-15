#!/bin/bash

for dir in */ ; do
    if [ "$dir" != "python-development/" ]; then

        cd "$dir"

        cp ../python-development/NEW_AI_KNOWLEDGE.md .
        cp ../python-development/BEST_PRACTICES.md .
        cp ../python-development/KNOWN_PATTERNS.md .

        cd ..
    fi
done

echo "Category knowledge structure created."
