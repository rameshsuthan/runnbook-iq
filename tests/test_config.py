from decimal import Decimal
import pytest


def test_settings_enforce_budget_and_baseline():
    from runbook_iq.config import Settings
    s = Settings()
    assert s.budget_usd == Decimal('3') and s.top_k == 5
    assert not s.paid_fallback and s.retries == 0
    assert Settings(hybrid=True).hybrid
    assert Settings(reranking=True).reranking
    for feature in ('multi_query', 'repair'):
        with pytest.raises(ValueError, match='Phase 2'):
            Settings(**{feature: True})


def test_credential_conflict_never_echoes_values(monkeypatch):
    from runbook_iq.config import credentials
    monkeypatch.setenv('GOOGLE_API_KEY', 'private-one')
    monkeypatch.setenv('GEMINI_API_KEY', 'private-two')
    with pytest.raises(ValueError) as error:
        credentials('gemini')
    assert 'private' not in str(error.value)


def test_missing_credentials_report_names_only():
    from runbook_iq.config import credentials
    with pytest.raises(ValueError, match='GEMINI_API_KEY'):
        credentials('gemini')


def test_offline_doctor_never_requires_network(capsys):
    from runbook_iq.cli import main
    assert main(['doctor', '--offline']) == 0
    assert 'missing' in capsys.readouterr().out
