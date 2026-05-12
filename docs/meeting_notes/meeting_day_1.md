# Meeting Day 1

## Main decisions

- Test both Mininet and container-based simulation.
- Mininet may be useful for network simulation and SDN, but is not mandatory.
- Docker can be tested, but resource usage must be considered.
- Traffic generation can be done with Scapy loops over an IP address range.
- A traffic monitor must be developed.
- The project must include three modules:
  - detection
  - characterization
  - mitigation
- Expected outputs include curves, ML model results, detection performance, precision metrics and model parameters.
- The GitHub repository must be shared with the supervisors.
- The repository must be protected before publishing documents.

## Important technical point

The system should detect abnormal traffic toward inactive or normally unused machines. If an inactive address receives traffic, it may be considered suspicious.

## Next step

Build a small simulation environment and generate controlled traffic.
