#!/bin/bash
cd /Users/bprzybysz/nc-src/ctx-eng-plus/syntropy-mcp
npm run build
npm test 2>&1 | tail -20
