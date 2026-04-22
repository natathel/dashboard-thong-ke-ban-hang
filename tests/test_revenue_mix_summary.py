from services.metrics import revenue_mix_summary


def test_revenue_mix_summary_has_positive_segments():
    summary = revenue_mix_summary()
    assert set(summary) == {'online', 'retail', 'enterprise'}
    assert sum(summary.values()) > 0
