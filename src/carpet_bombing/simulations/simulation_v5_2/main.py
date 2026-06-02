import sys
from pathlib import Path

from mininet.log import setLogLevel

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from carpet_bombing.simulations.simulation_v5_2.topology.paris_canada_fragmented_topology import (
    parse_args,
    run,
)


def main() -> int:
    setLogLevel("info")
    args = parse_args()
    run(
        args.auto_scenario,
        args.duration,
        args.attack_duration,
        args.warmup,
        args.pps,
        args.protocol,
        args.fragment_mode,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
