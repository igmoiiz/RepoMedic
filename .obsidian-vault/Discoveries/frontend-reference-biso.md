---
date: 2026-10-18
tags:
  - discovery
  - repomedic
  - frontend
category: pattern
---

# Discovery: BISO Frontend Reference

## What was found

User provided a screenshot of BISO (Bug Immune System) — a dark-themed, feature-rich debugging dashboard. Key design patterns to replicate for RepoMedic:

### Layout
- Left sidebar with icon + label navigation
- Top bar with system name, environment tag, live indicator, system status
- Main content area with multiple panels

### Navigation modules
- Overview, Oracle, Bugs, Fix loops, Fuzzer, Dreamer
- Cartographer (causal graph), Historian, Learner
- Quarantine, Extinction, Economist
- Pathogen Registry, Metrics, Audit log, Settings

### Cartographer panel (primary view)
- Stats panel: Files count, Edges count, Shown count
- Hot Files panel: Ranked by indegree (load-bearing files) with icons and counts
- Causal graph: Force-directed graph with color-coded nodes
- Blast a Diff panel: Paste a diff to see which files would break
- Nothing Selected panel: Instructions to click nodes

### Visual style
- Dark background (#0a0e1a or similar dark navy)
- Teal/green accent color (#4fd1c5 or similar)
- Monospace/code-style fonts for data
- Subtle borders and panel separation
- Clean typography with good hierarchy

## Context

User wants this level of frontend polish for RepoMedic. The frontend should be a React + TypeScript + Vite app with Tailwind CSS.

## Impact

High — this sets the design standard for the entire RepoMedic UI.

## Recommendation

Build the frontend with:
- React + TypeScript + Vite + Tailwind CSS
- Force-directed graph visualization (d3-force or similar)
- Dark theme with teal accents
- Sidebar navigation with all investigation modules
- Real-time event streaming via SSE or polling
