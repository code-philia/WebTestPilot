### Overview
This document outlines main functionality of fixtures.

The idea of fixture in GUI testing is to have many testcases starting from the same, reusable point with the same "setupFunction".

### Implementation details:
- Storage: simply save at .webtestpilot/.fixtures, each fixture has its own .json. record.
- Nestability: a fixture can use another fixture as its own fixture.
- UI: add a tab to view&edit test cases and another tab for fixtures.
- Usage:
  - From test-case editing: when editing a testcase, user can choose the fixture to use for that testcase (or no fixture).
  - From fixture editing: from the fixture editing page, it should allow user to add steps to the fixture, and configure fixture on top of fixtures.

### Analysis & Visualization:
This is to visualize the topologies and dependencies of test cases and fixtures and among fixtures themselves. This visualization/analysis tab is used for user to see the overview of all testcases in a graph.