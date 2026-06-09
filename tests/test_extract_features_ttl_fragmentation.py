from scapy.all import IP, UDP, Raw, fragment, wrpcap

from carpet_bombing.characterization.extract_features import extract_pcap_features


def test_extracts_ttl_and_fragmentation_features(tmp_path):
    normal_packet = IP(src="192.0.2.10", dst="10.0.0.1", ttl=64) / UDP(
        sport=12000,
        dport=53,
    )
    fragmented_packet = IP(src="192.0.2.20", dst="10.0.0.2", ttl=42) / UDP(
        sport=13000,
        dport=123,
    ) / Raw(b"A" * 1200)

    pcap_path = tmp_path / "carpet_fragmented.pcap"
    wrpcap(str(pcap_path), [normal_packet, *fragment(fragmented_packet, fragsize=300)])

    rows = extract_pcap_features(
        pcap_file=pcap_path,
        window_size=1.0,
        label="carpet_mixed",
        inactive_ips=set(),
        attack_config=None,
    )

    normal_row = next(row for row in rows if row["src_ip"] == "192.0.2.10")
    fragment_rows = [row for row in rows if row["src_ip"] == "192.0.2.20"]

    assert normal_row["ttl_min"] == 64
    assert normal_row["ttl_max"] == 64
    assert normal_row["ttl_mean"] == 64
    assert normal_row["unique_ttl_count"] == 1
    assert normal_row["fragmented_packet_count"] == 0
    assert normal_row["fragment_ratio"] == 0

    assert sum(row["fragmented_packet_count"] for row in fragment_rows) > 0
    assert sum(row["first_fragment_count"] for row in fragment_rows) == 1
    assert sum(row["non_initial_fragment_count"] for row in fragment_rows) > 0
    assert {row["ttl_min"] for row in fragment_rows} == {42}
    assert {row["protocol"] for row in fragment_rows} == {"UDP"}
